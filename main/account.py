# ? Built-in
import os
import sys
import json
import struct
import numpy as np
from typing import Any
from pprint import pprint
from hashlib import sha256
from base64 import b64encode, b64decode
from binascii import hexlify, unhexlify
from dataclasses import dataclass, field, asdict

# ? Third Party
from nptyping import NDArray, Int, Shape, Structure

# ? Local
from keypair import KeyPair
from signature import Signature
from operation import Operation
from transaction import Transaction

# Class Initialization
KEYS = KeyPair()
SIGNER: "Signature" = Signature()
OP: "Operation" = Operation()
TX: "Transaction" = Transaction()

# Random Integer 4bytes
RANDNONCE: int = int.from_bytes


@dataclass(repr=False)
class Account:
    """
    :test_coins:
        an integer representing test coins

    :account_id:
        an unique value for identifying an account within the system.
        It can often be a public key or its hash value.

    :wallet:
        an array that stores KeyPair objects that belong to the same account.

    :properties:
        a dictonary containing properties own by the accountt

    :tx_history:
        a numpy array value representing unspent and spent transaction outputs.

    """

    _account_id: bytes = b""

    wallet: NDArray[
        Shape["1,0"],
        Structure["PrivateKey: Object, PublicKey: Object, Modulus: Object"],
    ] = field(default_factory=lambda: np.empty([1, 0], dtype="O"))

    _properties: dict = field(default_factory=lambda: dict())
    _tx_history: NDArray[
        Shape["2,2"], Structure["UTXO: Object, STXO: Object"]
    ] | None = None

    @property
    def get_account_id(self) -> bytes:
        """Returns account's id"""
        return self._account_id

    @classmethod
    def __create_account(cls, id, wall, property, tx_history) -> "Account":
        """Return a new object of Account"""
        return cls(id, wall, property, tx_history)

    def gen_account(self) -> "Account":
        """
        a function that allows you to create an account.
                The first key pair is generated and assigned to the account.

        :returns:
             an object of the Account class.
        """
        # Get KeyPair
        kPrv, kPub = KEYS.gen_key_pair().values()
        acc_id = sha256(str(kPub).encode("ascii")).hexdigest()

        data_struct = np.dtype(
            [("PrivateKey", "O"), ("PublicKey", "O"), ("Modulus", "O")]
        )
        wallet = np.array([(kPrv[0], kPub[1], kPub[0])], dtype=data_struct)
        return self.__create_account(acc_id, wallet, self.get_properties, self._tx_history)

    def add_key_pair_to_wallet(self, keypair: KeyPair) -> None:
        """
        a function that allows you to add a new key pair to the wallet and use it in the future to sign operations
        initiated from this account.

        :keypair:
            object of KeyPair class

        :return:
            None.
        """
        # Generates New keypair from private key
        kPrv, kPub = keypair.gen_key_pair(self.wallet["PrivateKey"][0]).values()
        data_struct = np.dtype(
            [("PrivateKey", "O"), ("PublicKey", "O"), ("Modulus", "O")]
        )
        #  Updates account id with the new publickey
        self._account_id = sha256(str(kPub).encode("ascii")).hexdigest()

        temp = np.array([(kPrv[0], kPub[1], kPub[0])], dtype=data_struct)
        self.wallet = np.append(self.wallet, temp)  # Add new keys to the wallet

    def create_payment_op(
        self, recipient: "Account", asset: int | float | str | bytes, index: int
    ) -> Transaction:
        """
        a function that allows to create a payment operation on behalf of this account to the recipient.

        :recipient:
            Account object as input to which the payment will be made.

        :asset:
            could be amount to transfer or property to transfer

        :index:
            index of key for signing data

        :return:
            Trasaction object.
        """
        sig: bytes = b""  # Sign asset
        if isinstance(asset, int):
            sig = self.sign_data(
                asset.to_bytes(asset.bit_length(), "little"), index
            )  # signs integer: coins

        elif isinstance(asset, float):
            sig = self.sign_data(struct.pack("f", asset), index)  # signs float: coins

        elif isinstance(asset, bytes) or isinstance(asset, str):
            try:
                sig = self.sign_data(
                    asset.encode("ascii"), index
                )  # signs string: property's id
            except AttributeError:
                sig = self.sign_data(asset, index)  # signs bytes: property's id

        # Create Operation from Operation Class
        operation = OP.create_operation(self, recipient, asset, sig)

        # Verify Operation
        if operation.verify_operation(index):
            op: list[Operation] = operation.get_operation_list
            transaction = TX.create_operation(
                op, RANDNONCE(os.urandom(4), sys.byteorder)
            )  # If operation is genuine create transaction

            # Update both sender and receiver's transaction history
            self._update_tx_history(transaction)
            recipient._update_tx_history(transaction)
            return transaction

        raise BaseException(
            f"Transfer of {asset} to {recipient.get_account_id} from {self.get_account_id} failed!!"
        )

    @property
    def get_balance(self) -> int | float:
        """
        a function that allows to get the state of the user's balance.

        :return:
            integer
        """
        unspent: int = self.__compute_utxos_stxos("UTXO")
        spent: int = self.__compute_utxos_stxos("STXO")
        if unspent > spent:
            return unspent - spent
        return 0

    @get_balance.getter
    def print_balance(self) -> None:
        """
        a function that allows to display the state of the user's balance.

        :return:
            None
        """
        print(f"Account balance: {self.get_balance}")

    def create_property(self, deed_no: bytes, appro_area: bytes, worth: int) -> None:
        """
        a function creates a new property.

        :deed_no:
            a deed number that will be turned into a digital deed. It designates ownership of a property

        :appro_area:
            approximate area of the property/land

        :worth:
            cost of the property

        :owner:
            account_id of the current owner
        """
        property_: dict[bytes, dict[str, bytes]] = {
            hexlify(b64encode(deed_no)).decode("ascii"): {
                "appro_area": hexlify(b64encode(appro_area)).decode("ascii"),
                "worth": hexlify(b64encode(worth)).decode("ascii"),
                "owner": self.get_account_id,
            }
        }

        self.update_properties = property_  # Update Properties
        # Statically create a transaction for the new property
        operation = [
            {
                "asset": hexlify(b64encode(deed_no)).decode("ascii"),
                "receiver": self.get_account_id,
                "sender": None,
                "sig": None,
            }
        ]

        tx: Transaction = TX.create_operation(
            operation, RANDNONCE(os.urandom(4), sys.byteorder)
        )
        # self._update_tx_history(tx)

    def payment_op_for_property(
        self, prop_id: str, buyer: "Account", amount: int | float | float, index: int
    ) -> Transaction:
        """
        a function that allows to create a payment operation on behalf of this account to the recipient.

        :prop_id:
            a digital deed that uniquely identifies a property.

        :buyer:
            account object as input to which the property ownership will be transfered.

        :amount:
            property's worth.

        :index:
            index of key for signing data

        :return:
            trasaction object.
        """
        # Create operation for and seller
        sig: bytes = self.sign_data(prop_id.encode("ascii"), index)
        seller_op: Operation = OP.create_operation(self, buyer, prop_id, sig)

        if seller_op.verify_operation(index, True):  # verify property of interest exist
            # Initiate coin payment operation
            buyer.create_payment_op(self, amount, index)
            # if payment operation was a success remove and update seller properties
            temp = {prop_id: self.get_properties.pop(prop_id)}
            # change property owner
            temp[prop_id]["owner"] = buyer.get_account_id
            # Update buyer's properties
            buyer.update_properties = temp

            transaction: Transaction = TX.create_operation(
                seller_op.get_operation_list, RANDNONCE(os.urandom(4), sys.byteorder)
            )
            # self.__update_transaction_history(transaction)
            # buyer.__update_transaction_history(transaction)
            return transaction

        raise BaseException(
            f"Transfer of {prop_id} to {buyer.get_account_id} from {self.get_account_id} failed!!"
        )

    @property
    def get_properties(self):
        """
        a function that allows to get the state of the user's balance.

        :return:
            None
        """
        return self._properties

    @get_properties.setter
    def update_properties(self, property_: dict[bytes, dict[str, bytes]]) -> None:
        """
        a function that allows to update the state of the user's properties.

        :property_:
            A dictionary consisting of information of a new property.

        :return:
            None
        """
        if self._properties is None:
            self._properties = property_
        else:
            self._properties.update(property_)

    @get_properties.getter
    def print_properties(self) -> None:
        """
        a function that allows to display the state of the user's propertys.

        :return:
            None
        """
        if self.get_properties is not None:
            print(self.get_properties)
        else:
            raise ValueError("You have no propertiess available.")

    def sign_data(self, msg: bytes, index: int = 1) -> bytes:
        """
        a function that allows the user to sign random data.

        :msg:
            It accepts a message

        :index:
            an index of the key pair in the wallet as input.
            default = 1(KeyPair generated to signing data)

        :return:
            bytes -> The value of the signature
        """
        d, n = self.wallet["PrivateKey"][index], self.wallet["Modulus"][index]
        signed_data = SIGNER.sign_data((d, n), msg)
        return signed_data

    @property
    def get_history(self):
        """function return an array of history or transaction"""
        return self._tx_history

    def __compute_utxos_stxos(self, coin: str) -> int:
        """function calculate and returns available coin that can spent"""

        tx: int = 0
        if coin == "UTXO":  # Calculate Unspent
            unspent: list = list(self.get_history["UTXO"])

            for u in range(len(unspent)):
                if unspent[u] is not None:
                    temp = unspent[u][0]["operation"][0]["asset"]
                    if not isinstance(temp, str):
                        tx += temp

        elif coin == "STXO":  # Calculate Spent
            spent: list = list(self.get_history["STXO"])

            for s in range(len(spent)):
                if spent[s] is not None:
                    temp = spent[s][0]["operation"][0]["asset"]
                    if not isinstance(temp, str):
                        tx += temp
        else:
            raise BaseException(f"Invalid coin {coin}!")
        return tx

    def _update_tx_history(self, tx: Transaction):
        """Function keeps record of transactions for account"""

        data_struct = np.dtype([("UTXO", "O"), ("STXO", "O")])
        temp_tx = None

        if tx.get_trasaction_list[0]["operation"][0]["sender"] == self.get_account_id:
            temp_tx = np.array([(None, tx.get_trasaction_list)], dtype=data_struct)

        if tx.get_trasaction_list[0]["operation"][0]["receiver"] == self.get_account_id:
            temp_tx = np.array([(tx.get_trasaction_list, None)], dtype=data_struct)

        if self._tx_history is not None:
            self._tx_history = np.append(self._tx_history, temp_tx)
        else:
            self._tx_history = temp_tx
        # print(self._tx_history)

    def print_tx_history(self, tx: str | None = None) -> None:
        """
        function prints transaction history

        :tx:
            transaction type.
            To print:
                pass "UTXO" for Unspent Transaction Outputs
                    or
                "STXO" for Spent Transaction Outputs
        """
        if tx == "UTXO":
            temp = list(self.get_history["UTXO"])
            print(f"UTXO: {json.dumps(temp, indent=2)}", end="\n")
        elif tx == "STXO":
            temp = list(self.get_history["STXO"])
            print(f"STXO: {json.dumps(temp, indent=2)}", end="\n")
        else:
            temp = list(self.get_history["UTXO"])
            temp2 = list(self.get_history["STXO"])
            print(f"UTXO: {json.dumps(temp, indent=2)}", end="\n")
            print(f"STXO: {json.dumps(temp2, indent=2)}", end="\n")


    def to_string(self) -> str:
        """
        a function that allows to form a string with an account object.

        :return:
            an object of the String class.
        """
        return f"account_id: {self.get_account_id!r}\nproperties: {self._properties!r}\nbalance: {self.get_balance!r}"

    def print(self) -> None:
        """
        a function for output key pair objects.

        :return:
            None
        """
        pprint(self.wallet)

class SpecialAccount(Account):
    """
    :test_coins:
        an integer representing test coins

    :account_id:
        an unique value for identifying an account within the system.
        It can often be a public key or its hash value.

    :wallet:
        an array that stores KeyPair objects that belong to the same account.

    :properties:
        a dictonary containing properties own by the accountt

    :tx_history:
        a numpy array value representing unspent and spent transaction outputs.

    """

    def __init__(
        self,
        _account_id: bytes = b"",
        wallet: NDArray[
            Shape["1,0"],
            Structure["PrivateKey: Object, PublicKey: Object, Modulus: Object"],
        ] = np.empty([1, 0], dtype="O"),
        _properties: dict = dict(),
        _tx_history: NDArray[Shape["2,2"], Structure["UTXO: Object, STXO: Object"]]
        | None = None,
        test_coins: int = 0,
    ) -> None:
    
        super().__init__(_account_id, wallet, _properties, _tx_history)
        self.test_coins = test_coins


    def gen_account(self) -> "Account":
        obj = super().gen_account()
        """Sets first UTXO: Statically for test purposes"""
        temp_utxo = [
            {
                "sender": None,
                "receiver": obj.get_account_id,  
                "asset": self.test_coins,
                "sig": None,
            }
        ]
        tx = TX.create_operation(temp_utxo, RANDNONCE(os.urandom(4), sys.byteorder))
        obj._update_tx_history(tx)
        obj.test_coins = self.test_coins
        return obj

# ? Built-in
import os
import sys
import json
import numpy as np
from typing import Any
from binascii import hexlify, unhexlify
from base64 import b64encode, b64decode
from hashlib import sha256, sha512
from pprint import pprint
from dataclasses import dataclass, field, asdict

# ? Third Party
from nptyping import NDArray, Int, Shape, Structure

# ? Local
from keypair import KeyPair
from signature import Signature
from operation import Operation
from transaction import Transaction

# ? Class Initialization
KEYS = KeyPair()
SIGNER: "Signature" = Signature()
OP: "Operation" = Operation()
TX: "Transaction" = Transaction()

# ? Random Integer 4bytes
RANDNONCE: int = int.from_bytes(os.urandom(4), sys.byteorder)


@dataclass(repr=False)
class Account:
    """
    :account_id:
        an unique value for identifying an account within the system.
        It can often be a public key or its hash value.

    wallet:
        an array that stores KeyPair objects that belong to the same account.

    balance:
        an integer value representing the number of coins belongs to the account.

    """

    __account_id: bytes = b""
    wallet: NDArray[
        Shape["1,0"],
        Structure["PrivateKey: Object, PublicKey: Object, Modulus: Object"],
    ] | None = None
    __properties: NDArray[
        Shape["1,0"],
        Structure[
            "digital_deed: Object, appro_area: Object, worth: Object, owner: Object"
        ],
    ] | None = None
    __tx_history: NDArray[
        Shape["2,2"], Structure["UTXO: Object, STXO: Object"]
    ] | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Sets first UTXO: Statically for test purposes"""

        temp_utxo = [
            {
                "sender": None,
                "receiver": self.get_account_id,  # id from firstly generated keys
                "amount": 50000.00,
                "sig": None,
            }
        ]
        tx = TX.create_operation(temp_utxo, RANDNONCE)
        self.__update_tx_history(tx)

    @property
    def get_account_id(self) -> bytes:
        """Returns account's id"""
        return self.__account_id

    @classmethod
    def __create_account(cls, id, wall) -> "Account":
        """Return a new object of Account"""
        return cls(id, wall)

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
        return self.__create_account(acc_id, wallet)

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
        self.__account_id = sha256(str(kPub).encode("ascii")).hexdigest()

        temp = np.array([(kPrv[0], kPub[1], kPub[0])], dtype=data_struct)
        self.wallet = np.append(self.wallet, temp)  # Add new keys to the wallet

    def create_payment_op(self, recipient: "Account", amount: int, index: int) -> None:
        """
        a function that allows to create a payment operation on behalf of this account to the recipient.

        :recipient:
            Account object as input to which the payment will be made.
        :amount:
            the transfer amount.

        :return:
            Trasaction object.
        """
        # Create Operation from Operation Class
        operation = OP.create_operation(self, recipient, amount)

        # Verify Operation
        if operation.verify_operation(index):
            op: list[Operation] = operation.get_operation_list
            transaction = TX.create_operation(
                op, RANDNONCE
            )  # If operation is genuine create transaction

            # Update both sender and receiver's transaction history
            self.__update_tx_history(transaction)
            recipient.__update_tx_history(transaction)

        else:
            raise BaseException(
                f"Payment of {amount} to {recipient.get_account_id} from {self.get_account_id} failed!!"
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

    def __compute_utxos_stxos(self, coin: str) -> int:
        """function calculate and returns available coin that can spent"""

        tx: int = 0
        if coin == "UTXO":  # Calculate Unspent
            unspent: list = list(self.get_history["UTXO"])

            for u in range(len(unspent)):
                if unspent[u] is not None:
                    tx += unspent[u][0]["operation"][0]["amount"]

        elif coin == "STXO":  # Calculate Spent
            spent: list = list(self.get_history["STXO"])

            for s in range(len(spent)):
                if spent[s] is not None:
                    tx += spent[s][0]["operation"][0]["amount"]
        else:
            raise BaseException(f"Invalid coin {coin}!")
        return tx

    @get_balance.getter
    def print_balance(self) -> None:
        """
        a function that allows to display the state of the user's balance.

        :return:
            None
        """
        print(f"Account balance: {self.get_balance}")

    def payment_op_for_property(
        self, prop_id: bytes, buyer: "Account", amount: int | float
    ) -> None:
        """
        a function that allows to create a payment operation on behalf of this account to the recipient.

        :prop_id:
            a digital deed that uniquely identifies a property.

        :buyer:
            Account object as input to which the property ownership will be transfered.

        :amount:
            the transfer amount which must be equal to property's worth.

        :return:
            Trasaction object.
        """
        # Create operation for and seller
        seller_op: Operation = OP.create_operation(self, buyer, prop_id)

        if seller_op.verify_operation(prop=True): # verify property of interest
            # Initiate coin transaction
            self.create_payment_op(buyer, self, amount)
            # Update buyer's properties
            buyer.update_properties
            # Update seller's properties
            self.update_properties

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
        data_struct = np.dtype(
            [
                ("digital_deed", "O"),
                ("appro_area", "O"),
                ("worth", "O"),
                ("owner", "O"),
            ]
        )
        temp = np.array(
            [
                (
                    hexlify(b64encode(deed_no)),
                    hexlify(b64encode(appro_area)),
                    hexlify(b64encode(worth)),
                    self.get_account_id,
                )
            ],
            dtype=data_struct,
        )

        self.update_properties = temp

    @property
    def get_properties(self):
        """
        a function that allows to get the state of the user's balance.

        :return:
            None
        """
        return self.__properties

    @get_properties.setter
    def update_properties(
        self,
        property_: NDArray[
            Shape["1,0"],
            Structure[
                "digital_deed: Object, appro_area: Object, worth: Object, owner: Object"
            ],
        ],
    ) -> None:
        """
        a function that allows to update the state of the user's properties.

        :property_:
            An Array consisting of information of a new property.

        :return:
            None
        """
        if self.get_account_id == property_["owner"][0]:

            if self.__properties is None:
                self.__properties = property_
            else:
                self.__properties = np.append(self.__properties, property_)

    @get_properties.getter
    def print_properties(self) -> None:
        """
        a function that allows to display the state of the user's propertys.

        :return:
            None
        """
        if self.get_properties is not None:
            print(
                f"Deed: {self.get_properties['digital_deed']}\nApproximate Area: {self.get_properties['appro_area']}\nWorth: {self.get_properties['worth']}\nowner: {self.get_properties['owner'][0]}"
            )
        else:
            raise ValueError("You have no propertiess available.")

    def sign_data(self, msg: bytes, idx: int = 1) -> bytes:
        """
        a function that allows the user to sign random data.

        :msg:
            It accepts a message

        idx:
            an index of the key pair in the wallet as input.
            default = 1(KeyPair generated to signing data)

        :return:
            bytes -> The value of the signature
        """
        d, n = self.wallet["PrivateKey"][idx], self.wallet["Modulus"][idx]
        signed_data = SIGNER.sign_data((d, n), msg)
        return signed_data

    @property
    def get_history(self):
        """function return an array of history or transaction"""
        return self.__tx_history

    def __update_tx_history(self, tx: Transaction):
        """Function keeps record of transactions for account"""

        data_struct = np.dtype([("UTXO", "O"), ("STXO", "O")])
        temp_tx = None

        if tx.get_trasaction_list[0]["operation"][0]["sender"] == self.get_account_id:
            temp_tx = np.array([(None, tx.get_trasaction_list)], dtype=data_struct)

        if tx.get_trasaction_list[0]["operation"][0]["receiver"] == self.get_account_id:
            temp_tx = np.array([(tx.get_trasaction_list, None)], dtype=data_struct)

        if self.__tx_history is not None:
            self.__tx_history = np.append(self.__tx_history, temp_tx)
        else:
            self.__tx_history = temp_tx

    def print_tx_history(self, tx: str | None = None) -> None:
        """
        function print transaction history

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
        return f"account_id: {self.get_account_id!r}\nproperties: {self.__properties!r}\nbalance: {self.get_balance!r}"

    def print(self) -> None:
        """
        a function for output key pair objects.

        :return:
            None
        """
        pprint(self.wallet)


if __name__ == "__main__":
    account1 = Account()
    sender = account1.gen_account()
    sender.add_key_pair_to_wallet(KeyPair())
    # print(sender.get_account_id)

    #! https://upload.wikimedia.org/wikipedia/commons/8/80/Example_of_a_blank_Kenyan_Deed_Title.png
    sender.create_property(b"KAJIADO/LOODARIAK/579", b"104.0 hectares", b"1000000")
    sender.create_property(b"KAJIADO/LOODARIAK/579", b"80.0 hectares", b"1000000")
    # # print(sender.to_string())
    # sender.to_string()
    # sender.print()
    # sender.print_propertiess
    # print(sender.wallet)

    account2 = Account()
    receiver = account2.gen_account()
    receiver.add_key_pair_to_wallet(KeyPair())
    # receiver.add_key_pair_to_wallet(KeyPair())
    # sender.create_payment_op(receiver, 9000, 1)
    # sender.create_payment_op(receiver, 40.99, 1)
    # sender.create_payment_op(receiver, 20, 1)
    # sender.create_payment_op(receiver, 60, 1)
    # receiver.create_payment_op(sender, 10, 1)
    # receiver.create_payment_op(sender, 5, 1)
    # print(sender.get_balance)
    # sender.print_tx_history("UTXO")
    # sender.print_tx_history("STXO")
    # sender.print_tx_history()
    # print()
    # receiver.print_tx_history("UTXO")
    # receiver.print_tx_history("STXO")
    # receiver.print_tx_history()
    # sender.compute_balance()
    # receiver.compute_balance()
    # print(sender.get_account_id)
    # print(receiver.get_account_id)
    # print(sender.get_history)
    # print(sender.get_account_id)
    # print(sender.get_balance)
    # print(receiver.get_balance)
    # print(sender.get_properties)
    sender.print_properties
    cost = int(b64decode(unhexlify(b"4d5441774d4441774d413d3d")))

    sender.payment_op_for_property(
        b"5330464b535546455479394d5430394551564a4a515573764e546335",
        receiver,
        cost
    )

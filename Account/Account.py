import sys
import numpy as np
from base64 import b64encode, b16decode
from hashlib import sha256, sha512
from pprint import pprint
from dataclasses import dataclass, field, asdict

from nptyping import NDArray, Int, Shape, Structure

sys.path.append("../")
from Operation import Operation
from RSA.KeyPair import KeyPair
from RSA.Signature import Signature

# ? Digital Signature Class
SIGNER = Signature()


@dataclass
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

    account_id: str = b""
    wallet: NDArray[
        Shape["1,0"],
        Structure["PrivateKey: Object, PublicKey: Object, n_value: Object"],
    ] | None = None
    __balance: int = 0
    __assets: NDArray[
        Shape["1,0"],
        Structure[
            "digital_deed: Object, appro_area: Object, worth: Object, owner: Object"
        ],
    ] | None = None

    @classmethod
    def __create_account(cls, id, wall, balance) -> "Account":
        """Return a new instance of Account"""
        return cls(id, wall, balance)

    def gen_account(self) -> "Account":
        """
        a function that allows you to create an account. It returns an object of the Account class.
        The first key pair is generated and assigned to the account.
        """
        # Get KeyPair
        keys = KeyPair()
        kPrv, kPub = keys.gen_key_pair().values()
        acc_id = (
            sha256(kPub[0].to_bytes(kPub[0].bit_length(), sys.byteorder))
            .hexdigest()
            .encode("ascii")
        )

        data_struct = np.dtype(
            [("PrivateKey", "O"), ("PublicKey", "O"), ("n_value", "O")]
        )
        wallet = np.array([(kPrv[0], kPub[1], kPub[0])], dtype=data_struct)
        return self.__create_account(acc_id, wallet, 0)

    def add_key_pair_to_wallet(self, keypair: KeyPair) -> None:
        """
        a function that allows you to add a new key pair to the wallet and use it in the future to sign operations
        initiated from this account. It does not return anything.
        """
        kPrv, kPub = keypair.gen_key_pair(
            self.wallet["PrivateKey"][0]
        ).values()  #! Generates New keypair from private key
        data_struct = np.dtype(
            [("PrivateKey", "O"), ("PublicKey", "O"), ("n_value", "O")]
        )

        temp = np.array([(kPrv[0], kPub[1], kPub[0])], dtype=data_struct)
        self.wallet = np.append(self.wallet, temp)

    def create_payment_op(
        self, recipient: "Account", amount: int, index: int
    ) -> Operation:
        """
        a function that allows to create a payment operation on behalf of this account to the recipient.

        :recipient: Account object as input to which the payment will be made.
        :amount: the transfer amount.
        :index: key index in the wallet.
        """
        # TODO: Needs Operation Class.
        ...

    @property
    def get_balance(self) -> int:
        """
        a function that allows to get the state of the user's balance.

        :return: integer
        """
        return self.__balance

    @get_balance.setter
    def update_balance(self, value: int) -> None:
        """
        a function that allows to update the state of the user's balance.

        :value: an integer input.
        :return: None
        """
        # TODO: Needs Transaction Class.
        ...

    @get_balance.getter
    def print_balance(self) -> None:
        """
        a function that allows to display the state of the user's balance.

        :return: None
        """
        print(f"Account balance: {self.__balance}")

    def create_assets(self, deed_no: bytes, appro_area: bytes, worth: int) -> None:
        """
        a function creates a new assets.

        :deed_no: a deed number that will be turned into a digital deed. It designates ownership of a property
        :appro_area: approximate area of the property/land
        :worth: cost of the property
        :owner: account_id of the current owner
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
                    b64encode(deed_no).hex(),
                    b64encode(appro_area).hex(),
                    b64encode(worth).hex(),
                    self.account_id,
                )
            ],
            dtype=data_struct,
        )
        
        if self.__assets is not None:
            self.update_assets = temp
        self.__assets = temp

    @property
    def get_assets(self):
        """
        a function that allows to get the state of the user's balance.

        :return: None
        """
        return self.__assets

    @get_assets.setter
    def update_assets(
        self,
        asset: NDArray[
            Shape["1,0"],
            Structure[
                "digital_deed: Object, appro_area: Object, worth: Object, owner: Object"
            ],
        ],
    ) -> None:
        """
        a function that allows to update the state of the user's assets.

        :asset: An Array consisting of information of a property.
        :return: None
        """
        if self.account_id == asset["owner"][0]:
            if self.__assets is None:
                self.__assets = asset
            else:
                self.__assets = np.append(self.__assets, asset)

    @get_assets.getter
    def print_assets(self) -> None:
        """
        a function that allows to display the state of the user's assets.

        :return: None
        """
        if self.get_assets is not None:
            print(
                f"""
            Deed: {self.get_assets['digital_deed']}
            Approximate Area: {self.get_assets['appro_area']}
            Worth: {self.get_assets['worth']}
            owner: {self.get_assets['owner'][0]}
            """
            )
        else:
            raise ValueError("You have no assets available.")

    def sign_data(self, msg: bytes, idx: int) -> bytes:
        """
        a function that allows the user to sign random data. It accepts a message and an index of the key pair in the
        wallet as input.

        :return: bytes -> The value of the signature
        """
        d, n = self.wallet["PrivateKey"][idx], self.wallet["n_value"][idx]
        signed_data = SIGNER.sign_data((d, n), msg)
        return signed_data

    def to_string(self) -> str:
        """
        a function that allows to form a string with an account object.

        :return: an object of the String class.
        """
        return f"""
        account_id: {self.account_id!r}\n
        assets: {self.assets!r}\n
        balance: {self.__balance!r}\n
        wallet: {self.wallet!r}
        """

    def print(self) -> None:
        """
        a function for output key pair objects.

        :return: None
        """
        pprint(self.wallet)


if __name__ == "__main__":
    account = Account()
    acc = account.gen_account()
    acc.add_key_pair_to_wallet(KeyPair())
    randata: bytes = b"some random data to be signed."

    #! https://upload.wikimedia.org/wikipedia/commons/8/80/Example_of_a_blank_Kenyan_Deed_Title.png
    acc.create_assets(b"KAJIADO/LOODARIAK/579", b"104.0 hectares", b"1000000")
    acc.create_assets(b"KAJIADO/LOODARIAK/579", b"80.0 hectares", b"1000000")
    # acc.sign_data(randata, 1)
    # print(acc.to_string())
    # acc.to_string()
    # acc.print()
    acc.print_assets

import sys
import numpy as np
from hashlib import sha256
from pprint import pprint
from dataclasses import dataclass, field, asdict

from nptyping import NDArray, Int, Shape, Structure

sys.path.append("../")
from Operation import Operation
from RSA.KeyPair import KeyPair
from RSA.Signature import Signature


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

    account_id: bytes = b""
    wallet: NDArray[
        Shape["1,0"], Structure["kPrv: Object, kPub: Object, n_value: Object"]
    ] | None = None
    balance: int = 0

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
        acc_id = sha256(kPub[0].to_bytes(kPub[0].bit_length(), sys.byteorder)).digest()

        struct = np.dtype([("PrivateKey", "O"), ("PublicKey", "O"), ("n_value", "O")])
        wallet = np.array([(kPrv[0], kPub[1], kPub[0])], dtype=struct)
        return self.__create_account(acc_id, wallet, self.balance)

    def add_key_pair_to_wallet(self) -> None:
        """
        a function that allows you to add a new key pair to the wallet and use it in the future to sign operations
        initiated from this account. It does not return anything.
        """
        ...

    def update_balance(self, value: int) -> None:
        """
        a function that allows to update the state of the user's balance. It takes an integer value as input, and does
        not return anything.
        """
        ...

    def create_payment_op(
        self, recipient: "Account", amount: int, index: int
    ) -> Operation:
        """
        a function that allows to create a payment operation on behalf of this account to the recipient. Accepts the
        account object as input to which the payment will be made, the transfer amount and the key index in the wallet.
        """
        ...

    def get_balance(self) -> int:
        """
        a function that allows to get the state of the user's balance. It returns an integer value.
        """
        ...

    def print_balance(self) -> None:
        """
        a function that allows to display the state of the user's balance. It does not return anything.
        """
        ...

    def sign_data(self, msg: bytes, idx: int) -> bytes:
        """
        a function that allows the user to sign random data. It accepts a message and an index of the key pair in the
        wallet as input. Returns the value of the signature
        """
        ...

    def to_string(self) -> str:
        """
        a function that allows to form a string with an account object. Returns an object of the String class.
        """
        ...

    def print(self, acc: "Account") -> None:
        """
        a function for output key pair objects. It does not return anything.
        """
        pprint(asdict(acc))


if __name__ == "__main__":
    account = Account()
    acc = account.gen_account()
    # acc2 = account.gen_account()
    # acc3 = account.gen_account()
    # print(acc == acc2 == acc3)
    acc.print(acc)

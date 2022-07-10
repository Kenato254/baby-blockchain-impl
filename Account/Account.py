import sys
import numpy as np
from dataclasses import dataclass, field

from Operation import Operation

sys.path.append("../")
from RSA.KeyPair import KeyPair
from RSA.Signature import Signature


@dataclass(init=False)
class Account:
    """
    account_id:
        an unique value for identifying an account within the system.
        It can often be a public key or its hash value.

    wallet:
        an array that stores KeyPair objects that belong to the same account.

    balance:
        an integer value representing the number of coins belongs to the account.

    """

    account_id: bytes = b""
    wallet: list[bytes] = []
    balance: int = 0

    def gen_account(self) -> "Account":
        """
        a function that allows you to create an account. It returns an object of the Account class.
        The first key pair is generated and assigned to the account.
        """
        ...

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

    def create_payment_op(self, acc_obj: "Account", amt: int, idx: int) -> Operation:
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

    def print(self) -> None:
        """
        a function for output key pair objects. It does not return anything.
        """
        ...


if __name__ == "__main__":
    account = Account()

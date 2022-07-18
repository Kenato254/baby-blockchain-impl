import sys
from typing import TypeVar
from dataclasses import dataclass
from pprint import pprint

from account import Account
from keypair import KeyPair
from script import Script


@dataclass
class Operation:
    """
    :sender:
        payment sender's account

    :receiver:
        payment recipient's account

    :amount:
        the amount of transfer

    :signature:
        signature data generated by the sender of the payment

    :OPERATIONS:
        a stack of operations
    """

    sender: Account | None = None
    receiver: Account | None = None
    amount: int = 0
    signature: bytes = b""

    @classmethod
    def __create_operation_helper(cls, s, r, a, sig) -> "Operation":
        """Return a new object of Operation"""
        return cls(s, r, a, sig)

    def create_operation(
        self, sender: Account, recpt: Account, amt: int
    ) -> "Operation":
        """
        a function that allows to create an operation with all the necessary details and signature.

        :sndr:
            account of the sender
        :recpt:
            account of recipient
        :amt:
            amount to transfer

        :sig:
            signature of the sender

        :return:
            Operation object.
        """
        sig: bytes = sender.sign_data(amt.to_bytes(amt.bit_length(), "little"), 1)
        return self.__create_operation_helper(sender, recpt, amt, sig)

    def verify_operation(self, op: "Operation") -> bool:
        """
        a function that checks the operation. The main checks (relevant for the proposed implementation) include:

            verification of the transfer amount (that it does not exceed the sender's balance)
            signature verification (using the public key of the sender of the payment).

        :returns:
             true/false depending on the results of checking the operation.
        """
        if op.amount < op.sender.get_balance:
            op_codes: str = "{0} {1} OP_DUP OP_SHA256 OP_EQUALVERIFY OP_CHECKSIG".format(
                op.signature.hex(), op.sender.wallet["PublicKey"][1]
            )

            script: object = Script(op_codes)
            return script.eval()
        return False


    def to_string(self) -> str:
        """
        a  function that allows to form a string from the objects of the operation.

        :returns:
             an object of the String class.
        """
        return f"""
        Sender: {self.sender!r}\n
        Receiver: {self.receiver!r}\n
        Amount: {self.amount!r}\n
        Signature: {self.signature!r}
        """

    def print_operation(self) -> None:
        """
        a  function to output the objects of the operation.

        :return:
            none.
        """
        pprint(self.to_string())


if __name__ == "__main__":
    sender = Account(1000)
    receiver = Account()
    acc_sender = sender.gen_account()
    acc_sender.add_key_pair_to_wallet(KeyPair())

    acc_receiver = sender.gen_account()
    acc_receiver.add_key_pair_to_wallet(KeyPair())

    # print(acc_sender)
    # print(acc_receiver)
    # acc_sender.print()
    # acc_receiver.print()

    op = Operation()
    operation = op.create_operation(acc_sender, acc_receiver, 100)
    # print(operation, sep="\n")
    # pprint(operation.sender)
    # pprint(operation.receiver)
    # pprint(operation.amount)
    # pprint(operation.signature)
    # operation.print_operation()
    print(operation.verify_operation(operation))
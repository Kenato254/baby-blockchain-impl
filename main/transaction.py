import json
import os
from hashlib import sha256
from dataclasses import dataclass, astuple
from pprint import pprint
from typing import Optional


RANDNONCE: int = int.from_bytes(os.urandom(4), "little")


@dataclass(repr=False)
class Transaction:
    """
    :transactionID:
        a unique identifier of the transaction (a hash value from all other fields of the transaction)

    :setOfOperations:
        a set of payment operations confirmed in this transaction.

    :nonce:
        a value to protect duplicate transactions with the same operations.
    """

    transaction_id: str = ""
    set_of_operations: Optional[set] = None
    nonce: int = 0

    @classmethod
    def __create_operation_helper(cls, ops, n) -> "Transaction":
        """Return a new object of Transaction with unique id"""
        tx = cls(ops, n).eval()
        return cls(tx, ops, n)

    def create_operation(self, ops: list, nonce: int) -> "Transaction":
        """
        a function that allows to create a transaction with all the necessary details.

        :ops:
            a list of operations

        :nonce:
            integer value to protect duplicate transactions with the same operations.

        :returns:
             a Transaction object
        """
        return self.__create_operation_helper(ops, nonce)

    def eval(self) -> str:
        """Return transaction hash"""
        return sha256(
            str((self.set_of_operations, self.nonce)).encode("ascii")
        ).hexdigest()

    def to_string(self) -> str:
        """
        function that allows to form a string from transaction objects.
        Returns an object of the String class.
        """
        return json.dumps(self.get_trasaction_list, indent=2)

    def print_transaction(self) -> None:
        """
        function for output transaction objects. It does not return anything
        """
        print(self.to_string())

    @property
    def get_trasaction_list(self) -> list[dict]:
        return [
            {
                "transaction_id": self.transaction_id,
                "operation": self.set_of_operations,
                "nonce": self.nonce,
            }
        ]


if __name__ == "__main__":
    from keypair import KeyPair
    from account import Account
    from operation import Operation

    # ? User1
    sender = Account()
    acc_sender = sender.gen_account()
    acc_sender.add_key_pair_to_wallet(KeyPair())

    # ? User2
    receiver = Account()
    acc_receiver = receiver.gen_account()
    acc_receiver.add_key_pair_to_wallet(KeyPair())

    # ? Operation
    op = Operation()
    operation = op.create_operation(acc_sender, acc_receiver, 100, b"")

    if operation.verify_operation(index=1):
        sender_op = operation.get_operation_list
        temp = Transaction()

        tx = temp.create_operation(sender_op, RANDNONCE)
        # print(tx.to_string())
        # print(tx.transaction_id)
        # print(tx.get_trasaction_list)
        print("What!")
        # print(tx.transaction_id)
        # print(tx.nonce)
        # operation.print_operation()

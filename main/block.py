import json
from hashlib import sha256
from dataclasses import dataclass


@dataclass(repr=False)
class Block:
    """
    :block_id:
        an unique block identifier (the hash value from all other data).

    :prev_hash:
        an identifier of the previous block (it is needed to ensure history integrity check).

    :transaction:
        a  list of transactions confirmed in this block.
    """

    block_id: str = ""
    prev_hash: str = ""
    transactions: list | None = None

    @classmethod
    def __create_block_helper(cls, prev_hash: str, transactions: list) -> "Block":
        """Helper function returns an new object of Block"""
        block_id = cls(prev_hash, transactions).eval()
        return cls(block_id, prev_hash, transactions)

    def create_block(self, prev_hash: str, transactions: list) -> "Block":
        """
        a function that allows to create a block with all the necessary details.

        :transactions:
            a list of transactions

        :prev_hash:
            the hash of the previous block as input.

        :returns:
             a Block object.
        """
        return self.__create_block_helper(prev_hash, transactions)

    def eval(self) -> str:
        """Return hash of the block"""
        return sha256(
            str((self.transactions, self.prev_hash)).encode("ascii")
        ).hexdigest()

    def to_string(self) -> str:
        """
        a function that allows to form a string from block objects.

        :returns:
             an object of the Block class.
        """
        block = [
            {
                "block_id": self.block_id,
                "prev_hash": self.prev_hash,
                "transactions": self.transactions,
            }
        ]
        return json.dumps(block, indent=4)

    def print_block_object(self) -> None:
        """
        a function for output block objects. It does not return anything.
        """
        print(self.to_string())


if __name__ == "__main__":
    block = Block()

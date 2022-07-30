import json
from hashlib import sha256
from dataclasses import dataclass, field


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
    transactions: list = field(default_factory=lambda: list())

    @classmethod
    def __create_block_helper(cls, prev_hash: str, transactions: list) -> "Block":
        """Helper function returns an new object of Block"""
        block_id = cls("", prev_hash, transactions).eval()
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
        return json.dumps(block)

    def print_block_object(self) -> None:
        """
        a function for output block objects. It does not return anything.
        """
        print(self.to_string())


if __name__ == "__main__":
    block = Block()
    tx = [
        {
            "trasaction_id": "977b41effe56b110a30f628863e53d80cc623693fab31fd0e19f38aa61c3ced0",
            "operation": [
                {
                    "sender": "14bea94409798b67d78cfd9d544c8714af1e195f061395cdfc401f5891212434",
                    "receiver": "13888b7f65354f0f67116ffd0254f77205620a3f6e8ce24d7f7bd346e9e7b17e",
                    "asset": 1000000,
                    "sig": "d6f3178feecf7bf7d27041dc1819ec612bb2be632ae5730d9cf2eb6b40b695a658a7e20b2a22141af92c209f4d1f4559ff1c0c0a9d60909e35513dc08c20a387f1a5c57b1dd21b5256005a4479c219d12f71285cd656fb41d30e7ebc2be4dbb0c2ec4a6a50b346b9f41580dbea7f376d5dc9a30dc1e3588df2b1e916e3fd23c7635afdb8aa10209fce8655938e60b9eac410f0da3175a3582451d32c20f12d343e32609a54906d2f3f099889c2ee821e7afb1f22c611b2f6537b2ed06e5553a62f896bcdbf1e475a37b3c9e2f72a84ba3475507126194ed164ab23bad95487ebcf25731a88ef128aee3dd511267e5f4bbcb3171663afd4f6f3b093b841c12944",
                }
            ],
            "nonce": 185881423,
        }
    ]
    tx2 = [
        {
            "trasaction_id": "977b41effe56b110a30f628863e53d80cc623693fab31fd0e19f38aa61c3ced0",
            "operation": [
                {
                    "sender": "14bea94409798b67d78cfd9d544c8714af1e195f061395cdfc401f5891212434",
                    "receiver": "13888b7f65354f0f67116ffd0254f77205620a3f6e8ce24d7f7bd346e9e7b17e",
                    "asset": 100000,
                    "sig": "bb2be632ae5730d9cf2eb6b40b695a65d6f3178feecf7bf7d27041dc1819ec6128a7e20b2a22141af92c209f4d1f4559ff1c0c0a9d60909e35513dc08c20a387f1a5c57b1dd21b5256005a4479c219d12f71285cd656fb41d30e7ebc2be4dbb0c2ec4a6a50b346b9f41580dbea7f376d5dc9a30dc1e3588df2b1e916e3fd23c7635afdb8aa10209fce8655938e60b9eac410f0da3175a3582451d32c20f12d343e32609a54906d2f3f099889c2ee821e7afb1f22c611b2f6537b2ed06e5553a62f896bcdbf1e475a37b3c9e2f72a84ba3475507126194ed164ab23bad95487ebcf25731a88ef128aee3dd511267e5f4bbcb3171663afd4f6f3b093b841c12944",
                }
            ],
            "nonce": 785881423,
        }
    ]
    block = block.create_block('0'.zfill(64), tx)
    block2 = block.create_block(block.block_id, tx2)
    print(block.to_string())
    print("\n\n\n\n")
    print(block2.to_string())

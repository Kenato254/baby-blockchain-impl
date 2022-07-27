# built-in
from collections import defaultdict
from dataclasses import dataclass, field

# Local imports
from block import Block
from keypair import KeyPair
from account import Account

# Class initialization
BLOCK: Block = Block()
ACCOUNT: Account = Account()

@dataclass(repr=False)
class Blockchain:
    """
    :coin_database:
        a table reflecting the current state of balances in the system. 
        The account identifier is used as the key, 
        the user balance is used as the value.

    :block_history:
        an array storing all the blocks added to the history.

    :tx_database:
        an array storing all transactions in history. It will be used for faster access 
        when checking the existence of the transaction in the history (protection against duplication).

    :fauce_coins:
        an integer value defining the number of coins available in the faucet for testing.
    """
    coin_database: defaultdict[dict] = field(default_factory=lambda: defaultdict(dict))
    block_history: list| None = None
    tx_database: list| None = None
    fauce_coins: int = 1000

    def init_blockchain(self) -> None:
        """
        a function that allows to initialize the blockchain. The genesis block is created and added to the history.
        """
        genesis: Block = BLOCK.create_block('0'.zfill(64), )
        self.block_history.append(genesis)

    def get_token_from_faucet(self) -> None:
        """
        a function that allows you to get test coins from the faucet. Updates the state of the coinDatabase and the
        balance of the account that was called by the method.
        """
        ...

    def validate_block(self) -> None:
        """
        a function that allows you to make a check and add a block to the history.
        """
        ...

    def show_coin_database(self) -> None:
        """
        a function that allows you to get the current state of accounts and balances.
        """
        pprint(blockchain.coin_database)

    def to_string(self) -> str:
        """
        a function that allows you to form a string from blockchain objects. 
        
        :returns:
             an object of the String class.
        """
        ...

    def print_blockchain(self) -> None:
        """
        a function for output blockchain objects.

        :returns:
            None
        """
        ...

if __name__ == "__main__":
    blockchain = Blockchain()
    #! First user
    user1 = ACCOUNT.gen_account()
    user1.add_key_pair_to_wallet(KeyPair())

    #! User1 Current balance
    print(f"Initial balance user1: {user1.get_balance}", end="\n")

    #! Add user1 to blockchain
    blockchain.coin_database.update({user1.get_account_id: user1.get_balance})

    #! Second user
    user2 = ACCOUNT.gen_account()
    user2.add_key_pair_to_wallet(KeyPair())

    #! User1 Current balance
    print(f"Initial balance user2: {user2.get_balance}", end="\n")

    #! Add user2 to blockchain
    blockchain.coin_database.update({user2.get_account_id: user2.get_balance})

    #! Transact (Send 500 to user1 from user2)
    user2.create_payment_op(user1, 500, 1)

    #! Print Coin database
    from pprint import pprint
    blockchain.show_coin_database()

    #! A
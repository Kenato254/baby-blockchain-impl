# built-in
import json
from collections import defaultdict
from dataclasses import dataclass, field

from numpy import block

# Local imports
from block import Block
from keypair import KeyPair
from account import Account, SpecialAccount
from transaction import Transaction

# Class initialization
BLOCK: Block = Block()


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
        a specail Account object value defining the number of coins available in the faucet for testing.
    """

    coin_database: defaultdict[dict] = field(default_factory=lambda: defaultdict(dict))
    block_history: list = field(default_factory=lambda: list())
    tx_database: defaultdict[list] = field(default_factory=lambda: defaultdict(list))
    # Sets one time coins
    __fauce_coins: SpecialAccount = field(default_factory=lambda: SpecialAccount(test_coins=1000), init=False)
    mempool_mirror: defaultdict[list] = field(default_factory=lambda: defaultdict(list))

    def __post_init__(self) -> None:
        """
        Special account that regulates coins circulation.
        Uses __post_init_ method in the Account class to set first time coins(fauce_coins) using a static transaction.

        Users can transact directly with fauce_coins or peer to peer
        """
        # Subsequent transactions are created from this class
        # BlockchainAccount: Account = Account(self.__fauce_coins)
        # Generate account new object
        self.__fauce_coins = self.__fauce_coins.gen_account()
        # Generates wallets
        self.__fauce_coins.add_key_pair_to_wallet(KeyPair())

    def get_fauce_coins(self) -> int:
        """functions returns available coins in the blockchain"""
        return self.__fauce_coins.get_balance

    def init_blockchain(self, tx_list: list) -> Block:
        """
        a function that allows to initialize the blockchain. The genesis block is created and added to the history.

        :returns:
            genesis block
        """
        # Create Genesis block with transactions in the mempool 
        genesis: Block = BLOCK.create_block("0".zfill(64), list(self.mempool_mirror.values()))
        return genesis

    def get_token_from_faucet(self, account: Account, amount: int) -> None:
        """
        a function that allows you to get test coins from the faucet. Updates the state of the coinDatabase and the
        balance of the account that was called by the method.

        :account:
            account balance to be updated

        :amount:
            amount to update on coin_database
        """
        if account and amount:
            # Create Transaction
            transaction: Transaction = self.__fauce_coins.create_payment_op(account, amount, 1)
            # Add transactions to the mempool
            self.mempool_mirror[len(self.mempool_mirror)] = transaction.get_trasaction_list
            # Update coin database
            self.update_coin_database(account)

    def update_coin_database(self, *args) -> None:
        """
        function update coin database 
        """
        if args:
            for account in args:
                if isinstance(account, Account):
                    self.coin_database.update({account.get_account_id: account.get_balance})
                else:
                    raise BaseException(f"Unknown account {account}")

    def validate_block(self, block: Block) -> None:
        """
        a function that allows you to make a check and add a block to the history.

        :block:
            to validate
        """
        for each in block.transactions:
            for tx in each:
                # * Double spending check
                if tx["transaction_id"] in self.tx_database.values():
                    raise BaseException(
                        f"Similar transaction '{tx['transaction_id']}' exist!"
                    )
        # * Update blockchain transaction history
        self.tx_database[len(self.tx_database)] = block.transactions

        self.mempool_mirror.clear() #* Clear mempool

        # * Update block history
        self.block_history.append(block.to_string())

    def show_coin_database(self) -> None:
        """
        a function that allows you to get the current state of accounts and balances.
        """
        print(json.dumps(self.coin_database, indent=4))

    def to_string(self) -> str:
        """
        a function that allows you to form a string from blockchain objects.

        :returns:
             an object of the String class.
        """
        blockchain_obj = {
            "coin_database": self.coin_database,
            "transaction_database": self.tx_database,
            "fauce_coins": self.get_fauce_coins(),
        }
        return json.dumps(blockchain_obj, indent=4)

    def print_block_history(self) -> None:
        """function prints block history"""
        from pprint import pprint
        pprint(self.block_history)

    def print_blockchain(self) -> None:
        """
        a function for output blockchain objects.

        :returns:
            None
        """
        print(self.to_string())


def main():
    blockchain = Blockchain()

    #! First user
    user1: Account = Account()
    user1 = user1.gen_account()
    user1.add_key_pair_to_wallet(KeyPair())
    # Add user1 to blockchain
    blockchain.get_token_from_faucet(user1, 100)

    #! Second user
    user2: Account = Account()
    user2 = user2.gen_account()
    user2.add_key_pair_to_wallet(KeyPair())
    # Add user2 to blockchain
    blockchain.get_token_from_faucet(user2, 20)

    #! Third user
    user3: Account = Account()
    user3 = user3.gen_account()
    user3.add_key_pair_to_wallet(KeyPair())
    # Add user3 to blockchain
    blockchain.get_token_from_faucet(user3, 450)

    #! Transact and create geneis block (Send 500 to user1 from user2)
    tx1 = user1.create_payment_op(user2, 5, 1)
    genesis = blockchain.init_blockchain(tx1.get_trasaction_list)
    # Validate genesis block
    blockchain.validate_block(genesis)
    # print(genesis.print_block_object())

    #! Create a list of transactions
    tx2 = user3.create_payment_op(user2, 30, 1)
    tx3 = user2.create_payment_op(user1, 3, 1)
    tx4 = user3.create_payment_op(user1, 100, 1)

    #! Add transactions to the mempool
    blockchain.mempool_mirror[len(blockchain.mempool_mirror)] = tx2.get_trasaction_list
    blockchain.mempool_mirror[len(blockchain.mempool_mirror)] = tx3.get_trasaction_list
    blockchain.mempool_mirror[len(blockchain.mempool_mirror)] = tx4.get_trasaction_list

    #! Create subsequent block
    block2 = BLOCK.create_block(genesis.block_id, list(blockchain.mempool_mirror.values()))
    blockchain.validate_block(block2)

    # Update coin database and print blockchain state
    blockchain.update_coin_database(user1,user2, user3)
    # blockchain.print_blockchain()
    blockchain.print_block_history()


if __name__ == "__main__":
    main()

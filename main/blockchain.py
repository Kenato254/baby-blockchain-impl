
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
    coin_database: dict| None = None
    block_history: list| None = None
    tx_database: list| None = None
    fauce_coins: int = 0

    def init_blockchain(self) -> None:
        """
        a function that allows to initialize the blockchain. The genesis block is created and added to the history.
        """
        ...

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
        ...

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
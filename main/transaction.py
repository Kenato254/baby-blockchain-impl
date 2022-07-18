from dataclasses import dataclass


@dataclass
class Transaction:
    """
    :transactionID:
        a unique identifier of the transaction (a hash value from all other fields of the transaction)

    :setOfOperations:
        a set of payment operations confirmed in this transaction.
    
    :nonce:
        a value to protect duplicate transactions with the same operations.
    """
    transaction_id = None
    set_of_operations = {}
    nonce = None

    def create_operation(self, ops: list, nonce: int) -> "Transaction":
        """
        a function that allows to create a transaction with all the necessary details.

        :ops:
            a list of operations 

        :nonce: 
             as input. 
        
        :returns:
             a Transaction object
        """
        ...

    def to_string(self) -> str:
        """
        function that allows to form a string from transaction objects. 
        Returns an object of the String class.
        """
        ...

    def print_key_pair(self) -> None:
        """
         function for output transaction objects. It does not return anything
        """
        ...
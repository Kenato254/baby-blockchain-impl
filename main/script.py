import sys
from copy import copy
from hashlib import sha256
from typing import Any

from signature import Signature

SIGNER = Signature()

class Script:
    """
    Simple Stack P2PKH Script Operation for Spending coins

    Operations:
        :DUP:
            Makes a copy of an item in the stack.

        :SHA256:
            Calculates the corresponding hash values.

        :EQUALVERIFY:
            Terminates or continues to execute script operation based on false or true conditions.

        :CHECKSIG:
            Single Signature verification.
    """

    # Operations:
    OP_DUP = "DUP"
    OP_SHA256 = "SHA256"
    OP_EQUALVERIFY = "EQUALVERIFY"
    OP_CHECKSIG = "CHECKSIG"

    def __init__(self, op_codes: Any) -> None:
        self.stack = []
        self.pointer = 0
        self.op_codes = op_codes.split(" ")

    def push(self, data) -> None:
        """
        a push operation on the stack.

        :data:
            an operation to be pushed into the stack
        """
        ...
        self.stack.append(data)
        self.pointer += 1

    def pop(self) -> Any:
        """
        removes last operation in the stack
        """        
        if self.pointer != 0:
            removed = self.stack.pop()
            self.pointer -= 1
            return removed
        raise IndexError("No Operation in the stack!")

    def peak(self) -> Any:
        """
        return last operation in the stack without completely removing it.
        """
        if self.pointer > 0:
            return self.stack[self.pointer]
        raise IndexError("No Operation in the stack!")

    def eval(self) -> int:
        for op in self.op_codes:
            if op == self.OP_DUP:
                peaked = self.op.eval(self.peak())
                self.push(peaked)

            elif self.op.__class__.__name__ == self.OP_SHA256:
                pubk = self.pop()
                hashed = self.op.eval(pubk)
                self.push(hashed)

            elif self.op.__class__.__name__  == self.OP_EQUALVERIFY:
                hash_from_tx = None
                self.push(hash_from_tx)
        
            

    def __repr__(self) -> str:
        return f"Operations {self.stack!r}"

class DataNode:
    def __init__(self, data: Any) -> None:
        self.data = data

    def bit_length(self):
        if isinstance(self.data, int):
            return self.data.bit_length()

    def eval(self):
        return self.data

class DUP:
    """
    Stack Iteraction Operation:
        Makes a copy of an item in the stack.
    """

    def __init__(self, data: Any) -> None:
        self.data = data

    def eval(self):
        return self.data.eval()

class SHA256:
    """
    Cryptographic Operation:
        Calculates the corresponding hash values,
    """

    def __init__(self, data: Any) -> None:
        self.data = data

    def eval(self):
        return sha256(
            self.data.eval().to_bytes(self.data.bit_length(), sys.byteorder)
        ).digest()

class EQUALVERIFY:
    """
    Stack Item Comparison Operation:
        Terminates or continues to execute script operation based on false or true conditions.
    """

    def __init__(self, data: Any, data2: Any) -> None:
        self.data = data
        self.data2 = data2

    def eval(self):
        return self.data.eval() == self.data2.eval()

class CHECKSIG:
    """
    Cryptographic Operation:
        Single Signature verification.
    """

    def __init__(self, msg, pubK: object, sig: Signature) -> None:
        self.pubK = pubK
        self.sig = sig
        self.msg = msg

    def eval(self):
        return SIGNER.verify_signature(self.msg.eval(), self.sig.eval(), self.pubK.eval()) 

if __name__ == "__main__":
    dup = DUP(100)
    script = Script(dup)
    # script.perform_operation()

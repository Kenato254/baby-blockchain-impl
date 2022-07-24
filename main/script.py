import struct
from typing import Any
from copy import copy
from pprint import pprint
from hashlib import sha256
from base64 import b64encode
from binascii import unhexlify


from signature import Signature

SIGNER = Signature()


class DataNode:
    """A node operand used in operations"""

    def __init__(self, data: Any) -> None:
        self.data = data

    def bit_length(self):
        if isinstance(self.data, int):
            return self.data.bit_length()

    def eval(self) -> Any:
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

    def eval(self) -> bytes:
        return sha256(unhexlify(self.data.eval())).hexdigest().encode("ascii")


class EQUALVERIFY:
    """
    Stack Item Comparison Operation:
        Terminates or continues to execute script operation based on false or true conditions.
    """

    def __init__(self, data: Any, data2: Any) -> None:
        self.data = data
        self.data2 = data2

    def eval(self) -> Any:
        return self.data.eval() == self.data2.eval()


class CHECKSIG:
    """
    Cryptographic Operation:
        Single Signature verification.
    """

    def __init__(self, msg, pubK: int, sig: bytes) -> None:
        self.msg = msg
        self.pubK = pubK
        self.sig = sig

    def eval(self) -> bool:
        return SIGNER.verify_signature(
            self.msg.eval(), self.sig.eval(), eval(unhexlify(self.pubK.eval()))
        )


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

    def __init__(self, op_codes: Any, amt: int | float | str | bytes) -> None:
        self.stack = []
        self.pointer = -1
        self.op_codes = op_codes.split(" ")

        if isinstance(amt, int):
            self.amt = amt.to_bytes(amt.bit_length(), "little")
        elif isinstance(amt, float):
            self.amt = struct.pack("f", amt)
        elif isinstance(amt, str):
            self.amt = amt.encode("ascii")
        elif isinstance(amt, bytes):
            self.amt = amt
        else:
            raise BaseException("Invalid {amt} input!")

    def push(self, data) -> None:
        """
        a push operation on the stack.

        :data:
            an operation to be pushed into the stack
        """
        self.stack.append(data)
        self.pointer += 1

    def pop(self) -> Any:
        """
        removes last operation in the stack
        """
        removed = self.stack.pop()
        self.pointer -= 1
        return removed

    def peak(self) -> Any:
        """
        return last operation in the stack without completely removing it.
        """
        return self.stack[self.pointer]

    def eval(self) -> bool:
        self.push(DataNode(unhexlify(self.op_codes[0])))

        for op in self.op_codes[1:]:
            if op == self.OP_DUP:
                peaked = self.peak()
                self.push(DUP(peaked))

            elif op == self.OP_SHA256:
                pubk = self.pop()
                self.push(SHA256(pubk))

            elif op == self.OP_EQUALVERIFY:
                hash1 = self.pop()
                hash2 = self.pop()
                response = EQUALVERIFY(hash1, hash2)

                if not response.eval():
                    return False

            elif op == self.OP_CHECKSIG:
                kPub = self.pop()
                sig = self.pop()
                result = CHECKSIG(DataNode(self.amt), kPub, sig)
                return result.eval()

            else:
                try:
                    temp = eval(op)
                except:
                    temp = op.encode("ascii")
                self.push(DataNode(temp))
        return False


if __name__ == "__main__":
    script = Script

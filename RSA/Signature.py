import sys
import base64
import pyasn1.codec.der.encoder
import pyasn1.type.univ
from hashlib import sha512
from dataclasses import dataclass

# ? Local Imports
from RSA.KeyPair import KeyPair

GETKEYPAIR = KeyPair(1024)


@dataclass
class Signature:
    """ Not completely implemented as per PKCS Specifications.
        This for learning purposes. Can be updated to meet RFC3447 specs
        https://datatracker.ietf.org/doc/html/rfc3447#page-27
    """
    __signature: bytes = None

    @property
    def get_signature(self):
        return self.__signature

    def sign_data(self, kPr: tuple[int, int], msg: bytes) -> bytes:
        """ Computes Digital Signature of a given message
            RSASP1
        """
        d, n = kPr  # Unpack Private Key
        msg_hash = int.from_bytes(sha512(msg).digest(), sys.byteorder)
        temp = pow(msg_hash, d, n)
        self.__signature = temp.to_bytes(temp.bit_length(), sys.byteorder)
        return self.__signature

    def verify_signature(self, msg, signed_msg: bytes, kPub: tuple[int, int]) -> bool:
        n, e = kPub  # Unpack Public Key
        msg_hash = int.from_bytes(sha512(msg).digest(), sys.byteorder)
        unsign_msg = pow(int.from_bytes(signed_msg, sys.byteorder), e, n)
        return msg_hash == unsign_msg

    def to_string(self, **kwargs):
        template = "--------------------BEGIN CERTIFICATE--------------------\n{}--------------------END CERTIFICATE--------------------\n"
        seq = pyasn1.type.univ.Sequence()
        for i, x in enumerate((0, int.from_bytes(self.get_signature, sys.byteorder))):
            seq.setComponentByPosition(i, pyasn1.type.univ.Integer(x))
        der = pyasn1.codec.der.encoder.encode(seq)
        if kwargs.get("format", None) == "PEM":
            return template.format(base64.encodebytes(der).decode("ascii"))
        return der

    def print_signature(self, **kwargs) -> None:
        print(self.to_string(**kwargs))


if __name__ == "__main__":
    signer = Signature()
    msg: bytes = b"Blockchain-Developer-Clases/baby-blockchain/baby-blockchain-impl/"

    privateKey, publicKey = GETKEYPAIR.gen_key_pair().values()
    signed_msg = signer.sign_data(privateKey, msg)
    print(signer.verify_signature(msg, signed_msg, publicKey))
    signer.print_signature(format="PEM")

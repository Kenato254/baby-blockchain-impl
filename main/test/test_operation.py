import sys
import unittest
from hashlib import sha256
from binascii import unhexlify, hexlify
from keypair import KeyPair
from signature import Signature

from script import DataNode, DUP, SHA256, EQUALVERIFY, CHECKSIG

KEYS = KeyPair()
SIGNER = Signature()

class OpsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.private_key, self.public_key = KEYS.gen_key_pair().values()

        self.data_node = DataNode(hexlify(str(self.public_key).encode("ascii")))
        self.dup_test = DUP(self.data_node)
        self.hash_ = SHA256(self.data_node)
        self.manual_hash = sha256(str(self.public_key).encode("ascii")).hexdigest().encode("ascii")

    def test_dup(self) -> None:
        """Test "DUP" Operation: return a duplicate-value """

        self.assertEqual(self.data_node.eval(), self.dup_test.eval())

    def test_sha256(self) -> None:
        """Test "SHA256" Operation: returns a sha-value """

        self.assertEqual(self.manual_hash, self.hash_.eval())


    def test_equal_verify(self) -> None:
        """Test "EQUALVERIFY" returns a "bool" """

        equal_verify_test = EQUALVERIFY(self.hash_.eval(), self.manual_hash)
        self.assertTrue(equal_verify_test)

    def test_check_sig(self) -> None:
        """ Test "CHECKSIG" """

        sig = SIGNER.sign_data(self.public_key, b"check!!")
        checked = CHECKSIG(DataNode(b"check"), self.data_node, sig)
        self.assertTrue(checked)
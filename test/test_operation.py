import sys
import unittest
from hashlib import sha256

sys.path.append("../")
from main.keypair import KeyPair
from main.signature import Signature

from main.script import DataNode, DUP, SHA256, EQUALVERIFY, CHECKSIG

KEYS = KeyPair()
SIGNER = Signature()

class OpsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.private_key, self.public_key = KEYS.gen_key_pair().values()
        self.data_node = DataNode(self.private_key[0])

        self.dup_test = DUP(self.data_node)
        self.hash = SHA256(self.data_node)
        self.manual_hash = sha256(
            self.private_key[0].to_bytes(
                self.private_key[0].bit_length(), sys.byteorder
            )
        ).digest()
        # self.check = CHECKSIG(self.public_key[1], self.sig)
        # self.sig = SIGNER.sign_data(self.public_key[1])

    def test_dup(self) -> None:
        """Test "DUP" Operation: return a duplicate-value """

        private_dup = self.dup_test.eval()
        self.assertEqual(self.private_key[0], private_dup)

    def test_sha256(self) -> None:
        """Test "SHA256" Operation: returns a sha-value """

        self.assertEqual(self.manual_hash, self.hash.eval())

    def test_equal_verify(self) -> None:
        """Test "EQUALVERIFY" returns a "bool" """

        equal_verify_test = EQUALVERIFY(self.hash.eval(), self.manual_hash)
        self.assertTrue(equal_verify_test)

    def test_check_sig(self) -> None:
        ...

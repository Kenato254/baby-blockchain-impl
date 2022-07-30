import unittest

from account import Account, SpecialAccount
from keypair import KeyPair

class AccountTest(unittest.TestCase):
    def setUp(self) -> None:
        # User 1
        super_account = SpecialAccount(test_coins=500.0)
        self.user1 = super_account.gen_account()
        self.user1.add_key_pair_to_wallet(KeyPair())

        # User 2
        user2 = Account()
        self.user2 = user2.gen_account()
        self.user2.add_key_pair_to_wallet(KeyPair())

    def test_initial_500_coins(self):
        self.assertEqual(self.user1.get_balance, 500.0)
    
    def test_payment_to_user2_from_user1(self):
            # Send 150 coins to user2 from user1
        self.user1.create_payment_op(self.user2, 150.50, 1)

        self.assertEqual(self.user1.get_balance, 500-150.50)
        self.assertEqual(self.user2.get_balance, 150.50)

    def test_payment_of_more_than_availble(self):
        with self.assertRaises(BaseException):
            self.user1.create_payment_op(self.user2, 10000, 1)


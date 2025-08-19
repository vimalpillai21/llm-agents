import unittest
from datetime import datetime, timedelta
from accounts import Account, Transaction, get_share_price


class TestAccount(unittest.TestCase):
    def setUp(self):
        self.account = Account()

    def test_deposit_positive_amount(self):
        self.account.deposit(1000.0)
        self.assertEqual(self.account._cash_balance, 1000.0)
        self.assertEqual(self.account._initial_deposit, 1000.0)
        self.assertEqual(len(self.account._transactions), 1)
        tx = self.account._transactions[0]
        self.assertEqual(tx.type, "deposit")
        self.assertEqual(tx.amount, 1000.0)
        self.assertIsNone(tx.symbol)
        self.assertIsNone(tx.quantity)
        self.assertIsNone(tx.price_per_share)

    def test_deposit_zero_or_negative_amount_raises(self):
        with self.assertRaises(ValueError):
            self.account.deposit(0)
        with self.assertRaises(ValueError):
            self.account.deposit(-100)

    def test_withdraw_positive_amount(self):
        self.account.deposit(1000)
        self.account.withdraw(400)
        self.assertEqual(self.account._cash_balance, 600)
        self.assertEqual(len(self.account._transactions), 2)
        tx = self.account._transactions[-1]
        self.assertEqual(tx.type, "withdrawal")
        self.assertEqual(tx.amount, 400)
        self.assertIsNone(tx.symbol)
        self.assertIsNone(tx.quantity)
        self.assertIsNone(tx.price_per_share)

    def test_withdraw_zero_or_negative_amount_raises(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(0)
        with self.assertRaises(ValueError):
            self.account.withdraw(-300)

    def test_withdraw_more_than_balance_raises(self):
        self.account.deposit(500)
        with self.assertRaises(ValueError):
            self.account.withdraw(600)

    def test_buy_shares_success(self):
        self.account.deposit(10000)  # deposit enough cash
        self.account.buy_shares("AAPL", 10)  # 10 * 150 = 1500
        self.assertEqual(self.account._cash_balance, 10000 - 1500)
        self.assertIn("AAPL", self.account._holdings)
        self.assertEqual(self.account._holdings["AAPL"], 10)
        self.assertEqual(len(self.account._transactions), 2)
        tx = self.account._transactions[-1]
        self.assertEqual(tx.type, "buy")
        self.assertEqual(tx.quantity, 10)
        self.assertEqual(tx.symbol, "AAPL")
        self.assertEqual(tx.price_per_share, 150.0)
        self.assertEqual(tx.amount, 0.0)

    def test_buy_shares_zero_or_negative_quantity_raises(self):
        self.account.deposit(10000)
        with self.assertRaises(ValueError):
            self.account.buy_shares("AAPL", 0)
        with self.assertRaises(ValueError):
            self.account.buy_shares("AAPL", -5)

    def test_buy_shares_insufficient_cash_raises(self):
        self.account.deposit(100)
        with self.assertRaises(ValueError):
            self.account.buy_shares("TSLA", 1)  # TSLA is 700, only have 100 cash

    def test_buy_shares_unknown_symbol_raises(self):
        self.account.deposit(10000)
        with self.assertRaises(ValueError):
            self.account.buy_shares("FAKE", 5)

    def test_sell_shares_success(self):
        self.account.deposit(10000)
        self.account.buy_shares("TSLA", 10)  # cost 7000
        self.account.sell_shares("TSLA", 5)
        expected_cash = 10000 - (700 * 10) + (700 * 5)
        self.assertEqual(self.account._cash_balance, expected_cash)
        self.assertEqual(self.account._holdings["TSLA"], 5)
        self.assertEqual(len(self.account._transactions), 3)
        tx = self.account._transactions[-1]
        self.assertEqual(tx.type, "sell")
        self.assertEqual(tx.quantity, 5)
        self.assertEqual(tx.symbol, "TSLA")
        self.assertEqual(tx.price_per_share, 700.0)
        self.assertEqual(tx.amount, 0.0)

    def test_sell_shares_removes_symbol_when_zero_holdings(self):
        self.account.deposit(10000)
        self.account.buy_shares("AAPL", 2)
        self.account.sell_shares("AAPL", 2)
        self.assertNotIn("AAPL", self.account._holdings)

    def test_sell_shares_zero_or_negative_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.account.sell_shares("AAPL", 0)
        with self.assertRaises(ValueError):
            self.account.sell_shares("AAPL", -3)

    def test_sell_shares_insufficient_shares_raises(self):
        self.account.deposit(10000)
        self.account.buy_shares("GOOGL", 2)
        with self.assertRaises(ValueError):
            self.account.sell_shares("GOOGL", 3)
        with self.assertRaises(ValueError):
            self.account.sell_shares("AAPL", 1)  # never bought

    def test_get_holdings_immutable_copy(self):
        self.account.deposit(1000)
        self.account.buy_shares("AAPL", 1)
        holdings = self.account.get_holdings()
        holdings["AAPL"] = 100
        self.assertNotEqual(self.account.get_holdings().get("AAPL"), 100)

    def test_list_transactions_immutable_copy(self):
        self.account.deposit(500)
        transactions = self.account.list_transactions()
        self.assertIsInstance(transactions, list)
        transactions.append("fake")
        self.assertNotIn("fake", self.account.list_transactions())

    def test_get_portfolio_value(self):
        self.account.deposit(10000)
        self.account.buy_shares("AAPL", 10)  # cost 1500
        self.account.buy_shares("TSLA", 5)   # cost 3500
        expected_cash = 10000 - (150 * 10) - (700 * 5)
        expected_value = expected_cash + (150 * 10) + (700 * 5)
        self.assertAlmostEqual(self.account.get_portfolio_value(), expected_value)

    def test_get_profit_loss(self):
        self.account.deposit(10000)
        # Initially profit loss is zero
        self.assertAlmostEqual(self.account.get_profit_loss(), 0.0)
        self.account.buy_shares("AAPL", 10)  # spend 1500
        # Profit loss should be current portfolio value minus initial deposit
        expected = self.account.get_portfolio_value() - 10000
        self.assertAlmostEqual(self.account.get_profit_loss(), expected)

    def test_transaction_repr(self):
        now = datetime.now()
        tx = Transaction(
            timestamp=now,
            type="deposit",
            amount=123.45,
            symbol=None,
            quantity=None,
            price_per_share=None,
        )
        expected_repr = (
            f"Transaction(timestamp={now}, type=deposit, amount=123.45, "
            f"symbol=None, quantity=None, price_per_share=None)"
        )
        self.assertEqual(repr(tx), expected_repr)

    def test_get_share_price_known_symbol(self):
        self.assertEqual(get_share_price("AAPL"), 150.0)
        self.assertEqual(get_share_price("TSLA"), 700.0)
        self.assertEqual(get_share_price("GOOGL"), 2800.0)

    def test_get_share_price_unknown_symbol_raises(self):
        with self.assertRaises(ValueError):
            get_share_price("UNKNOWN")

if __name__ == "__main__":
    unittest.main()
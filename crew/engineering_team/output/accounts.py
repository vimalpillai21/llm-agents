from datetime import datetime
from typing import Optional, List, Dict


def get_share_price(symbol: str) -> float:
    prices = {
        "AAPL": 150.0,
        "TSLA": 700.0,
        "GOOGL": 2800.0,
    }
    if symbol not in prices:
        raise ValueError(f"Unknown share symbol: {symbol}")
    return prices[symbol]


class Transaction:
    def __init__(
        self,
        timestamp: datetime,
        type: str,
        amount: float,
        symbol: Optional[str],
        quantity: Optional[int],
        price_per_share: Optional[float],
    ):
        self.timestamp = timestamp
        self.type = type  # "deposit", "withdrawal", "buy", "sell"
        self.amount = amount  # funds amount for deposit/withdrawal; zero for buy/sell
        self.symbol = symbol  # stock symbol for buy/sell; None for deposit/withdrawal
        self.quantity = quantity  # number of shares for buy/sell; None for deposit/withdrawal
        self.price_per_share = price_per_share  # price per share for buy/sell; None for deposit/withdrawal

    def __repr__(self):
        return (
            f"Transaction(timestamp={self.timestamp}, type={self.type}, amount={self.amount}, "
            f"symbol={self.symbol}, quantity={self.quantity}, price_per_share={self.price_per_share})"
        )


class Account:
    def __init__(self):
        self._cash_balance: float = 0.0
        self._initial_deposit: float = 0.0
        self._holdings: Dict[str, int] = {}
        self._transactions: List[Transaction] = []

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._cash_balance += amount
        self._initial_deposit += amount
        self._transactions.append(
            Transaction(
                timestamp=datetime.now(),
                type="deposit",
                amount=amount,
                symbol=None,
                quantity=None,
                price_per_share=None,
            )
        )

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self._cash_balance:
            raise ValueError("Insufficient cash balance for withdrawal")
        self._cash_balance -= amount
        self._transactions.append(
            Transaction(
                timestamp=datetime.now(),
                type="withdrawal",
                amount=amount,
                symbol=None,
                quantity=None,
                price_per_share=None,
            )
        )

    def buy_shares(self, symbol: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity to buy must be positive")
        price = get_share_price(symbol)
        total_cost = price * quantity
        if total_cost > self._cash_balance:
            raise ValueError("Insufficient cash to buy shares")
        self._cash_balance -= total_cost
        self._holdings[symbol] = self._holdings.get(symbol, 0) + quantity
        self._transactions.append(
            Transaction(
                timestamp=datetime.now(),
                type="buy",
                amount=0.0,
                symbol=symbol,
                quantity=quantity,
                price_per_share=price,
            )
        )

    def sell_shares(self, symbol: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity to sell must be positive")
        if symbol not in self._holdings or self._holdings[symbol] < quantity:
            raise ValueError("Insufficient shares to sell")
        price = get_share_price(symbol)
        total_revenue = price * quantity
        self._holdings[symbol] -= quantity
        # If after sale holdings are zero, remove the symbol entry for cleanliness
        if self._holdings[symbol] == 0:
            del self._holdings[symbol]
        self._cash_balance += total_revenue
        self._transactions.append(
            Transaction(
                timestamp=datetime.now(),
                type="sell",
                amount=0.0,
                symbol=symbol,
                quantity=quantity,
                price_per_share=price,
            )
        )

    def get_holdings(self) -> Dict[str, int]:
        # Return a copy to prevent external mutation
        return dict(self._holdings)

    def get_portfolio_value(self) -> float:
        total_value = self._cash_balance
        for symbol, quantity in self._holdings.items():
            price = get_share_price(symbol)
            total_value += price * quantity
        return total_value

    def get_profit_loss(self) -> float:
        current_value = self.get_portfolio_value()
        return current_value - self._initial_deposit

    def list_transactions(self) -> List[Transaction]:
        # Return a copy to prevent external mutation
        return list(self._transactions)
```markdown
# accounts.py - Detailed Design for the Account Management System

## Overview

This module implements a simple account management system for a trading simulation platform.  
Users can create accounts, deposit and withdraw funds, buy and sell shares, and track portfolio value and transactions.  
A test implementation of `get_share_price(symbol)` is included, returning fixed share prices for AAPL, TSLA, and GOOGL.

---

## Classes and Functions

### 1. Function: `get_share_price(symbol: str) -> float`
- **Purpose:** Returns the current price of a share given its symbol.
- **Behavior:**  
  - Returns a fixed price for the known symbols:  
    - "AAPL" → 150.0  
    - "TSLA" → 700.0  
    - "GOOGL" → 2800.0  
  - Raises ValueError for unknown symbols.
- **Usage:** Called internally by Account methods to get current share prices.

---

### 2. Class: `Transaction`
- **Purpose:** Represents a single user transaction (deposit, withdrawal, buy, or sell).
  
- **Attributes:**  
  - `timestamp` (datetime) - When the transaction occurred.  
  - `type` (str) - One of: "deposit", "withdrawal", "buy", "sell".  
  - `amount` (float) - Amount of funds for deposits and withdrawals; zero for buy/sell (since share quantity and price capture value).  
  - `symbol` (str or None) - Stock symbol for buy/sell; None for deposit/withdrawal.  
  - `quantity` (int or None) - Shares bought/sold for buy/sell; None for deposit/withdrawal.  
  - `price_per_share` (float or None) - Share price at which buy/sell happened; None for deposit/withdrawal.

- **Constructor:**  
  `__init__(self, timestamp: datetime, type: str, amount: float, symbol: Optional[str], quantity: Optional[int], price_per_share: Optional[float])`

---

### 3. Class: `Account`
- **Purpose:** Represents a user's trading account, managing cash balance, share holdings, transactions, and profit/loss.

- **Attributes:**  
  - `_cash_balance` (float) - Current available cash balance.  
  - `_initial_deposit` (float) - Total funds initially deposited (for profit/loss calculations).  
  - `_holdings` (dict[str, int]) - Maps share symbol to quantity currently held.  
  - `_transactions` (list[Transaction]) - List of all transactions made, ordered chronologically.

- **Constructor:**  
  `__init__(self)`: Initializes an empty account with zero cash balance and no holdings.

#### Methods:

1. `deposit(self, amount: float) -> None`  
   - Adds funds to cash balance and records a deposit transaction.  
   - `amount` must be positive.  
   - Increases `_cash_balance` and `_initial_deposit`.

2. `withdraw(self, amount: float) -> None`  
   - Withdraws funds from cash balance if sufficient cash available.  
   - `amount` must be positive and not cause negative cash balance.  
   - Records a withdrawal transaction.

3. `buy_shares(self, symbol: str, quantity: int) -> None`  
   - Buys `quantity` shares of `symbol` at current share price.  
   - Checks sufficient cash to cover total cost (price * quantity).  
   - Deducts cash and adds to holdings.  
   - Records a buy transaction.

4. `sell_shares(self, symbol: str, quantity: int) -> None`  
   - Sells `quantity` shares of `symbol` at current share price.  
   - Checks sufficient shares in holdings.  
   - Adds cash from sale and deducts share quantity from holdings.  
   - Records a sell transaction.

5. `get_holdings(self) -> dict[str, int]`  
   - Returns a copy of current holdings dictionary (symbol → quantity).

6. `get_portfolio_value(self) -> float`  
   - Calculates total portfolio value as cash balance plus market value of all shares held.  
   - Uses `get_share_price` to get current price per share.

7. `get_profit_loss(self) -> float`  
   - Calculates profit or loss as (current portfolio value) - (initial deposit).

8. `list_transactions(self) -> list[Transaction]`  
   - Returns a copy of the full chronological list of transactions.

---

## Error Handling

- Raising `ValueError` for:
  - Attempting to deposit/withdraw non-positive amounts.
  - Attempting to withdraw more than available cash.
  - Attempting to buy shares without enough cash.
  - Attempting to sell shares not owned or insufficient quantity.
  - Unknown share symbols in buy/sell operations.

---

## Additional Notes

- The entire system is self-contained in `accounts.py`.
- The design supports potential extensions such as multiple users or persisted storage by encapsulating state in the `Account` class.
- Timestamp for transactions will be generated at transaction creation time using `datetime.datetime.now()`.

---

# Summary of module contents:

```python
from datetime import datetime
from typing import Optional, List, Dict

def get_share_price(symbol: str) -> float:
    ...

class Transaction:
    def __init__(self, timestamp: datetime, type: str, amount: float,
                 symbol: Optional[str], quantity: Optional[int],
                 price_per_share: Optional[float]):
        ...

class Account:
    def __init__(self):
        ...
    def deposit(self, amount: float) -> None:
        ...
    def withdraw(self, amount: float) -> None:
        ...
    def buy_shares(self, symbol: str, quantity: int) -> None:
        ...
    def sell_shares(self, symbol: str, quantity: int) -> None:
        ...
    def get_holdings(self) -> Dict[str, int]:
        ...
    def get_portfolio_value(self) -> float:
        ...
    def get_profit_loss(self) -> float:
        ...
    def list_transactions(self) -> List[Transaction]:
        ...
```
```
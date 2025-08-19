import gradio as gr
from datetime import datetime
from accounts import Account, get_share_price


account = Account()


def create_account():
    global account
    account = Account()
    return "Account created/reset."


def deposit_funds(amount):
    try:
        amount = float(amount)
        account.deposit(amount)
        return f"Deposited ${amount:.2f} successfully."
    except Exception as e:
        return f"Error: {str(e)}"


def withdraw_funds(amount):
    try:
        amount = float(amount)
        account.withdraw(amount)
        return f"Withdrew ${amount:.2f} successfully."
    except Exception as e:
        return f"Error: {str(e)}"


def buy_shares(symbol, quantity):
    symbol = symbol.strip().upper()
    try:
        quantity = int(quantity)
        account.buy_shares(symbol, quantity)
        return f"Bought {quantity} shares of {symbol}."
    except Exception as e:
        return f"Error: {str(e)}"


def sell_shares(symbol, quantity):
    symbol = symbol.strip().upper()
    try:
        quantity = int(quantity)
        account.sell_shares(symbol, quantity)
        return f"Sold {quantity} shares of {symbol}."
    except Exception as e:
        return f"Error: {str(e)}"


def show_holdings():
    holdings = account.get_holdings()
    if not holdings:
        return "No holdings."
    lines = []
    for symbol, qty in holdings.items():
        price = get_share_price(symbol)
        value = qty * price
        lines.append(f"{symbol}: {qty} shares @ ${price:.2f} = ${value:.2f}")
    return "\n".join(lines)


def show_portfolio_value():
    value = account.get_portfolio_value()
    return f"Total portfolio value (cash + shares): ${value:.2f}"


def show_profit_loss():
    pl = account.get_profit_loss()
    sign = "+" if pl >= 0 else "-"
    return f"Profit/Loss since initial deposit: {sign}${abs(pl):.2f}"


def show_transactions():
    txs = account.list_transactions()
    if not txs:
        return "No transactions recorded."
    lines = []
    for tx in txs:
        time_str = tx.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        if tx.type in ["deposit", "withdrawal"]:
            lines.append(f"{time_str}: {tx.type.capitalize()} ${tx.amount:.2f}")
        elif tx.type in ["buy", "sell"]:
            lines.append(f"{time_str}: {tx.type.capitalize()} {tx.quantity} shares of {tx.symbol} @ ${tx.price_per_share:.2f}")
    return "\n".join(lines)


with gr.Blocks() as demo:
    gr.Markdown("# Trading Simulation Account Demo")

    with gr.Row():
        with gr.Column():
            btn_create = gr.Button("Create/Reset Account")
            inp_deposit = gr.Textbox(label="Deposit Amount (USD)", placeholder="e.g. 1000", value="")
            btn_deposit = gr.Button("Deposit")
            inp_withdraw = gr.Textbox(label="Withdraw Amount (USD)", placeholder="e.g. 500", value="")
            btn_withdraw = gr.Button("Withdraw")
        with gr.Column():
            inp_buy_symbol = gr.Textbox(label="Buy Shares Symbol", placeholder="AAPL, TSLA, GOOGL", value="")
            inp_buy_qty = gr.Textbox(label="Buy Quantity", placeholder="e.g. 10", value="")
            btn_buy = gr.Button("Buy Shares")
            inp_sell_symbol = gr.Textbox(label="Sell Shares Symbol", placeholder="AAPL, TSLA, GOOGL", value="")
            inp_sell_qty = gr.Textbox(label="Sell Quantity", placeholder="e.g. 5", value="")
            btn_sell = gr.Button("Sell Shares")

    output_text = gr.Textbox(label="Output", interactive=False, lines=8)

    with gr.Row():
        btn_holdings = gr.Button("Show Holdings")
        btn_portfolio_value = gr.Button("Show Portfolio Value")
        btn_profit_loss = gr.Button("Show Profit/Loss")
        btn_transactions = gr.Button("Show Transactions")

    btn_create.click(create_account, outputs=output_text)
    btn_deposit.click(deposit_funds, inputs=inp_deposit, outputs=output_text)
    btn_withdraw.click(withdraw_funds, inputs=inp_withdraw, outputs=output_text)
    btn_buy.click(buy_shares, inputs=[inp_buy_symbol, inp_buy_qty], outputs=output_text)
    btn_sell.click(sell_shares, inputs=[inp_sell_symbol, inp_sell_qty], outputs=output_text)
    btn_holdings.click(show_holdings, outputs=output_text)
    btn_portfolio_value.click(show_portfolio_value, outputs=output_text)
    btn_profit_loss.click(show_profit_loss, outputs=output_text)
    btn_transactions.click(show_transactions, outputs=output_text)

if __name__ == "__main__":
    demo.launch()
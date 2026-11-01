"""
Stock Portfolio Performance Tracker
-----------------------------------
- Enter ticker symbols, buy prices and share quantities.
- Positions are stored in a dictionary: {ticker: {"buy_price", "shares"}}.
- Current prices come from Yahoo Finance (yfinance) when available;
  otherwise you are asked to type the current price manually.
- Computes invested capital, current market value and % gain/loss per holding
  and for the whole portfolio, prints a formatted table, and appends a
  timestamped log to 'portfolio_summary.csv' (built-in csv module).
- Optional: if 'sp500.csv' (S&P 500 Ticker Dataset) is in the same folder,
  tickers are validated against it and company names are shown.
"""

import csv
import os
from datetime import datetime

try:
    import yfinance as yf          # optional: pip install yfinance
except ImportError:
    yf = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_FILE = os.path.join(BASE_DIR, "sp500.csv")
SUMMARY_FILE = os.path.join(BASE_DIR, "portfolio_summary.csv")
FIELDS = ["Timestamp", "Symbol", "Company", "Shares", "Buy Price",
          "Current Price", "Invested", "Current Value", "Gain/Loss", "Gain/Loss %"]


# ---------- Data loading ----------
def load_sp500(path=DATASET_FILE):
    """Return {symbol: company name} from the S&P 500 CSV (empty if missing)."""
    companies = {}
    try:
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                companies[row["Symbol"].upper()] = row["Security"]
    except OSError:
        print("(sp500.csv not found - ticker validation disabled.)")
    return companies


def fetch_price(ticker):
    """Try to get the latest price from Yahoo Finance; return None on failure."""
    if yf is None:
        return None
    try:
        hist = yf.Ticker(ticker.replace(".", "-")).history(period="1d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
    except Exception:
        pass
    return None


# ---------- Input helpers ----------
def ask_float(prompt, minimum=0.0):
    """Prompt until a number greater than `minimum` is entered."""
    while True:
        try:
            value = float(input(prompt).strip().replace(",", ""))
            if value > minimum:
                return value
            print(f"Value must be greater than {minimum}.")
        except ValueError:
            print("Please enter a valid number.")


def collect_positions(companies):
    """Interactively build the portfolio dictionary."""
    portfolio = {}
    print("Enter your holdings (press Enter on the ticker to finish).\n")
    while True:
        ticker = input("Ticker symbol: ").strip().upper()
        if not ticker:
            if portfolio:
                break
            print("Add at least one holding first.")
            continue
        if companies and ticker not in companies:
            print(f"'{ticker}' was not found in the S&P 500 dataset. Try again.")
            continue
        buy_price = ask_float("  Buy price per share ($): ")
        shares = ask_float("  Number of shares: ")
        if ticker in portfolio:      # merge repeat buys using weighted average cost
            old = portfolio[ticker]
            total = old["shares"] + shares
            old["buy_price"] = (old["buy_price"] * old["shares"] + buy_price * shares) / total
            old["shares"] = total
        else:
            portfolio[ticker] = {"buy_price": buy_price, "shares": shares}
        print(f"  Added {ticker}.\n")
    return portfolio


# ---------- Calculations ----------
def evaluate(portfolio, companies):
    """Return a list of result rows (dicts), one per holding."""
    results = []
    for ticker, pos in portfolio.items():
        price = fetch_price(ticker)
        if price is None:
            print(f"Could not fetch live price for {ticker}.")
            price = ask_float(f"  Enter current price for {ticker} ($): ")
        invested = pos["buy_price"] * pos["shares"]
        value = price * pos["shares"]
        results.append({
            "Symbol": ticker,
            "Company": companies.get(ticker, "N/A"),
            "Shares": pos["shares"],
            "Buy Price": pos["buy_price"],
            "Current Price": price,
            "Invested": invested,
            "Current Value": value,
            "Gain/Loss": value - invested,
            "Gain/Loss %": (value - invested) / invested * 100,
        })
    return results


def totals(results):
    invested = sum(r["Invested"] for r in results)
    value = sum(r["Current Value"] for r in results)
    return invested, value, value - invested, (value - invested) / invested * 100


# ---------- Output ----------
def print_report(results):
    line = "-" * 96
    print("\n" + line)
    print(f"{'Symbol':<8}{'Shares':>9}{'Buy $':>11}{'Now $':>11}"
          f"{'Invested $':>14}{'Value $':>14}{'Gain/Loss $':>14}{'%':>9}")
    print(line)
    for r in results:
        print(f"{r['Symbol']:<8}{r['Shares']:>9.2f}{r['Buy Price']:>11.2f}"
              f"{r['Current Price']:>11.2f}{r['Invested']:>14,.2f}"
              f"{r['Current Value']:>14,.2f}{r['Gain/Loss']:>+14,.2f}"
              f"{r['Gain/Loss %']:>+8.2f}%")
    inv, val, gl, pct = totals(results)
    print(line)
    print(f"{'TOTAL':<8}{'':>9}{'':>11}{'':>11}{inv:>14,.2f}{val:>14,.2f}"
          f"{gl:>+14,.2f}{pct:>+8.2f}%")
    print(line)


def save_summary(results, path=SUMMARY_FILE):
    """Append this run to the CSV log (header written only for a new file)."""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_file = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        for r in results:
            row = {"Timestamp": stamp}
            row.update({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})
            writer.writerow(row)
        inv, val, gl, pct = totals(results)
        writer.writerow({"Timestamp": stamp, "Symbol": "TOTAL", "Company": "Portfolio",
                         "Invested": round(inv, 2), "Current Value": round(val, 2),
                         "Gain/Loss": round(gl, 2), "Gain/Loss %": round(pct, 2)})
    print(f"\nSummary logged to {os.path.basename(path)}")


def main():
    print("=== STOCK PORTFOLIO PERFORMANCE TRACKER ===\n")
    companies = load_sp500()
    portfolio = collect_positions(companies)
    results = evaluate(portfolio, companies)
    print_report(results)
    save_summary(results)


if __name__ == "__main__":
    main()

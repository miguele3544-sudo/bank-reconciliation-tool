import pandas as pd


def load_transactions(path):
    df = pd.read_csv(path, parse_dates=["date"])
    df["amount"] = df["amount"].round(2)
    df["matched"] = False
    return df


def match_transactions(bank, ledger, date_tolerance_days=3):
    for i, b in bank.iterrows():
        candidates = ledger[
            (~ledger["matched"])
            & (ledger["amount"] == b["amount"])
            & ((ledger["date"] - b["date"]).abs().dt.days <= date_tolerance_days)
        ]
        if not candidates.empty:
            j = candidates.index[0]
            bank.at[i, "matched"] = True
            ledger.at[j, "matched"] = True
    return bank, ledger


def reconcile(bank_path, ledger_path, bank_ending_balance, book_ending_balance):
    bank = load_transactions(bank_path)
    ledger = load_transactions(ledger_path)
    bank, ledger = match_transactions(bank, ledger)

    unmatched_bank = bank[~bank["matched"]]
    unmatched_ledger = ledger[~ledger["matched"]]

    # Items only in the books (outstanding checks, deposits in transit) adjust the bank balance.
    adjusted_bank = round(bank_ending_balance + unmatched_ledger["amount"].sum(), 2)
    # Items only on the bank statement (fees, interest) adjust the book balance.
    adjusted_book = round(book_ending_balance + unmatched_bank["amount"].sum(), 2)

    return {
        "unmatched_bank": unmatched_bank,
        "unmatched_ledger": unmatched_ledger,
        "adjusted_bank": adjusted_bank,
        "adjusted_book": adjusted_book,
        "difference": round(adjusted_bank - adjusted_book, 2),
    }


if __name__ == "__main__":
    result = reconcile(
        "data/bank_statement.csv",
        "data/ledger.csv",
        bank_ending_balance=5637.50,
        book_ending_balance=6000.00,
    )
    cols = ["date", "description", "amount"]
    print("\nOn bank statement but not in books (record these):")
    print(result["unmatched_bank"][cols].to_string(index=False))
    print("\nIn books but not yet on bank statement:")
    print(result["unmatched_ledger"][cols].to_string(index=False))
    print(f"\nAdjusted bank balance: {result['adjusted_bank']:,.2f}")
    print(f"Adjusted book balance: {result['adjusted_book']:,.2f}")
    print(f"Difference:            {result['difference']:,.2f}")
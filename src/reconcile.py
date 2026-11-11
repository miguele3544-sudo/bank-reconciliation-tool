import argparse

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


def to_cents(amount):
    return round(abs(amount) * 100)


def same_digits(a, b):
    return sorted(str(to_cents(a))) == sorted(str(to_cents(b)))


def classify_error(bank_amount, ledger_amount):
    # Only compare amounts going the same direction (both in or both out).
    if bank_amount == ledger_amount or (bank_amount > 0) != (ledger_amount > 0):
        return None
    bank_cents, ledger_cents = to_cents(bank_amount), to_cents(ledger_amount)
    # Transposition and slide errors always create a difference divisible by 9.
    if abs(bank_cents - ledger_cents) % 9 != 0:
        return None
    big, small = max(bank_cents, ledger_cents), min(bank_cents, ledger_cents)
    if big in (small * 10, small * 100):
        return "Slide error"
    if same_digits(bank_amount, ledger_amount):
        return "Transposition error"
    return None


def find_recording_errors(bank, ledger, date_tolerance_days=3):
    errors = []
    for i, b in bank[~bank["matched"]].iterrows():
        candidates = ledger[
            (~ledger["matched"])
            & ((ledger["date"] - b["date"]).abs().dt.days <= date_tolerance_days)
        ]
        for j, l in candidates.iterrows():
            error_type = classify_error(b["amount"], l["amount"])
            if error_type:
                errors.append({
                    "error_type": error_type,
                    "bank_description": b["description"],
                    "ledger_description": l["description"],
                    "bank_amount": b["amount"],
                    "ledger_amount": l["amount"],
                    # The bank shows what actually cleared, so the books are corrected to it.
                    "book_correction": round(b["amount"] - l["amount"], 2),
                })
                bank.at[i, "matched"] = True
                ledger.at[j, "matched"] = True
                break
    columns = ["error_type", "bank_description", "ledger_description",
               "bank_amount", "ledger_amount", "book_correction"]
    return pd.DataFrame(errors, columns=columns)


def reconcile(bank_path, ledger_path, bank_ending_balance, book_ending_balance,
              date_tolerance_days=3):
    bank = load_transactions(bank_path)
    ledger = load_transactions(ledger_path)
    bank, ledger = match_transactions(bank, ledger, date_tolerance_days)
    recording_errors = find_recording_errors(bank, ledger, date_tolerance_days)

    unmatched_bank = bank[~bank["matched"]]
    unmatched_ledger = ledger[~ledger["matched"]]

    # Items only in the books (outstanding checks, deposits in transit) adjust the bank balance.
    adjusted_bank = round(bank_ending_balance + unmatched_ledger["amount"].sum(), 2)
    # Items only on the bank statement (fees, interest) and corrections of
    # recording errors adjust the book balance.
    adjusted_book = round(
        book_ending_balance
        + unmatched_bank["amount"].sum()
        + recording_errors["book_correction"].sum(),
        2,
    )

    return {
        "unmatched_bank": unmatched_bank,
        "unmatched_ledger": unmatched_ledger,
        "recording_errors": recording_errors,
        "adjusted_bank": adjusted_bank,
        "adjusted_book": adjusted_book,
        "difference": round(adjusted_bank - adjusted_book, 2),
    }


def print_report(result):
    cols = ["date", "description", "amount"]
    print("\nOn bank statement but not in books (record these):")
    print(result["unmatched_bank"][cols].to_string(index=False))
    print("\nIn books but not yet on bank statement:")
    print(result["unmatched_ledger"][cols].to_string(index=False))
    print("\nProbable recording errors (correct these in the books):")
    if result["recording_errors"].empty:
        print("None found")
    else:
        print(result["recording_errors"].to_string(index=False))
    print(f"\nAdjusted bank balance: {result['adjusted_bank']:,.2f}")
    print(f"Adjusted book balance: {result['adjusted_book']:,.2f}")
    print(f"Difference:            {result['difference']:,.2f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reconcile a bank statement against the general ledger."
    )
    parser.add_argument("bank_file", nargs="?", default="data/bank_statement.csv",
                        help="path to the bank statement CSV")
    parser.add_argument("ledger_file", nargs="?", default="data/ledger.csv",
                        help="path to the ledger CSV")
    parser.add_argument("--bank-balance", type=float, default=5637.50,
                        help="ending balance per the bank statement")
    parser.add_argument("--book-balance", type=float, default=6000.00,
                        help="ending balance per the books")
    parser.add_argument("--tolerance", type=int, default=3,
                        help="maximum days apart for two transactions to match")
    args = parser.parse_args()

    result = reconcile(args.bank_file, args.ledger_file,
                       args.bank_balance, args.book_balance, args.tolerance)
    print_report(result)
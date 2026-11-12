import argparse

import pandas as pd


def load_transactions(path):
    df = pd.read_csv(path, parse_dates=["date"])
    df["amount"] = df["amount"].round(2)
    df["matched"] = False
    return df


def days_apart(ledger, bank_date):
    return (ledger["date"] - bank_date).abs().dt.days


def match_transactions(bank, ledger, date_tolerance_days=3):
    for i, b in bank.iterrows():
        candidates = ledger[
            (~ledger["matched"])
            & (ledger["amount"] == b["amount"])
            & (days_apart(ledger, b["date"]) <= date_tolerance_days)
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
    if bank_amount == ledger_amount:
        return None
    # Same amount, opposite direction: money in was recorded as money out, or vice versa.
    if bank_amount == -ledger_amount:
        return "Sign reversal"
    if (bank_amount > 0) != (ledger_amount > 0):
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
            & (days_apart(ledger, b["date"]) <= date_tolerance_days)
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


def find_duplicate_entries(ledger):
    # An unmatched entry identical to an earlier one (same date, description and
    # amount) was probably entered twice.
    repeats = ledger.duplicated(subset=["date", "description", "amount"], keep="first")
    duplicates = []
    for j, l in ledger[repeats & ~ledger["matched"]].iterrows():
        duplicates.append({
            "date": l["date"],
            "description": l["description"],
            "amount": l["amount"],
            # Reversing the duplicate removes its effect from the books.
            "book_correction": -l["amount"],
        })
        ledger.at[j, "matched"] = True
    columns = ["date", "description", "amount", "book_correction"]
    return pd.DataFrame(duplicates, columns=columns)


def find_near_matches(bank, ledger, near_match_days=10):
    near_matches = []
    for i, b in bank[~bank["matched"]].iterrows():
        gaps = days_apart(ledger, b["date"])
        candidates = ledger[
            (~ledger["matched"])
            & (ledger["amount"] == b["amount"])
            & (gaps <= near_match_days)
        ]
        if not candidates.empty:
            j = gaps[candidates.index].idxmin()  # the closest date wins
            l = ledger.loc[j]
            near_matches.append({
                "bank_date": b["date"],
                "bank_description": b["description"],
                "ledger_date": l["date"],
                "ledger_description": l["description"],
                "amount": b["amount"],
                "days_apart": int(gaps[j]),
            })
            bank.at[i, "matched"] = True
            ledger.at[j, "matched"] = True
    columns = ["bank_date", "bank_description", "ledger_date",
               "ledger_description", "amount", "days_apart"]
    return pd.DataFrame(near_matches, columns=columns)


def reconcile(bank_path, ledger_path, bank_ending_balance, book_ending_balance,
              date_tolerance_days=3, near_match_days=10):
    bank = load_transactions(bank_path)
    ledger = load_transactions(ledger_path)
    bank, ledger = match_transactions(bank, ledger, date_tolerance_days)
    recording_errors = find_recording_errors(bank, ledger, date_tolerance_days)
    duplicates = find_duplicate_entries(ledger)
    near_matches = find_near_matches(bank, ledger, near_match_days)

    unmatched_bank = bank[~bank["matched"]]
    unmatched_ledger = ledger[~ledger["matched"]]

    # Items only in the books (outstanding checks, deposits in transit) adjust the bank balance.
    adjusted_bank = round(bank_ending_balance + unmatched_ledger["amount"].sum(), 2)
    # Items only on the bank statement, plus corrections of errors in the books,
    # adjust the book balance.
    adjusted_book = round(
        book_ending_balance
        + unmatched_bank["amount"].sum()
        + recording_errors["book_correction"].sum()
        + duplicates["book_correction"].sum(),
        2,
    )

    return {
        "unmatched_bank": unmatched_bank,
        "unmatched_ledger": unmatched_ledger,
        "recording_errors": recording_errors,
        "duplicates": duplicates,
        "near_matches": near_matches,
        "adjusted_bank": adjusted_bank,
        "adjusted_book": adjusted_book,
        "difference": round(adjusted_bank - adjusted_book, 2),
    }


def print_section(title, table):
    print(f"\n{title}")
    if table.empty:
        print("None found")
    else:
        print(table.to_string(index=False))


def print_report(result):
    cols = ["date", "description", "amount"]
    print_section("On bank statement but not in books (record these):",
                  result["unmatched_bank"][cols])
    print_section("In books but not yet on bank statement:",
                  result["unmatched_ledger"][cols])
    print_section("Probable recording errors (correct these in the books):",
                  result["recording_errors"])
    print_section("Possible duplicate entries in the books (reverse these):",
                  result["duplicates"])
    print_section("Matched, but dates are far apart (review these):",
                  result["near_matches"])
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
    parser.add_argument("--near-match-days", type=int, default=10,
                        help="maximum days apart to flag a same-amount pair for review")
    args = parser.parse_args()

    result = reconcile(args.bank_file, args.ledger_file,
                       args.bank_balance, args.book_balance,
                       args.tolerance, args.near_match_days)
    print_report(result)
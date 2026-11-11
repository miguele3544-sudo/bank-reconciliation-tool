# bank-reconciliation-tool

A Python tool that automates monthly bank reconciliation. It compares a bank statement with a company's general ledger, matches transactions that appear in both, identifies the reconciling items on each side, and calculates whether the adjusted balances agree.

## Why this project

Bank reconciliation is a routine but time-consuming accounting task. Reviewing transactions by hand is slow and error-prone, especially with high transaction volumes. This tool automates the matching and produces a clear summary of what needs attention.

## How it works

1. **Load** the bank statement and ledger from CSV files.
2. **Match** each bank transaction to a ledger entry with the same amount, dated within 3 days of each other (to allow for clearing time). Each ledger entry can only be matched once.
3. **Identify reconciling items:**
   - On the bank statement but not in the books (e.g., bank fees, interest earned): these need to be recorded in the ledger.
   - In the books but not yet on the bank statement (e.g., outstanding checks, deposits in transit): these adjust the bank balance.
4. **Calculate** the adjusted bank and book balances and report any difference.

## Project structure

```
bank-reconciliation-tool/
├── data/
│   ├── bank_statement.csv   # sample bank statement
│   └── ledger.csv           # sample general ledger
├── src/
│   └── reconcile.py         # matching and reconciliation logic
├── tests/
│   └── test_reconcile.py    # automated tests
├── requirements.txt
└── README.md
```

## Getting started

Requires Python 3.10 or later.

```
git clone https://github.com/miguele3544-sudo/bank-reconciliation-tool.git
cd bank-reconciliation-tool
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Mac/Linux
pip install -r requirements.txt
```

## Usage

```
python src/reconcile.py
```

### Input format

Both CSV files need these columns:

| Column        | Description                                     |
|---------------|-------------------------------------------------|
| `date`        | Transaction date (YYYY-MM-DD)                   |
| `description` | Short description of the transaction            |
| `amount`      | Positive for money in, negative for money out   |

### Example output

```
On bank statement but not in books (record these):
      date      description  amount
2026-10-28 Bank service fee  -15.0
2026-10-31  Interest earned    2.5

In books but not yet on bank statement:
      date            description  amount
2026-10-29 Check #102 - Utilities  -300.0
2026-10-31    Deposit - Gamma LLC   650.0

Adjusted bank balance: 5,987.50
Adjusted book balance: 5,987.50
Difference:            0.00
```

## Running tests

```
python -m pytest
```

The tests check the tool against sample data with a known, hand-calculated answer.

## Limitations and planned improvements

- Matching requires exact amounts; it does not yet handle one bank deposit covering several ledger entries.
- When multiple entries could match, the first eligible one is used.
- Planned: command-line inputs for file names and balances, Excel export of reconciling items, description-based matching, and a simple web interface.

## Data notice

All data in this repository is fictional. Never commit real bank statements or account information.

## License

MIT
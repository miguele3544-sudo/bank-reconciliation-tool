# Answer key: hard dataset (October 2026)

Files: `hard_bank.csv`, `hard_ledger.csv`, `hard_prior_outstanding.csv`

| Balance                         | Amount     |
|---------------------------------|-----------:|
| Bank balance, Sept 30           | 24,770.00  |
| Book balance, Sept 30           | 25,000.00  |
| **Bank balance, Oct 31**        | **23,210.37** |
| **Book balance, Oct 31**        | **20,717.60** |

The Sept 30 balances differ by the items in `hard_prior_outstanding.csv`
(1,800.00 deposit in transit less 1,570.00 of outstanding checks = 230.00).

## Correct reconciliation

| Bank side                                         | Amount       |
|---------------------------------------------------|-------------:|
| Balance per bank                                  | 23,210.37    |
| Add: deposit in transit, Quail Partners (Oct 31)  | 2,750.00     |
| Add: bank error, check 3114 is not ours           | 275.00       |
| Less: outstanding check #176 (stale, issued March)| (1,150.00)   |
| Less: outstanding check #301                      | (300.00)     |
| Less: outstanding check #309                      | (145.00)     |
| Less: outstanding check #310                      | (3,200.00)   |
| **Adjusted bank balance**                         | **21,440.37** |

| Book side                                              | Amount       |
|--------------------------------------------------------|-------------:|
| Balance per books                                      | 20,717.60    |
| Add: check #306 recorded as 850.00, cleared for 85.00 (slide error) | 765.00 |
| Add: Office Depot refund recorded as a payment (sign reversed)      | 150.00 |
| Add: check #308 recorded twice                         | 600.00       |
| Add: interest earned                                   | 4.12         |
| Less: check #305 recorded as 1,250.00, cleared for 1,520.00 (transposition) | (270.00) |
| Less: merchant processing fee netted from card deposit | (58.00)      |
| Less: NSF returned item fee                            | (30.00)      |
| Less: Geico insurance ACH not recorded                 | (389.00)     |
| Less: City Power bill recorded as 312.40, paid 318.75  | (6.35)       |
| Less: wire transfer fee                                | (25.00)      |
| Less: monthly service fee                              | (18.00)      |
| **Adjusted book balance**                              | **21,440.37** |

## Correct matches (no adjustment needed)

- Harbor Foods receipt.
- Juniper Vet and Ivy Dental: both 250.00. Juniper Vet (Oct 3) was entered late, so it appears
  out of date order in the ledger. Correct pairing is by name, not by first available.
- Check #302 cleared; check #301 (same 300.00 amount) is the one still outstanding.
- Kestrel, Lark, and Maple receipts (1,200 + 1,250 + 1,000) were deposited together as one
  3,450.00 bank deposit (one-to-many).
- Card sales of 2,000.00 arrived as a 1,942.00 deposit, net of a 58.00 processing fee.
- Payroll of 6,240.00 left the bank as two debits: 5,100.00 net pay and 1,140.00 payroll tax (many-to-one).
- Nova Corp: deposited Oct 22, returned NSF Oct 24, redeposited and cleared Oct 29. The -900 and
  +900 bank entries cancel; only the 30.00 fee needs recording.
- Osprey Ltd: same transaction, dated 5 days apart.
- Wire to Pelican Supply.
- Prior-month items: the Sept 30 deposit and check #188 cleared in October. Check #176 is still
  outstanding.

## Other findings to flag

- Check #176 was issued in March and is over six months old (stale-dated). Consider contacting the
  payee or voiding it.
- Check 3114 should be reported to the bank for correction.

## Proposed journal entries

| Account (debit / credit)                          | Debit   | Credit  |
|---------------------------------------------------|--------:|--------:|
| Cash / Postage expense (correct check #306)       | 765.00  | 765.00  |
| Cash / Supplies expense (reverse sign on refund: 2 x 75.00) | 150.00 | 150.00 |
| Cash / Repairs expense (reverse duplicate #308)   | 600.00  | 600.00  |
| Cash / Interest income                            | 4.12    | 4.12    |
| Supplies expense / Cash (correct check #305)      | 270.00  | 270.00  |
| Merchant fees expense / Cash                      | 58.00   | 58.00   |
| Bank fees expense / Cash (NSF fee)                | 30.00   | 30.00   |
| Insurance expense / Cash                          | 389.00  | 389.00  |
| Utilities expense / Cash                          | 6.35    | 6.35    |
| Bank fees expense / Cash (wire fee)               | 25.00   | 25.00   |
| Bank fees expense / Cash (service fee)            | 18.00   | 18.00   |

## What the current tool reports

Run with ending balances 23,210.37 and 20,717.60, the current tool reports an adjusted bank
balance of 20,327.97, an adjusted book balance of 20,557.97, and a difference of -230.00.
It pairs Juniper Vet with Ivy Dental, lists check #302 as outstanding instead of #301,
and has no way to account for the prior-month items, the one-to-many and many-to-one
matches, the net card deposit, or the NSF redeposit.

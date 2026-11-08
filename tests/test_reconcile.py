from src.reconcile import reconcile


def run():
    return reconcile("data/bank_statement.csv", "data/ledger.csv", 5637.50, 6000.00)


def test_finds_bank_only_items():
    result = run()
    assert sorted(result["unmatched_bank"]["amount"].tolist()) == [-15.00, 2.50]


def test_finds_book_only_items():
    result = run()
    assert sorted(result["unmatched_ledger"]["amount"].tolist()) == [-300.00, 650.00]


def test_balances_agree():
    result = run()
    assert result["difference"] == 0
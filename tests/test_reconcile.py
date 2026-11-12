from src.reconcile import classify_error, reconcile


def run():
    return reconcile("data/bank_statement.csv", "data/ledger.csv", 5637.50, 6000.00)


def run_tricky():
    return reconcile("data/tricky_bank.csv", "data/tricky_ledger.csv", 10823.00, 11000.00)


def run_hard():
    return reconcile("data/hard_bank.csv", "data/hard_ledger.csv", 23210.37, 20717.60)


def test_finds_bank_only_items():
    result = run()
    assert sorted(result["unmatched_bank"]["amount"].tolist()) == [-15.00, 2.50]


def test_finds_book_only_items():
    result = run()
    assert sorted(result["unmatched_ledger"]["amount"].tolist()) == [-300.00, 650.00]


def test_balances_agree():
    result = run()
    assert result["difference"] == 0


def test_classify_error():
    assert classify_error(-540.00, -450.00) == "Transposition error"
    assert classify_error(-85.00, -850.00) == "Slide error"
    assert classify_error(75.00, -75.00) == "Sign reversal"
    assert classify_error(-318.75, -312.40) is None   # wrong amount, not a 9-type error


def test_tricky_transposition():
    errors = run_tricky()["recording_errors"]
    assert errors["error_type"].tolist() == ["Transposition error"]
    assert errors["book_correction"].tolist() == [-90.00]


def test_tricky_duplicate_and_near_match():
    result = run_tricky()
    assert result["duplicates"]["book_correction"].tolist() == [300.00]
    assert result["near_matches"]["amount"].tolist() == [700.00]


def test_tricky_matches_answer_key():
    result = run_tricky()
    assert result["adjusted_bank"] == 9973.00
    assert result["adjusted_book"] == 9973.00


def test_hard_recording_errors():
    errors = run_hard()["recording_errors"]
    assert sorted(errors["error_type"].tolist()) == [
        "Sign reversal", "Slide error", "Transposition error"]
    assert sorted(errors["book_correction"].tolist()) == [-270.00, 150.00, 765.00]


def test_hard_duplicate():
    assert run_hard()["duplicates"]["book_correction"].tolist() == [600.00]
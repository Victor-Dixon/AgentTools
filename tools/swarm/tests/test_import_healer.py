from tools.swarm.tests.validate_import_healer import run_validation


def test_import_healer_validation() -> None:
    assert run_validation() == 0

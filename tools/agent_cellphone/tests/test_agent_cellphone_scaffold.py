from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_manifest_exists():
    assert (ROOT / "manifest.yaml").exists()

def test_cli_exists():
    cli = ROOT / "bin" / "agent-cellphone"
    assert cli.exists()
    assert cli.stat().st_mode & 0o111

def test_import_manifests_exist():
    assert (ROOT / "imports" / "Agent_Cellphone.files.txt").exists()
    assert (ROOT / "imports" / "Agent_Cellphone_V2_Repository.files.txt").exists()

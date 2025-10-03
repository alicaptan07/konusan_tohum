import importlib

def test_imports():
    assert importlib.import_module("konusan_tohum")

def test_cli_smoke(monkeypatch, capsys):
    from konusan_tohum.cli import main
    monkeypatch.setenv("TOHUM_FAKE", "1")  # örnek bayrak
    main()
    out = capsys.readouterr().out
    assert "TOHUM" in out  # initialize_system çıktı veriyor

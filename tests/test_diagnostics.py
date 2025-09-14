from diagnostics.system_tester import SystemTester

def test_system_tester():
    dummy_modules = {"mod1": object(), "mod2": object()}
    tester = SystemTester(dummy_modules)
    results = tester.run_basic_tests()
    assert all(results.values())
    print("✅ SystemTester test edildi.")
class SystemTester:
    def __init__(self, modules):
        self.modules = modules

    def run_basic_tests(self):
        results = {}
        for name, mod in self.modules.items():
            try:
                # Modül ping fonksiyonu varsa çalıştır
                if hasattr(mod, "ping"):
                    result = mod.ping() == "OK"
                else:
                    # ping yoksa modülün varlığı yeterli
                    result = mod is not None
                results[name] = result
            except Exception:
                results[name] = False
        return results
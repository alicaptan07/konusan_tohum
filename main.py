from core.config_manager import ConfigError, ConfigManager
from core.module_loader import ModuleLoadError, ModuleLoader
from diagnostics.system_tester import SystemTester

def initialize_system():
    print("🌱 Konuşan Tohum v1.0 başlatılıyor...")

    # Ayarları yükle
    try:
        config = ConfigManager()
        settings = config.load_config()
        active_modules = config.get_active_modules()
    except ConfigError as exc:
        print(f"❌ Yapılandırma hatası: {exc}")
        raise SystemExit(1) from exc

    # Modülleri yükle
    loader = ModuleLoader(active_modules)
    try:
        loader.load_all()
    except ModuleLoadError as exc:
        print("❌ Modüller yüklenirken hatalar oluştu:")
        for error in exc.errors:
            print(f" - {error}")
        raise SystemExit(1) from exc
    modules = loader.get_all_modules()

    # Modül testi
    tester = SystemTester(modules)
    test_results = tester.run_basic_tests()

    print("✅ Sistem hazır. Modül durumu:")
    for name, result in test_results.items():
        print(f" - {name}: {'✅' if result else '❌'}")

    # Örnek mesaj işleme (ileride chat_api ile bağlanacak)
    if "dialog.response_generator" in modules:
        response = modules["dialog.response_generator"].generate("selam", {}, [], user_id="test_user")
        print(f"\n🗣 Yanıt: {response}")

# Doğrudan çalıştırıldığında sistem başlatılır
if __name__ == "__main__":
    initialize_system()
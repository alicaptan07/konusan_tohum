"""Konuşan Tohum başlangıç yürütücüsü, çekirdek konfigürasyonu yükleyip modül altyapısını ayağa kaldırır ve sistem sağlığını doğrulayan bir örnek çalışma akışı sunar."""

from konusan_tohum.core.config_manager import ConfigManager
from konusan_tohum.core.module_loader import ModuleLoader
from konusan_tohum.diagnostics.system_tester import SystemTester

def initialize_system():
    print("🌱 Konuşan Tohum v1.0 başlatılıyor...")

    # Ayarları yükle
    config = ConfigManager()
    settings = config.load_config()
    active_modules = config.get_active_modules()

    # Modülleri yükle
    loader = ModuleLoader(active_modules)
    loader.load_all()
    modules = loader.get_all_modules()

    # Modül testi
    tester = SystemTester(modules)
    test_results = tester.run_basic_tests()

    print("✅ Sistem hazır. Modül durumu:")
    for name, result in test_results.items():
        print(f" - {name}: {'✅' if result else '❌'}")

    # Örnek mesaj işleme (ileride chat_api ile bağlanacak)
    module_key = "konusan_tohum.dialog.response_generator"
    if module_key in modules:
        response = modules[module_key].generate("selam", {}, [], user_id="test_user")
        print(f"\n🗣 Yanıt: {response}")

# Doğrudan çalıştırıldığında sistem başlatılır
if __name__ == "__main__":
    initialize_system()

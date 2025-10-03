from pathlib import Path
import sys
from typing import Optional

from src.konusan_tohum.core.config_manager import ConfigManager
from src.konusan_tohum.core.module_loader import ModuleLoader
from src.konusan_tohum.diagnostics.system_tester import SystemTester
from src.konusan_tohum.dialog.response_generator import generate_response, FallbackResponseGenerator

SETTINGS_PATH = Path("src/konusan_tohum/settings/settings.yaml")

def initialize_system() -> Optional[str]:
    # 1) Config yükle
    if not SETTINGS_PATH.exists():
        print(f"[WARN] Ayar dosyası bulunamadı: {SETTINGS_PATH}. Fallback ile devam edilecek.")
        config = {}
    else:
        config = ConfigManager(SETTINGS_PATH).load()

    # 2) Modüller
    loader = ModuleLoader(config=config)
    try:
        loader.load_active_modules()
    except Exception as e:
        print(f"[WARN] Modül yüklemede hata: {e}. Fallback ile devam.")
    
    # 3) Sağlık kontrolü (yumuşak)
    try:
        SystemTester(config=config).run_basic_checks()
    except Exception as e:
        print(f"[WARN] Sistem testi uyarı verdi: {e}")

    # 4) Örnek yanıt
    try:
        text = generate_response("Merhaba!", config=config)
    except Exception:
        print("[INFO] NLP bağımlılıkları yok/çöktü; FallbackResponseGenerator devrede.")
        text = FallbackResponseGenerator().generate("Merhaba!")

    print(f"[TOHUM] {text}")
    return text

if __name__ == "__main__":
    try:
        initialize_system()
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"[FATAL] Başlatma hatası: {e}")
        sys.exit(1)

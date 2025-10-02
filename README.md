# Konuşan Tohum

Konuşan Tohum, sohbet tabanlı bir asistan oluşturmak için yapı taşları sunan modüler bir Python paketidir. Sistem; yapılandırma yönetimi, modül yükleme, teşhis, diyalog üretimi, hafıza, güvenlik ve dış servis entegrasyonları gibi katmanlarıyla etkileşimli deneyimler geliştirmeyi kolaylaştırır. 

## Proje Amacı / Project Purpose
- **Türkçe:** Yapay zekâ tabanlı sohbet deneyimleri geliştirmek için yeniden kullanılabilir bileşenler, testler ve örnek akışlar sağlamak.
- **English:** Provide reusable components, tests, and example flows for building AI-driven conversational experiences.

## Kurulum / Installation
1. Python 3.9 veya üstü bir sürüm kurduğunuzdan emin olun.
2. Depoyu klonlayın ve dizine geçin:
   ```bash
   git clone <repo-url>
   cd konusan_tohum
   ```
3. (İsteğe bağlı) Sanal ortam oluşturun:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   ```
4. Temel bağımlılıkları kurun:
   ```bash
   pip install -e .
   ```
5. Testleri de çalıştırmak istiyorsanız ek bağımlılıkları yükleyin:
   ```bash
   pip install -e .[tests]
   ```
6. NLP modellerini kullanmayı planlıyorsanız ek olarak `pip install -e .[nlp]` komutunu çalıştırın.

## Bağımlılıklar / Dependencies
- Zorunlu bağımlılık: [PyYAML](https://pyyaml.org) yapılandırma dosyalarını okumak için gereklidir.
- İsteğe bağlı bağımlılıklar:
  - `requests` (API entegrasyonları için `api` ekstra kümesi)
  - `transformers` ve `torch` (NLP modülleri için `nlp` ekstra kümesi)
  - `pytest` (testleri çalıştırmak için `tests` ekstra kümesi)

## Mimari Genel Bakış / Architectural Overview
- `main.py`: Yapılandırmayı yükler, aktif modülleri dinamik olarak çalıştırır ve sistem sağlık kontrolünü gerçekleştirir. Başlatma sonunda örnek bir yanıt üretir.
- `src/konusan_tohum/core/`: `ConfigManager` YAML tabanlı ayarları okur ve aktif modül listesini döndürür; `ModuleLoader` modülleri import eder ve isteğe bağlı `initialize` fonksiyonlarını çağırır.
- `src/konusan_tohum/diagnostics/`: `SystemTester`, modüllerin erişilebilirliğini doğrulamak için hafif denetimler uygular.
- `src/konusan_tohum/dialog/`: `response_generator.py` kural tabanlı yanıtları ve Hugging Face `pipeline` desteğiyle metin üretimini yönetir; dış bağımlılıklar mevcut değilse otomatik olarak geriye dönüş (fallback) üretici kullanılır.
- `src/konusan_tohum/memory/`: Kullanıcı hafızasını JSON dosyalarında saklar, geçmişi günceller ve maksimum uzunluğu yönetir.
- `src/konusan_tohum/security/`: Kimlik doğrulama, izin ve veri temizleme araçlarını içerir.
- `src/konusan_tohum/integration/`: Harici API'ler, veri kaynakları ve web aramalarını entegre etmek için bağlayıcı modüller sunar.
- `src/konusan_tohum/settings/settings.yaml`: API sağlayıcıları, model isimleri, hafıza dizini ve GUI özellikleri gibi sistem ayarlarını merkezi olarak tanımlar.

## Yapılandırma / Configuration
`ConfigManager`, `settings/settings.yaml` dosyasını yükleyerek hangi modüllerin aktif olacağını ve modellerin nasıl seçileceğini belirler. Dosyada API anahtarlarını, model adlarını ve hafıza yolunu güncelleyerek sistemi ihtiyaçlarınıza göre özelleştirebilirsiniz.

## Testleri Çalıştırma / Running Tests
Tüm birim testlerini çalıştırmak için proje kök dizininde aşağıdaki komutu kullanın:
```bash
pytest
```
Testler; diyalog, hafıza, güvenlik, entegrasyon ve tanılama katmanlarını kapsayan örnek senaryolar içerir.

## Temel Kullanım / Basic Usage
### Komut Satırından / From the Command Line
```bash
python main.py
```
Komut, sistemi başlatır, aktif modülleri yükler ve kısa bir örnek diyalog yanıtı üretir.

### Python İçinden / From Python Code
```python
from main import initialize_system

initialize_system()
```
Bu çağrı, CLI komutuyla aynı başlangıç akışını programatik olarak tetikler.

## Katkıda Bulunma / Contributing
- Pull Request açmadan önce `pytest` komutunu çalıştırın.
- Yeni özellikler eklerken uygun modül dizininde yer alan testleri güncellediğinizden emin olun.

## Lisans / License
Bu depo için lisans bilgisi henüz eklenmemiştir. Kurumsal gereksinimlerinize göre lisans dosyası oluşturabilirsiniz.

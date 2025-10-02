# Konuşan Tohum

Konuşan Tohum, çevrimdışı çalışabilen ve gerektiğinde bulut sağlayıcılarına
bağlanabilen modüler bir sohbet asistanıdır.  Depo; yapılandırma yönetimi,
metin üretimi, entegrasyon bağlayıcıları ve hafif bir GUI içerir.  Bu belge
paketlenmiş kurulumu, test sürecini ve temel çalışma akışlarını özetler.

## Kurulum

Paketleme düzenlemesinden sonra proje yerel geliştirme ortamına ``pip`` ile
edilebilir kurulum şeklinde eklenebilir:

```bash
pip install -e .
```

Komut, bağımlılıkların kurulumunu üstlenirken çekirdek modüllerin
(``core/config_manager.py`` ve ``dialog/response_generator.py``) yapılandırma
farklılıklarına karşı doğrulama adımlarını çalıştırmasına izin verir.  YAML
ayar dosyası ``settings/settings.yaml`` altında bulunur; ``ConfigManager``
(ve ``modules.active`` anahtarı) hangi entegrasyonların yükleneceğini belirler.

## Günlükleme

Modül yükleyicisi Python'un standart ``logging`` altyapısını kullanır.  CLI ya
da GUI oturumlarını başlatmadan önce ortam değişkenleri veya ayrı bir
``logging.conf`` dosyası üzerinden kayıt seviyesini güncelleyebilirsiniz.
Sürekli entegrasyon (CI) ortamlarında ``ModuleLoader`` hatalı modülleri rapor
ederek modüler yapılandırmanın doğrulandığını gösterir.

## Test Süreci

Projenin CI süreci ``pytest`` ile testlerin çalıştırılmasına dayanır.  Tüm
birim ve entegrasyon testlerini aşağıdaki komutla başlatın:

```bash
pytest
```

Testler, çevrimdışı durumlarda deterministik stub verileri döndüren entegrasyon
modüllerini (``integration`` klasörü) ve yapılandırma validasyonunu doğrular.
Bu yaklaşım, ağ bağlantısı ve üçüncü taraf API anahtarlarının bulunmadığı
ortamlarda bile aynı sonuçların elde edilmesini sağlar.

## GUI Başlatma

Grafik arayüzü başlatmak için kök dizinden aşağıdaki komutu kullanın:

```bash
python run_chat_gui.bat
```

Komut dosyası Windows üzerinde ``tkinter`` tabanlı GUI'yi başlatır.  Linux veya
macOS gibi platformlarda aynı komutu ``python`` yorumlayıcısıyla çalıştırmak
script içindeki ``main`` fonksiyonunu tetikleyerek eşdeğer arayüzü açacaktır.

## Yapılandırma ve Konfigürasyon Notları

- ``settings/settings.yaml`` dosyasındaki ``modules.active`` listesi hangi
  entegrasyonların (``integration/ai_connector.py``, ``integration/web_search_mod.py``
  vb.) yükleneceğini kontrol eder.
- ``api_keys`` ve ``models`` ad alanları, çevrimiçi sağlayıcılar (OpenAI veya
  OpenRouter) ile kullanılacak kimlik bilgilerini ve model adlarını belirtir.
- ``ConfigManager`` hatalı YAML dosyalarını güvenli şekilde işler ve CI
  boru hattının yapılandırma doğrulamasını destekler.
- Günlükler, ``ModuleLoader`` ve entegrasyon bağlayıcıları aracılığıyla farklı
  yürütme yollarını rapor ederek sorun giderme ve tekrarlanabilirlik sağlar.

Bu adımları izlemek, yerel geliştirme ile CI ortamlarının aynı yapılandırma
ve test disiplinine sahip olmasını garanti eder.

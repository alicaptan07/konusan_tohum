# Konuşan Tohum

## API Yardımcı Fonksiyonu

`call_api` yardımcı fonksiyonu, ağ bağlantısı veya `requests` kütüphanesi
bulunmadığında bile deterministik bir stub döndürerek testlerin güvenli bir
şekilde çalışmasını sağlar. Fonksiyon artık aşağıdaki yeni parametrelerle
konfigüre edilebilir:

- **timeout**: Her deneme için `requests.get` çağrısına iletilen zaman aşımı
  değeri. Varsayılan değer 5 saniyedir ve önceki davranış korunur.
- **retries**: Hata durumlarında yapılacak ek deneme sayısı. Varsayılan değer
  0'dır, yani yalnızca tek bir deneme yapılır.
- **backoff_factor**: Üstel gecikme için temel değer. Her başarısız denemenin
  ardından `backoff_factor * (2 ** deneme_indeksi)` kadar beklendikten sonra
  yeniden denenir.

Belirtilen tekrarlar başarısız olsa bile fonksiyon deterministik stub cevabını
vermeye devam eder.

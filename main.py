import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import serial
import time
import os

# SINIF YAPISI: Kodu daha düzenli hale getirmek için tüm fonksiyonları bir sınıf içinde topluyoruz.
class KonusanTohum:
    def __init__(self, port="COM3", baud_rate=9600):
        """Yapıcı metot: Program başlarken gerekli nesneleri oluşturur."""
        self.r = sr.Recognizer()
        self.ser = None  # Seri port nesnesini başlangıçta boş olarak tanımlıyoruz.
        self.port = port
        self.baud_rate = baud_rate
        # Komutları ve karşılık gelen verileri bir sözlükte topluyoruz. Bu, if/elif zincirini ortadan kaldırır.
        self.komutlar = {
            "ışığı aç": "1",
            "ışık aç": "1",
            "aç": "1",
            "ışığı kapat": "0",
            "ışık kapat": "0",
            "kapat": "0"
        }

    def seri_port_ac(self):
        """Seri portu açmayı dener ve başarılı olup olmadığını bildirir."""
        try:
            # Seri portu verilen port ve baud hızı ile açıyoruz.
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            print(f"Seri port ({self.port}) başarıyla açıldı.")
            time.sleep(2) # Arduino'nun hazır olması için kısa bir bekleme süresi ekliyoruz.
            return True
        except serial.SerialException as e:
            # Port açılamazsa (örn: takılı değilse veya başka bir program kullanıyorsa) hata mesajı veriyoruz.
            print(f"HATA: Seri port açılamadı: {e}")
            return False

    def seri_port_kapat(self):
        """Seri port açıksa güvenli bir şekilde kapatır."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Seri port kapatıldı.")

    def konus(self, metin):
        """Verilen metni sesli olarak okur."""
        print(f"Asistan: {metin}")
        try:
            tts = gTTS(text=metin, lang="tr")
            # Ses dosyasını geçici olarak kaydediyoruz
            dosya_adi = "response.mp3"
            tts.save(dosya_adi)
            playsound(dosya_adi)
            os.remove(dosya_adi) # Ses dosyasını çaldıktan sonra siliyoruz
        except Exception as e:
            print(f"Seslendirme hatası: {e}")

    def komut_dinle(self):
        """Mikrofondan ses dinler ve metne çevirir."""
        with sr.Microphone() as source:
            print("Dinliyorum...")
            self.r.adjust_for_ambient_noise(source) # Gürültü ayarı
            audio = self.r.listen(source)

        try:
            # Google'ın konuşma tanıma servisini kullanarak sesi metne çeviriyoruz.
            ses_metni = self.r.recognize_google(audio, language="tr-TR").lower()
            print(f"Siz: {ses_metni}")
            return ses_metni
        except sr.UnknownValueError:
            # Konuşma anlaşılamadığında bu blok çalışır.
            self.konus("Ne dediğini anlayamadım, tekrar eder misin?")
            return None
        except sr.RequestError:
            # İnternet bağlantısı veya servis hatası olduğunda bu blok çalışır.
            self.konus("Sistemsel bir hata oluştu, internet bağlantını kontrol et.")
            return None

    def komut_isleme(self, komut_metni):
        """Alınan sesli komutu işler ve Arduino'ya gönderilecek veriyi bulur."""
        if not komut_metni:
            return None, None

        for anahtar_kelime, veri in self.komutlar.items():
            if anahtar_kelime in komut_metni:
                yanit_metni = "Işık açılıyor." if veri == "1" else "Işık kapatılıyor."
                return veri, yanit_metni
        
        return None, "Bu komutu anlayamadım."

    def baslat(self):
        """Programın ana döngüsünü başlatır."""
        # Seri portu açmayı deniyoruz, başarılı değilse programdan çıkıyoruz.
        if not self.seri_port_ac():
            return # Port açılmazsa fonksiyonu sonlandır.

        self.konus("Merhaba, nasıl yardımcı olabilirim?")

        try:
            # ANA DÖNGÜ: Program burada sürekli çalışır.
            while True:
                # 1. Adım: Komutu dinle
                ses_metni = self.komut_dinle()

                # 2. Adım: Dinlenen komutu işle
                if ses_metni:
                    veri, yanit = self.komut_isleme(ses_metni)

                    # 3. Adım: Geçerli bir komut varsa Arduino'ya gönder
                    if veri:
                        self.konus(yanit)
                        self.ser.write(veri.encode())
                        print(f"Arduino'ya gönderilen veri: {veri}")
                    else:
                        # Anlaşılmayan komutlar için kullanıcıyı bilgilendir.
                        self.konus(yanit)
                
                # Her döngü arasında kısa bir bekleme süresi.
                time.sleep(1)

        except KeyboardInterrupt:
            # Kullanıcı Ctrl+C ile programı durdurduğunda bu blok çalışır.
            print("\nProgram sonlandırılıyor.")
            self.konus("Görüşmek üzere.")
        finally:
            # Program ne şekilde biterse bitsin (hata veya normal kapanış), seri portu güvenle kapatır.
            self.seri_port_kapat()


# --- PROGRAMIN BAŞLANGIÇ NOKTASI ---
if __name__ == "__main__":
    proje = KonusanTohum(port="COM3") # Arduino'nuzun bağlı olduğu COM portunu buraya yazın
    proje.baslat()

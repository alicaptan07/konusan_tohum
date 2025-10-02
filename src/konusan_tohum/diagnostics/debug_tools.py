"""Konuşan Tohum tanılama izleyicileri, modül davranışını görünür kılmak için hafif izleme yardımcıları sağlar."""

def trace(module_name):
    print(f"🔍 Modül izleniyor: {module_name}")
    # Geliştirici için izleme noktası
    return True

def ping():
    return "OK"

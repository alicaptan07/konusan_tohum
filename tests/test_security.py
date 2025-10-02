"""Konuşan Tohum güvenlik yardımcılarının veri temizleme süreçlerini sınayan testler."""

from konusan_tohum.security.data_sanitizer import sanitize

def test_data_sanitizer():
    clean = sanitize("<script>alert('x')</script>")
    assert "<script>" not in clean
    print("✅ DataSanitizer test edildi.")

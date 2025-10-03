from konusan_tohum.dialog.response_generator import FallbackResponseGenerator

def test_fallback_generates_text():
    g = FallbackResponseGenerator()
    assert isinstance(g.generate("selam"), str)

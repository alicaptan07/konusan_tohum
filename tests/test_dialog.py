from dialog.response_generator import generate

def test_response_generator():
    response = generate("greeting", {}, [])
    assert isinstance(response, str)
    print("✅ ResponseGenerator test edildi.")
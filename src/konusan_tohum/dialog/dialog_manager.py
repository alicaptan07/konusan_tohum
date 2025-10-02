# dialog/dialog_manager.py

from konusan_tohum.dialog.response_generator import generate_response
from konusan_tohum.memory.memory_updater import update_memory


def handle_message(user_id: str, message: str) -> str:
    """
    Kullanıcıdan gelen mesajı işler:
    - Yanıt üretir
    - Hafızaya kaydeder
    - Yanıtı döner
    """
    response = generate_response(message)
    update_memory(user_id, message, response)
    return response


if __name__ == "__main__":
    # Test
    user = "ali"
    msg = "Bugün hava nasıl?"
    print("Kullanıcı:", msg)
    print("Tohum AI:", handle_message(user, msg))

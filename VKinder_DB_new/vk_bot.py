import json
import vk_api
from random import randrange
from vk_api.longpoll import VkLongPoll, VkEventType
from config import group_token

vk_session = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk_session)


def get_but(text, color):
    return {
        "action": {
            "type": "text",
            "payload": "{\"button\": \"" + "1" + "\"}",
            "label": f"{text}"
        },
        "color": f"{color}"
    }


keyboard = {
    "one_time": False,
    "buttons": [
        [get_but('Начать поиск', 'secondary')],
        [get_but('Далее', 'secondary')]
    ]
}
keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
keyboard = str(keyboard.decode('utf-8'))

def sender(user_id, text):
    vk_session.method('messages.send', {'user_id': user_id, 'message': text, 'random_id': randrange(10 ** 7), 'keyboard': keyboard})

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text.lower()
            if request == "привет":
                sender(event.user_id, f"Добро пожаловать {event.user_id} в VKinder!")
            elif request == "начать поиск":
                sender(event.user_id, f"Нашел для тебя интересную пару, нажми - 'Далее'!")
            elif request == "Далее":
                break
                
            else:
                sender(event.user_id, "Повторите ваш запрос!")

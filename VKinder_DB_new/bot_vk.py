import json
import vk_api
from random import randrange
from vk_api.longpoll import VkLongPoll, VkEventType
from VKinder_get_and_filling.tokens_vk import token_gr, token
from VKinder_get_and_filling.VKinder_filling_db import filling_db
from VKinder_DB_folder.VKinder_DB import get_offer, get_user, add_favorite, get_favorite

vk_session = vk_api.VkApi(token=token_gr)
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

one_time = True
keyboard = {
    "one_time": one_time,
    "buttons": [
        [get_but('Начать поиск', 'secondary')],
        [get_but('Далее', 'secondary')],
        [get_but('Добавить в избранное', 'secondary')],
        [get_but('Показать избранное', 'secondary')]

    ]
}
keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
keyboard = str(keyboard.decode('utf-8'))

def sender(user_id, text):
    vk_session.method('messages.send',
                      {'user_id': user_id, 'message': text, 'random_id': randrange(10 ** 7), 'keyboard': keyboard})

counter = 0
for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text.lower()

            if request == "привет":
                sender(event.user_id, f"Добро пожаловать {event.user_id} в VKinder!")

            elif request == "начать поиск":
                sender(event.user_id, f"Подождите")
                if event.user_id not in get_user():
                    filling_db(token, event.user_id)

                list_all_offer = get_offer(event.user_id)
                print(list_all_offer)
                iter_all_offer = iter(list_all_offer)
                sender(event.user_id, f"Нашел для тебя интересную пару, нажми - 'Далее'!")
                counter = 0

            elif request == "далее":

                if len(list_all_offer) == counter:
                    sender(event.user_id, f"""
                    Это все результаты(
                    Начни заново ;)
                    """)
                    continue

                print(counter)
                offer_1 = next(iter_all_offer)
                sender(event.user_id, f"""
                {offer_1[1]} {offer_1[2]}
                https://vk.com/id{offer_1[0]}
                """)
                counter += 1

            elif request == "добавить в избранное":
                add_favorite(event.user_id, offer_1[0])
                sender(event.user_id, f"{offer_1[1]} добавлен в избранное")

            elif request == "показать избранное":
                favorites_list = get_favorite(event.user_id)
                for i in favorites_list:
                    sender(event.user_id, f"""
                                {i[1]} {i[2]}
                                https://vk.com/id{i[0]}
                                """)

            else:
                sender(event.user_id, "Повторите ваш запрос!")
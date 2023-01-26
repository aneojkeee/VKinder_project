import json
import vk_api
from random import randrange
from vk_api.longpoll import VkLongPoll, VkEventType
from VKinder_get_and_filling.tokens_vk import token_gr, token
from VKinder_get_and_filling.VKinder_filling_db import filling_db
from VKinder_DB_folder.VKinder_DB import get_offer, get_user, add_favorite, get_favorite, create_db

vk_session = vk_api.VkApi(token=token_gr)
longpoll = VkLongPoll(vk_session)


def get_but(text, color):
    """
    Данная функция предназначена для взаимодействия пользователя с интерфейсом приложения.
    :param text: передает текст кнопки
    :param color: передает цвет кнопки
    :return: возвращает текст и цвет кнопки
    """
    return {
        "action": {
            "type": "text",
            "payload": "{\"button\": \"" + "1" + "\"}",
            "label": f"{text}"
        },
        "color": f"{color}"
    }

keyboard = {
    "one_time": True,
    "buttons": [
        [get_but('Начать поиск', 'secondary')],
        [get_but('Далее', 'secondary')],
        [get_but('Добавить в избранное', 'secondary')],
        [get_but('Показать избранное', 'secondary')]

    ]
}
keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
keyboard = str(keyboard.decode('utf-8'))

def sender(user_id, text, attachment=None):
    post = {'user_id': user_id,
            'message': text,
            'random_id': randrange(10 ** 7),
            'attachment': attachment,
            'keyboard': keyboard}

    if attachment != None:
        post['attachment'] = attachment

    vk_session.method('messages.send', post)

counter = 0
for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text.lower()

            if request == "привет":
                sender(event.user_id, f"Добро пожаловать {event.user_id} в VKinder!")

            elif request == "начать поиск":
                try:
                    sender(event.user_id, f"Подождите")
                    if event.user_id not in get_user():
                        filling_db(token, event.user_id)

                    list_all_offer = get_offer(event.user_id)
                    print(list_all_offer)
                    iter_all_offer = iter(list_all_offer)
                    sender(event.user_id, f"Нашел для тебя интересную пару, нажми - 'Далее'!")
                    counter = 0
                except:
                    create_db()
                    sender(event.user_id, f"Пожалуйста нажмите ещё раз Начать поиск")
                    continue

            elif request == "далее":

                try:
                    if len(list_all_offer) == counter:
                        sender(event.user_id, f"""
                        Это все результаты(
                        Начни заново ;)
                        """)
                        continue

                    print(counter)
                    offer_1 = next(iter_all_offer)
                    att = [f"photo{offer_1[0]}_{i}" for i in offer_1[6]]
                    print(f"{','.join(att)}")
                    sender(event.user_id, f"""
                    {offer_1[1]} {offer_1[2]}
                    \nhttps://vk.com/id{offer_1[0]}
                    """, ','.join(att))
                    counter += 1
                except NameError:
                    sender(event.user_id, f"Нажмите сначала начать поиск!")
                    continue

            elif request == "добавить в избранное":
                try:
                    add_favorite(event.user_id, offer_1[0])
                    sender(event.user_id, f"{offer_1[1]} добавлен в избранное")
                except NameError:
                    sender(event.user_id, f"Нажмите сначала и посмотрите кто приглянулся ;)!")
                    continue

            elif request == "показать избранное":
                favorites_list = get_favorite(event.user_id)
                if not favorites_list:
                    sender(event.user_id, "Вы ещё никого не добавили в избранное (")
                for i in favorites_list:
                    sender(event.user_id, f"""
                                {i[1]} {i[2]}
                                https://vk.com/id{i[0]}
                                """)

            else:
                sender(event.user_id, "Повторите ваш запрос!")
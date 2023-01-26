from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from VKinder_get_and_filling.tokens_vk import token_gr, token
from VKinder_get_and_filling.VKinder_filling_db import filling_db
from VKinder_DB_folder.VKinder_DB import get_offer, get_user, add_favorite, get_favorite, add_black_list, create_db


vk_session = vk_api.VkApi(token=token_gr)
longpoll = VkLongPoll(vk_session)
counter = 0
create_db()


def sender(user_id, text, attachment=None):
    """
        Данная функция обеспечивает взаимодействие приложения с пользователем.
    :param user_id: id пользователя
    :param text: текст сообщения пользователя
    :param attachment: медиафайл к сообщению
    """
    keyboard = VkKeyboard()
    keyboard.add_button('Начать поиск', VkKeyboardColor.PRIMARY)
    keyboard.add_button('Далее', VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Добавить в черный список', VkKeyboardColor.NEGATIVE)
    keyboard.add_button('Добавить в избранное', VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('Показать избранное', VkKeyboardColor.PRIMARY)

    post = {'user_id': user_id,
            'message': text,
            'random_id': randrange(10 ** 7),
            'attachment': attachment,
            'keyboard': keyboard.get_keyboard()}

    if attachment is not None:
        post['attachment'] = attachment
    vk_session.method('messages.send', post)


for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text.lower()

            if request == 'привет':
                sender(event.user_id, 'Добро пожаловать в VKinder!')

            elif request == 'начать поиск':
                try:
                    sender(event.user_id, 'Подождите...')
                    if event.user_id not in get_user():
                        filling_db(token, event.user_id)
                    list_all_offer = get_offer(event.user_id)
                    iter_all_offer = iter(list_all_offer)
                    sender(event.user_id, 'Нашел для тебя интересную пару, нажми - "Далее"!')
                    counter = 0
                except NameError:
                    sender(event.user_id, 'Пожалуйста нажмите ещё раз "Начать поиск"')
                    continue

            elif request == 'далее':
                try:
                    if len(list_all_offer) == counter:
                        sender(event.user_id, 'Это все результаты( Начни заново ;)')
                        continue
                    offer_1 = next(iter_all_offer)
                    att = [f'photo{offer_1[0]}_{i}' for i in offer_1[6]]
                    sender(event.user_id, f'{offer_1[1]} {offer_1[2]}\nhttps://vk.com/id{offer_1[0]}', ','.join(att))
                    counter += 1
                except NameError:
                    sender(event.user_id, 'Нажмите "Начать поиск"!')
                    continue

            elif request == 'добавить в избранное':
                try:
                    add_favorite(event.user_id, offer_1[0])
                    sex_text = ''
                    if offer_1[3] == 1:
                        sex_text = 'а'
                    sender(event.user_id, f'{offer_1[1]} добавлен{sex_text} в избранное')
                except NameError:
                    sender(event.user_id, 'Начните сначала и посмотрите, кто приглянулся ;)!')
                    continue

            elif request == 'добавить в черный список':
                try:
                    add_black_list(event.user_id, offer_1[0])
                    sex_text = ''
                    if offer_1[3] == 1:
                        sex_text = 'а'
                    sender(event.user_id, f'{offer_1[1]} добавлен{sex_text} в черный список')
                except NameError:
                    sender(event.user_id, 'Нажмите сначала и посмотрите кто приглянулся ;)!')
                    continue

            elif request == 'показать избранное':
                fovorite_str = ''
                favorites_list = [f'{el[1]} {el[2]} https://vk.com/id{el[0]}\n' for el in get_favorite(event.user_id)]
                for el in favorites_list:
                    fovorite_str = fovorite_str + str(el)
                if not favorites_list:
                    sender(event.user_id, 'Вы ещё никого не добавили в избранное (')

                sender(event.user_id, fovorite_str)

            else:
                sender(event.user_id, 'Повторите ваш запрос!')

from VKinder_DB_folder.VKinder_DB import add_user, add_offer, add_photo
from VKinder_get_datainfo import Vkinder, AllInfo
from tokens_vk import token_gr, token


def convert_in_int(data_str):

    """
    :param data_str: На вход принимается дата в строковом формате. Пример '10.10.2023'
    :return: Возвращает дату в числовом формате. Пример 10102023
    """

    return int(''.join(data_str.split('.')))


def filling_db(token, user_id):

    """
    Данная функция получает данные от VK Api и загружает их в базу данных
    :param token: Токен VK Api
    :param user_id: id пользователя, который пишет нам в бот

    """

    vkinder = Vkinder(token, user_id)
    vkinder.activate_get_search_photos()
    user_info = AllInfo.dict_get_user
    offer_info = AllInfo.dict_search_user
    photos_info = AllInfo.dict_photos_search_user

    add_user(user_id, user_info['first_name'], user_info['sex'], convert_in_int(user_info['b_date']), user_info['city_name'])

    for dict in offer_info:
        add_offer(user_id, dict['id_offer'], dict['first_name'], dict['last_name'], dict['sex'], convert_in_int(dict['bdate']), dict['city'])

    for dict_p in photos_info:
        add_photo(dict_p["id_offer"], dict_p['top_photos'])


filling_db(token, 1)
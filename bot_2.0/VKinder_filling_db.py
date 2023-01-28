from VKinder_DB_folder.VKinder_DB import add_user, add_offer, add_photo, add_interest
from VKinder_get_and_filling.VKinder_get_data import VKinder


def filling_db(token, user_id):
    """
        Данная функция получает данные от VK API и загружает их в БД
    :param token: Токен VK API
    :param user_id: id пользователя, который пишет в бот
    """
    vkinder = VKinder(token, user_id)
    user_info, offer_info, photos_info = vkinder.activate_get_search_photos()

    add_user(vk_user_id=user_id, first_name=user_info['first_name'], sex=user_info['sex'], age=user_info['b_date'], city=user_info['city_name'])
    for interest in user_info['interests']:
        if len(interest) > 0:
            for el in interest:
                if len(el) > 0:
                    add_interest(vk_user_id=user_id, interest=el.strip().
                                 replace('(', '').
                                 replace(')', '').
                                 lower())

    for dict in offer_info:
        add_offer(user_id, dict['id_offer'], dict['first_name'], dict['last_name'], dict['sex'], dict['bdate'], dict['city'])
        for interest in dict['interests']:
            if len(interest) > 0:
                for el in interest:
                    if len(el) > 0:
                        add_interest(vk_offer_id=dict['id_offer'], interest=el.strip().
                                     replace('(', '').
                                     replace(')', '').
                                     lower())

    for dict_p in photos_info:
        add_photo(vk_offer_id=dict_p['id_offer'], photo_url=dict_p['top_photos'])

from VKinder_DB_folder.VKinder_DB import create_db, add_user, add_offer, add_photo
from VKinder_get_and_filling.VKinder_get_data import VKinder


def filling_db(token, user_id):
    """
    Данная функция получает данные от VK Api и загружает их в базу данных
    :param token: Токен VK Api
    :param user_id: id пользователя, который пишет нам в бот
    """
    vkinder = VKinder(token, user_id)
    user_info, offer_info, photos_info = vkinder.activate_get_search_photos()
    # print(user_info, offer_info, photos_info)
    vkinder.clear_func()

    create_db()
    add_user(vk_user_id=user_id, first_name=user_info['first_name'], sex=user_info['sex'], age=user_info['b_date'], city=user_info['city_name'])
    for dict in offer_info:
        add_offer(user_id, dict['id_offer'], dict['first_name'], dict['last_name'], dict['sex'], dict['bdate'], dict['city'])

    for dict_p in photos_info:
        add_photo(vk_offer_id=dict_p['id_offer'], photo_url=dict_p['top_photos'])



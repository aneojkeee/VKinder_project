import requests
from tokens_vk import token_gr, token
from dataclasses import dataclass
from datetime import datetime
from pprint import pprint
import traceback
import time
import logging


logging.basicConfig(level=logging.INFO, filename="main.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")


@dataclass()
class AllInfo:

    """
    Датакласс, где будет храниться id пользователя и информация полученная от методов класса Vkinder.
    После эти данные будут заливаться в базу данных
    """
    user_id: int
    dict_get_user: dict
    dict_search_user: list
    dict_photos_search_user: list


class HttpException(Exception):

    """Класс исключения, выбрасываем, когда API возвращает ошибку"""

    def __init__(self, status, message=''):
        self.status = status
        self.message = message

    def __str__(self):
        return f'http error: {self.status}\n{self.message}'


class ApiBasic:

    """Базовый класс API от него унаследуется Клиент VK"""

    def _send_request(self, http_method, uri_path, params=None, json=None, response_type=None):

        """
        Через этот метод будут отправляться все запросы ко всем API.
        Здесь мы можем обрабатывать любые исключения, логирвать запросы и т.п.

        :param http_method: GET/POST/PUT/PATCH/DELETE
        :param uri_path: uri API, например method/users.get
        :param params:
        :param json:
        :param response_type: тип ответа, например json
        :return:
        """

        response = requests.request(http_method, f'{self.host}/{uri_path}', params=params, json=json)  # отправляем запрос
        logging.info(f"""
                             Date and time: {datetime.now().strftime('%Y-%m-%d %H.%M')}
                             Method: {self.host}/{uri_path}
                             Status_code: {response.status_code}
                             Params: {params}
                             """)
        if response.status_code >= 400:
            # если с сервера приходит ошибка выбрасываем исключение
            raise HttpException(response.status_code, response.text)
        if response_type == 'json':
            response = response.json()

        return response


class Vkinder(ApiBasic):

    """Класс взаимодействующий с VK API"""

    host = 'https://api.vk.com/'

    def __init__(self, token, user_id):

        """

        :param token: Токен VK Api
        :param user_id: id пользователя, который пишет нам в бот
        """

        self.user_id = user_id
        self.params = {
            'access_token': token,
            'v': '5.131'
        }

    def get_user(self):

        """
        Получаем пользователя, используя унаследованный метод _send_request и передаем словарь
        в датакласс AllInfo
        """

        res = self._send_request(
            http_method='GET',
            uri_path='method/users.get',
            params={
                'user_id': self.user_id,
                'fields': 'sex,city,bdate',
                **self.params
            },
            response_type='json'
        )

        u_bdate = res['response'][0]['bdate']
        u_city = res['response'][0]['city']['id']
        u_sex = res['response'][0]['sex']
        u_name = res['response'][0]['first_name']
        data_dict = {'first_name': u_name, 'b_date': u_bdate, 'city': u_city, 'sex': u_sex, 'city_name': res['response'][0]['city']['title']}
        AllInfo.dict_get_user = data_dict

    def search_user(self):

        """
        Используем информацию, полученную от метода get_user(пол, возраст, город пользователя общающегося с ботом)
        из датакласса AllInfo.
        Через унаследованный метод _send_request, передаем VK параметры поиска людей для знакомства,
        получаем список словарей с данными предложений подходящих пользователю.
        Передаем эту информацию в датакласс AllInfo.
        """

        info_u = AllInfo.dict_get_user
        age = int(datetime.now().strftime('%Y')) - int(info_u['b_date'].split('.')[-1])

        res = self._send_request(
            http_method='GET',
            uri_path='method/users.search',
            params={'count': 15, # Количество пользователь которых хотим найти, поменять на 1000 как закончим тесты
                    'fields': 'city,bdate,sex,counters',
                    'city': info_u['city'],
                    'sex': 2 if info_u['sex'] == 1 else 1,
                    'age_from': age - 5,
                    'age_to': age + 5,
                     'status': '6',
                     **self.params},
            response_type='json'
        )
        search_data_list = []
        for user in res['response']['items']:

            if user['is_closed'] == True:
                continue
            if 'city' not in user.keys():
                continue
            if user['city']['id'] != info_u['city']:
                continue

            search_data_list.append(
                {'id_offer': user['id'], 'first_name': user['first_name'], 'last_name': user['last_name'],
                 'sex': user['sex'], 'city': user['city']['title'], 'bdate': user['bdate']})
        AllInfo.dict_search_user = search_data_list


    def get_fotos_user(self):

        """
        Используем информацию, полученную от метода search_user(а именно список людей
        предложенных пользователю для знакомства) из датакласса AllInfo.
        Осуществляем отбор 3 топовых фото по количеству лайков.
        Передаем список словарей с данными которые буду выводиться в чате с ботом пользователю.
        Имя, Фамилия, ссылка на профиль, 3 ссылки на фото предложения.
        Так же передаем эти данные в датакласс AllInfo.
        """

        search_u_info = AllInfo.dict_search_user
        finish_list = []
        for data in search_u_info:
            res = self._send_request(
                http_method='GET',
                uri_path='method/photos.get',
                params={'owner_id': data['id_offer'],
                        'album_id': 'profile',
                        'extended': 1,
                        'count': 15,
                        **self.params},
                response_type='json'
            )
            time.sleep(0.2) #Чтобы сервер не блокировал из-за привышения лимита запросов

            if res['response']['count'] == 0:
                continue

            list_id_likes = []
            for i in res['response']['items']:
                url_photo = i['sizes'][-1]['url']
                likes = i['likes']['count']
                list_id_likes.append({'url': url_photo, 'likes': likes})
            list_id_likes.sort(key=lambda dictionary: dictionary['likes'])

            if len(list_id_likes) >= 3:
                list_top_photos = [list_id_likes[-1]['url'], list_id_likes[-2]['url'], list_id_likes[-3]['url']]
            else:
                list_top_photos = [url['url'] for url in list_id_likes]
            finish_list.append({'id_offer': data["id_offer"],
                      'top_photos': list_top_photos, 'profile': f'https://vk.com/id{data["id_offer"]}'})
        AllInfo.dict_photos_search_user = finish_list


    def activate_get_search_photos(self):

        """
        Метод активирует, все предыдущие методы данного класса и проверяет на наличие даты рождения у пользователя
        """

        try:
            self.get_user()
            self.search_user()
            self.get_fotos_user()
        except KeyError:
            if 'bdate' in traceback.format_exc():
                print('Дата рождения отсутствует')



# user_id = 1
# vkinder = Vkinder(token, user_id)
# vkinder.activate_get_search_photos()
# pprint(AllInfo.dict_photos_search_user)
#AllInfo.dict_photos_search_user

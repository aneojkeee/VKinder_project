import requests
import traceback
import time
import logging
from datetime import date
from datetime import datetime
from pprint import pprint

logging.basicConfig(level=logging.INFO, filename="main.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")


class VKinder:
    """Класс взаимодействующий с VK API"""

    dict_get_user = {}
    list_search_user = []
    list_photos_search_user = []

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

    def http_exception(self, status, message=''):
        """Функция исключения, выбрасываем, когда API возвращает ошибку"""
        return f'http error: {status}\n{message}'

    def _send_request(self, http_method, uri_path, params=None, json=None, response_type=None):
        """
            Через этот метод будут отправляться все запросы ко всем API.
        Здесь мы можем обрабатывать любые исключения, логировать запросы и т.п.

        :param http_method: GET/POST/PUT/PATCH/DELETE
        :param uri_path: uri API, например method/users.get
        :param params:
        :param json:
        :param response_type: тип ответа, например json
        """
        host = 'https://api.vk.com/method'
        response = requests.request(http_method, f'{host}/{uri_path}', params=params, json=json)  # отправляем запрос
        logging.info(f"""
                        Date and time: {datetime.now().strftime('%Y-%m-%d %H.%M')}
                        Method: {host}/{uri_path}
                        Status_code: {response.status_code}
                        Params: {params}
                        """)
        if response.status_code >= 400:
            # если с сервера приходит ошибка выбрасываем исключение
            raise self.http_exception(response.status_code, response.text)
        if response_type == 'json':
            response = response.json()
        return response

    def user_age(self, user_b_date):
        date_born_str = user_b_date['bdate']
        date_born_list = [int(el) for el in date_born_str.split('.')][::-1]
        date_born = date(*date_born_list)
        delta_years = date.today().year - date_born.year
        if (date.today().month, date.today().day) > (date_born.month, date_born.day):
            return delta_years
        else:
            return delta_years - 1

    def get_user(self):
        """
            Получаем пользователя, используя унаследованный метод _send_request и передаем словарь
        в self.dict_get_user
        """
        res = self._send_request(
            http_method='GET',
            uri_path='users.get',
            params={
                'user_id': self.user_id,
                'fields': 'sex,city,bdate',
                **self.params
                    },
            response_type='json'
        )
        u_bdate = res['response'][0]
        u_city = res['response'][0]['city']['id']
        u_sex = res['response'][0]['sex']
        u_name = res['response'][0]['first_name']
        self.dict_get_user = {'first_name': u_name,
                     'b_date': self.user_age(u_bdate),
                     'city': u_city,
                     'sex': u_sex,
                     'city_name': res['response'][0]['city']['title']}

    def search_user(self):
        """
            Используем информацию, полученную от метода get_user(пол, возраст, город пользователя общающегося с ботом)
        из self.dict_get_user.
        Через унаследованный метод _send_request, передаем VK параметры поиска людей для знакомства,
        получаем список словарей с данными предложений подходящих пользователю.
        Передаем эту информацию в self.list_search_user.
        """

        age = self.dict_get_user['b_date']

        res = self._send_request(
            http_method='GET',
            uri_path='users.search',
            params={'count': 15, # Количество пользователь которых хотим найти, поменять на 1000 как закончим тесты
                    'fields': 'city,bdate,sex,counters',
                    'city': self.dict_get_user['city'],
                    'sex': 2 if self.dict_get_user['sex'] == 1 else 1,
                    'age_from': age - 5,
                    'age_to': age + 5,
                     'status': '6',
                     **self.params},
            response_type='json'
        )
        for user in res['response']['items']:
            if user['is_closed'] == True:
                continue
            if 'city' not in user.keys():
                continue
            if user['city']['id'] != self.dict_get_user['city']:
                continue
            self.list_search_user.append(
                {'id_offer': user['id'],
                 'first_name': user['first_name'],
                 'last_name': user['last_name'],
                 'sex': user['sex'],
                 'city': user['city']['title'],
                 'bdate': self.user_age(user)
                 })

    def get_fotos_user(self):
        """
            Используем информацию, полученную от метода search_user(а именно список людей
        предложенных пользователю для знакомства) из self.list_search_user.
        Осуществляем отбор 3 топовых фото по количеству лайков.
        Передаем список словарей с данными которые буду выводиться в чате с ботом пользователю.
        Имя, Фамилия, ссылка на профиль, 3 ссылки на фото предложения, передаем эти данные в
        self.list_photos_search_user.
        """
        for data in self.list_search_user:
            res = self._send_request(
                http_method='GET',
                uri_path='photos.get',
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
                id_photo = i['id']
                likes = i['likes']['count']
                list_id_likes.append({'id_img': id_photo, 'likes': likes})
            list_id_likes.sort(key=lambda dictionary: dictionary['likes'])
            pprint((list_id_likes))
            if len(list_id_likes) >= 3:
                list_top_photos = [list_id_likes[-1]['id_img'], list_id_likes[-2]['id_img'], list_id_likes[-3]['id_img']]
            else:
                list_top_photos = [url['id_img'] for url in list_id_likes]
            self.list_photos_search_user.append({'id_offer': data["id_offer"],
                                                'top_photos': list_top_photos,
                                                })

    def activate_get_search_photos(self):
        """
            Метод активирует, все предыдущие методы данного класса и
            проверяет на наличие даты рождения у пользователя
        """
        try:
            self.get_user()
            self.search_user()
            self.get_fotos_user()
            return self.dict_get_user, self.list_search_user, self.list_photos_search_user
        except KeyError:
            if 'bdate' in traceback.format_exc():
                print('Дата рождения отсутствует')

    def clear_func(self):
        """Функция очищает значение класса VKinder"""

        self.user_id = 0
        self.dict_get_user = {}
        self.list_search_user = []
        self.list_photos_search_user = []

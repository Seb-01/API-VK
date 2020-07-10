import requests

"""
vk.com/dev - документация по API
"""
# Шаг 1. Права доступа для токена сообщества. Позволяет работать от имени группы, сообщества или публичной страницы
# ниже ПРИМЕРНЫЙ код для получения токена:
"""
OAUTH_URL = 'https://oauth.vk.com/authorize'
APP_ID = 7532975

OAUTH_DATA = {
    'client_id': APP_ID,
    'display': 'mobile',
    'scope': 'status,audio',
    'response_type': 'token',
    'v': 5.120,
    'redirect_uri': 'https://example.com/'
}

print('?'.join(
    (OAUTH_URL, urlencode(OAUTH_DATA))
))
"""

# Токен (строка) у нас уже есть готовый:
TOKEN = '10b2e6b1a90a01875cfaa0d2dd307b7a73a15ceb1acf0c0f2a9e9c586f3b597815652e5c28ed8a1baf13c'

# Шаг 2. Префикс доступа к методам:
# протокол доступа: https://
# адрес API-сервиса: api.vk.com/method
API_URL = 'https://api.vk.com/method'

# Шаг 3. Ищем открытое сообщество
# Для работы с API достаточно просто токена. Выберем любых пользователей ВК по своему усмотрению
# (с открытыми профилями), и будем экспериментировать на них.
#  Я выбрал Зарулем. Раньше был неплохой журнал. 90760 подписчиков. Имя сообщества:
# https://vk.com/zronline

SHORT_NAME_COMMUNITY = 'zronline'

# Шаг 4. Ищем методы из раздела Groups для получения определенного количества участников сообщества
METHOD_GROUPS_MEMBERS = '/groups.getMembers'
# Шаг 5. Ищем методы из раздела friends для проверки "дружбы"
METHOD_FRIENDS_AREFRIENDS = '/friends.areFriends'
METHOD_FRIENDS_GET = '/friends.get' #возвращает список ID друзей пользователя
METHOD_FRIENDS_GETLISTS = '/friends.getLists' #возвращает список меток друзей пользователя

# Шаг 6. Префикс доступа к профилю:
PROFILE_URL = 'https://vk.com/id'

def get_members(token, num_members, group_name) -> list:
    """
    Получить список ID заданного количества участников сообщества
    """
    response = requests.get(
        API_URL + METHOD_GROUPS_MEMBERS,
        params={
            'access_token': token,
            'sort': 'id_asc', #в порядке возрастания id
            'offset': 0,
            'group_id': group_name,
            'count': num_members,
            'v': 5.23
        }
    )

    #получаем в ответ словарь с данными
    answer = response.json()['response']
    #но нам нужен список ID пользователей
    ids_list=answer['items']

    print(f'Список ID пользователей: {ids_list}')
    #print (type(ids_list))
    return ids_list


def find_equal(list_one, list_two) -> list:
    """
    Возвращает список одинаковых элементов двух списков
    :param list_one:
    :param list_two:
    :return:
    """
    return [same for same in set(list_one) & set (list_two)]

class User:
    """
    Класс - пользователь VK
    """
    def __init__(self, token, user_id) -> None:
        self.token = token
        self.user_id = user_id


    def __str__(self) -> str:
        """
        Определяет поведение функции str(), вызванной для экземпляра класса User.
        Для использования в print()

        :return:
        """
        return (PROFILE_URL + str(self.user_id))


    def get_friends(self, num_friends=5000) ->list:
        """
        Получить список num_friends ID друзей
        """
        response = requests.get(
            API_URL + METHOD_FRIENDS_GET,
            params={
                'access_token': self.token,
                'user_id': self.user_id,
                'count': num_friends,
                'v': 5.21
            }
        )

        # получаем в ответ словарь с данными
        #print(response.json())
        # проверка на error: есть ли в ответе ключ "error"
        if response.json().get('error'):
            #print (f"Ошибка: {response.json()['error']['error_code']}")
            return []
        else:
            answer = response.json()['response']
            # но нам нужен список ID друзей
            ids_list = answer['items']

        #print(ids_list)
        #print (type(ids_list))
        return ids_list

    def __and__(self, user) -> list:
        """
        Переопределяем магический метод: функция реализует логическое "И" как выдачу списка общих друзей пользователей
        :param value:
        :return:
        """
        my_friends=self.get_friends()
        user_friends=user.get_friends()

        #return find_equal(self.get_friends(),user.get_friends())
        return find_equal(my_friends, user_friends)


def main():
    """
    Главный модуль программы.
    """

    # Создаем экземпляры класса участников сообщества "За рулем":
    num_members = int(input(f'Введите количество участников сообщества https://vk.com/{SHORT_NAME_COMMUNITY} (не менее 20):'))
    members=get_members(TOKEN, num_members, SHORT_NAME_COMMUNITY)
    vk_users=[User(TOKEN,id) for id in members]


    # Ищем общих друзей среди всех выбранных пользователей:
    print(f'Ищем среди участников сообщества https://vk.com/{SHORT_NAME_COMMUNITY} общих друзей:')
    #pairs_count = 0
    for x in range(len(vk_users)):
        for y in range(len(vk_users)):
            #pairs_count += 1
            #print(f'Проверка пары {pairs_count}')
            if x == y:
                continue
            else:
                common = vk_users[x] & vk_users[y]
                # если есть общие друзья
                if not common == []:
                    print(f'У пользователей {vk_users[x]} и {vk_users[y]} есть общие друзья: {common}')
                    #print(vk_users[x])
                    #print(vk_users[y])

if __name__ == '__main__':
    main()


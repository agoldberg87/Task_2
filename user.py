import requests
import allure
from data import Data


@allure.step('Логин пользователя')
def login_user(email, password):
    login_data = {
        "email": email,
        "password": password
    }
    response = requests.post(f"{Data.BASE_URL}/auth/login", json=login_data)
    return response


@allure.step('Регистрация пользователя')
def register_user(email, password, name):
    user_data = {
        "email": email,
        "password": password,
        "name": name
    }
    response = requests.post(f"{Data.BASE_URL}/auth/register", json=user_data)
    return user_data, response




@allure.step('Обновление данных пользователя')
def update_user_data(access_token, updated_data):
    headers = {
        "Authorization": access_token
    }
    response = requests.patch(f"{Data.BASE_URL}/auth/user", json=updated_data, headers=headers)
    return response
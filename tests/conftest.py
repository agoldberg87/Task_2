import random
import string
import allure
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data import Data
import pytest
from user import register_user, login_user, delete_user


@pytest.fixture
@allure.step('Сгенерировать случайный email')
def generate_random_email():
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"test_{random_string}@example.com"


@pytest.fixture
@allure.step('Сгенерировать случайный пароль')
def generate_random_password():
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return random_string


@pytest.fixture
@allure.step('Сгенерировать случайное имя')
def generate_random_name():
    random_string = ''.join(random.choices(string.ascii_letters, k=10))
    return f"test_{random_string}"


@pytest.fixture
@allure.step('Сгенерировать данные пользователя')
def generate_user_data(generate_random_email, generate_random_password, generate_random_name):
    return {
        "email": generate_random_email,
        "password": generate_random_password,
        "name": generate_random_name
    }


@pytest.fixture
@allure.step('Генерация данных заказа')
def generate_order_data(ingredients=None):
    if ingredients is None:
        ingredients = [Data.SAMPLE_INGREDIENT_1, Data.SAMPLE_INGREDIENT_2]
    
    return {"ingredients": ingredients}


@pytest.fixture
@allure.step('Создание и удаление пользователя')
def create_and_delete_user(generate_random_email, generate_random_password, generate_random_name, request):
    """Фикстура создает пользователя и автоматически удаляет его после теста"""
    
    user_data, register_response = register_user(generate_random_email, generate_random_password, generate_random_name)
    assert register_response.status_code == 200, "Не удалось создать пользователя для теста"
    
    login_response = login_user(generate_random_email, generate_random_password)
    assert login_response.status_code == 200, "Не удалось войти в систему для получения токена"
    
    access_token = login_response.json()["accessToken"]
    
    def delete_user_finalizer():
        delete_response = delete_user(access_token)
        assert delete_response.status_code == 202, f"Не удалось удалить пользователя: {delete_response.status_code}"
    
    request.addfinalizer(delete_user_finalizer)
    
    return {
        "email": generate_random_email,
        "password": generate_random_password,
        "name": generate_random_name,
        "access_token": access_token
    }


@pytest.fixture
@allure.step('Создание и удаление второго пользователя')
def create_and_delete_second_user(generate_random_email, generate_random_password, generate_random_name, request):
    """Фикстура создает второго пользователя и автоматически удаляет его после теста - для теста с повторяющимся email'ом"""
    
    second_email = f"second_{generate_random_email}"
    user_data, register_response = register_user(second_email, generate_random_password, generate_random_name)
    assert register_response.status_code == 200, "Не удалось создать второго пользователя для теста"
    
    login_response = login_user(second_email, generate_random_password)
    assert login_response.status_code == 200, "Не удалось войти в систему для получения токена"
    
    access_token = login_response.json()["accessToken"]
    
    def delete_user_finalizer():
        delete_response = delete_user(access_token)
        assert delete_response.status_code == 202, f"Не удалось удалить второго пользователя: {delete_response.status_code}"
    
    request.addfinalizer(delete_user_finalizer)
    
    return {
        "email": second_email,
        "password": generate_random_password,
        "name": generate_random_name,
        "access_token": access_token
    }
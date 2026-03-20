import random
import string
import allure
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data import Data
import pytest


@pytest.fixture
@allure.step('Сгенерировать случайный email')
def generate_random_email():
    """Generate a random email for testing"""
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


@pytest.fixture(scope="session", autouse=True)
def cleanup_after_all_tests():
    yield
    print("All tests completed - final teardown executed")
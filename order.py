import requests
import allure
from data import Data


@allure.step('Создание заказа')
def create_order(access_token=None, ingredients=None):
    headers = {}
    if access_token:
        headers["Authorization"] = access_token
    
    order_data = {}
    if ingredients is not None:
        order_data["ingredients"] = ingredients
    
    response = requests.post(f"{Data.BASE_URL}/orders", json=order_data, headers=headers)
    return response


@allure.step('Получение заказов пользователя')
def get_user_orders(access_token):
    headers = {"Authorization": access_token}
    response = requests.get(f"{Data.BASE_URL}/orders", headers=headers)
    return response
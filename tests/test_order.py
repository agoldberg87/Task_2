import pytest
import requests
import allure
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data import Data
from user import login_user, register_user
from order import create_order, get_user_orders


class TestOrderCreation:
    
    @allure.title('Создание заказа с авторизацией')
    def test_create_order_with_authorization_success(self, generate_random_name, generate_random_email, generate_random_password, generate_order_data):
        register_user(generate_random_email, generate_random_password, generate_random_name)
        
        login_response = login_user(generate_random_email, generate_random_password)
        
        login_data = login_response.json()
        access_token = login_data["accessToken"]
        
        generated_order = generate_order_data
        order_response = create_order(access_token, generated_order["ingredients"])
        
        assert order_response.status_code == 200, f"Expected status 200, got {order_response.status_code}"
        
        order_data = order_response.json()
        assert order_data["success"] is True, "Success flag should be True"
        assert "order" in order_data, "Response should contain order object"
        assert "number" in order_data["order"], "Order should have a number"
        assert "status" in order_data["order"], "Order should have a status"
        assert "createdAt" in order_data["order"], "Order should have creation timestamp"
        assert "updatedAt" in order_data["order"], "Order should have update timestamp"
        
        assert "ingredients" in order_data["order"], "Order should contain ingredients"
        assert len(order_data["order"]["ingredients"]) == len(generated_order["ingredients"]), "Order should contain correct number of ingredients"
    
    @allure.title('Создание заказа без авторизации')
    def test_create_order_without_authorization_failure(self, generate_order_data):

        order_data = generate_order_data
        order_response = create_order(None, order_data["ingredients"])
        
        # Сервис позволяет заказать без авторизации, т.о. мы ожидаем успех
        assert order_response.status_code == 200, f"Expected status 200, got {order_response.status_code}"
        
        order_data = order_response.json()
        assert order_data["success"] is True, "Success flag should be True"
        assert "order" in order_data, "Response should contain order object"
    
    @allure.title('Создание заказа с валидными ингредиентами')
    def test_create_order_with_ingredients_success(self, generate_random_email, generate_random_password, generate_random_name):
        register_user(generate_random_email, generate_random_password, generate_random_name)
        
        login_response = login_user(generate_random_email, generate_random_password)
        
        login_data = login_response.json()
        access_token = login_data["accessToken"]
        
        ingredients = [Data.SAMPLE_INGREDIENT_1] # Проверяем с минимальным валидным количеством ингредиентов
        order_response = create_order(access_token, ingredients)
        
        assert order_response.status_code == 200, f"Expected status 200, got {order_response.status_code}"
        
        order_data = order_response.json()
        assert order_data["success"] is True, "Success flag should be True"
        assert len(order_data["order"]["ingredients"]) == 1, "Order should contain one ingredient"
    
    @allure.title('Создание заказа без ингредиентов')
    def test_create_order_without_ingredients_failure(self, generate_random_email, generate_random_password, generate_random_name):
        register_user(generate_random_email, generate_random_password, generate_random_name)
        
        login_response = login_user(generate_random_email, generate_random_password)
        
        login_data = login_response.json()
        access_token = login_data["accessToken"]
        
        order_response = create_order(access_token, None)
        
        assert order_response.status_code == 400, f"Expected status 400, got {order_response.status_code}"
        
        order_data = order_response.json()
        assert order_data["success"] is False, "Success flag should be False"
        assert order_data["message"] == Data.message_order_missing_ingredients, "Should indicate missing ingredients"
    
    @allure.title('Создание заказа с невалидным хэшем ингредиента')
    def test_create_order_with_invalid_ingredient_hash_failure(self, generate_random_email, generate_random_password, generate_random_name):
        register_user(generate_random_email, generate_random_password, generate_random_name)
        
        login_response = login_user(generate_random_email, generate_random_password)
        
        login_data = login_response.json()
        access_token = login_data["accessToken"]
        
        ingredients = [Data.INVALID_INGREDIENT]
        order_response = create_order(access_token, ingredients)
        
        assert order_response.status_code == 500, f"Expected status 500, got {order_response.status_code}"


class TestUserOrders:
    
    @allure.title('Получение заказов пользователя с авторизацией')
    def test_get_user_orders_with_authorization_success(self, generate_random_email, generate_random_password, generate_random_name, generate_order_data):
        register_user(generate_random_email, generate_random_password, generate_random_name)
        
        login_response = login_user(generate_random_email, generate_random_password)
        
        login_data = login_response.json()
        access_token = login_data["accessToken"]
        
        order_data = generate_order_data
        create_order(access_token, order_data["ingredients"])
        
        orders_response = get_user_orders(access_token)
        
        assert orders_response.status_code == 200, f"Expected status 200, got {orders_response.status_code}"
        
        orders_data = orders_response.json()
        assert orders_data["success"] is True, "Success flag should be True"
        assert "orders" in orders_data, "Response should contain orders array"
        assert isinstance(orders_data["orders"], list), "Orders should be a list"
        
        if orders_data["orders"]:
            order = orders_data["orders"][0]
            assert "_id" in order, "Order should have an id"
            assert "number" in order, "Order should have a number"
            assert "status" in order, "Order should have a status"
            assert "ingredients" in order, "Order should have ingredients"
            assert "createdAt" in order, "Order should have creation timestamp"
            assert "updatedAt" in order, "Order should have update timestamp"
    
    @allure.title('Получение заказов пользователя без авторизации')
    def test_get_user_orders_without_authorization_failure(self):
        orders_response = get_user_orders("")
        
        assert orders_response.status_code == 401, f"Expected status 401, got {orders_response.status_code}"
        
        orders_data = orders_response.json()
        assert orders_data["success"] is False, "Success flag should be False"
        assert orders_data["message"] == Data.message_order_unauthorized, "Should indicate authorization required"
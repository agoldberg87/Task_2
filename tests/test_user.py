import pytest
import requests
import allure
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data import Data
from user import login_user, register_user, update_user_data

class TestUserRegistration:
    
    @allure.title('Создание пользователя')
    def test_create_new_user_success(self, generate_random_email, generate_random_password, generate_random_name):
        _, response = register_user(generate_random_email, generate_random_password, generate_random_name)
        
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        response_data = response.json()
        assert response_data["success"] is True, "Флаг success должен быть True"
        assert "accessToken" in response_data, "В ответе должен быть accessToken"
        assert "refreshToken" in response_data, "В ответе должен быть refreshToken"
        assert "user" in response_data, "В ответе должен быть объект user"
        
        user_info = response_data["user"]
        assert user_info["email"] == generate_random_email, "Email пользователя должен совпадать"
        assert user_info["name"] == generate_random_name, "Имя пользователя должно совпадать"
    
    
    @allure.title('Создание пользователя с существующими данными')
    def test_create_existing_user_failure(self, generate_random_email, generate_random_password, generate_random_name):
        _, first_response = register_user(generate_random_email, generate_random_password, generate_random_name)
        assert first_response.status_code == 200, "Первая регистрация должна быть успешной"
        
        _, second_response = register_user(generate_random_email, generate_random_password, generate_random_name)
        assert second_response.status_code == 403, f"Ожидался статус 403, получен {second_response.status_code}"
        
        response_data = second_response.json()
        assert response_data["success"] is False, "Флаг success должен быть False"
        assert response_data["message"] == Data.message_failure_existing_user, "Сообщение должно информировать о том, что пользователь уже существует"
    
    
    @allure.title('Создание пользователя без обязательных полей')
    @pytest.mark.parametrize("field", ["email", "password", "name"])
    def test_create_user_missing_required_field_failure(self, field, generate_user_data):
        user_data_without_field = generate_user_data
        del user_data_without_field[field]
        
        _, response = register_user(user_data_without_field.get("email", ""), user_data_without_field.get("password", ""), user_data_without_field.get("name", ""))
        
        assert response.status_code == 403, f"Ожидался статус 403, получен {response.status_code}"
        
        response_data = response.json()
        assert response_data["success"] is False, "Флаг success должен быть False"
        assert response_data["message"] == Data.message_failure_missing_required_field, "В ответе должно быть сообщение об ошибке"


class TestUserLogin:
    
    @allure.title('Логин существующего пользователя')
    def test_login_existing_user_success(self, create_and_delete_user):
        login_response = login_user(create_and_delete_user["email"], create_and_delete_user["password"])
        
        assert login_response.status_code == 200, f"Ожидался статус 200, получен {login_response.status_code}"
        
        login_data = login_response.json()
        assert login_data["success"] is True, "Флаг success должен быть True"
        assert "accessToken" in login_data, "В ответе должен быть accessToken"
        assert "refreshToken" in login_data, "В ответе должен быть refreshToken"
        assert "user" in login_data, "В ответе должен быть объект user"
        
        user_info = login_data["user"]
        assert user_info["email"] == create_and_delete_user["email"], "Email пользователя должен совпадать"
        assert user_info["name"] == create_and_delete_user["name"], "Имя пользователя должно совпадать"
    
    
    @allure.title('Логин с неверными учетными данными')
    @pytest.mark.parametrize("field", ["email", "password"])
    def test_login_with_invalid_credentials_failure(self, field, create_and_delete_user):
        if field == "email":
            response = login_user("invalid_email", create_and_delete_user["password"])
        else:
            response = login_user(create_and_delete_user["email"], "invalid_password")
        
        assert response.status_code == 401, f"Ожидался статус 401, получен {response.status_code}"
        
        response_data = response.json()
        assert response_data["success"] is False, "Флаг success должен быть False"
        assert response_data["message"] == Data.message_login_invalid_credentials, "Сообщение должно информировать о неверных учетных данных"
        


class TestUserDataModification:
    
    @allure.title('Обновление данных пользователя с авторизацией')
    @pytest.mark.parametrize("field, value_generator", [
        ("name", lambda name: f"updated_{name}"),
        ("email", lambda email: f"updated_{email}"),
        ("password", lambda password: f"updated_{password}")
    ])
    def test_update_user_data_with_authorization_success(self, field, value_generator, create_and_delete_user):
        access_token = create_and_delete_user["access_token"]
        
        updated_value = value_generator(create_and_delete_user[field])
        updated_data = {field: updated_value}
        
        update_response = update_user_data(access_token, updated_data)
        
        assert update_response.status_code == 200, f"Ожидался статус 200, получен {update_response.status_code}"
        
        update_data = update_response.json()
        assert update_data["success"] is True, "Флаг success должен быть True"
        assert "user" in update_data, "В ответе должен быть объект user"
        
        user_info = update_data["user"]
        
        if field == "password": # так как пароль не возвращается, проверяем только флаг success
            assert update_data["success"] is True, "Update should be successful for password change"
        else:
            assert user_info[field] == updated_value, f"Поле {field} должно быть обновлено"
    

    @allure.title('Обновление электронной почты на уже использованную')
    def test_update_user_data_with_already_used_email_failure(self, create_and_delete_user, create_and_delete_second_user):
        access_token = create_and_delete_user["access_token"]
        
        updated_data = {"email": create_and_delete_second_user["email"]}
        
        update_response = update_user_data(access_token, updated_data)
        
        assert update_response.status_code == 403, f"Ожидался статус 403, получен {update_response.status_code}"
        
        update_data = update_response.json()
        assert update_data["success"] is False, "Флаг success должен быть False"
        assert update_data["message"] == Data.message_user_data_updated_duplicate_email, "Сообщение должно информировать о том, что email уже используется"


    @allure.title('Обновление данных пользователя без авторизации')
    def test_update_user_data_without_authorization_failure(self, generate_random_name, generate_random_email, generate_random_password):
        updated_data = {
            "name": f"unauthorized_{generate_random_name}",
            "email": f"unauthorized_{generate_random_email}",
            "password": f"unauthorized_{generate_random_password}"
        }
        
        update_response = update_user_data("", updated_data)
        
        assert update_response.status_code == 401, f"Ожидался статус 401, получен {update_response.status_code}"
        
        update_data = update_response.json()
        assert update_data["success"] is False, "Флаг success должен быть False"
        assert update_data["message"] == Data.message_user_unauthorised, "Сообщение должно информировать о необходимости авторизации"
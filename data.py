class Data():

    BASE_URL = "https://stellarburgers.education-services.ru/api"
    message_failure_existing_user = "User already exists"
    message_failure_missing_required_field = "Email, password and name are required fields"
    message_login_success = "Successfully logged in"
    message_login_invalid_credentials = "email or password are incorrect"
    message_user_unauthorised = "You should be authorised"
    message_user_data_updated_duplicate_email = "User with such email already exists"
    
    message_order_unauthorized = "You should be authorised"
    message_order_missing_ingredients = "Ingredient ids must be provided"
    message_order_invalid_ingredients = "One or more ingredient ids are invalid"
    
    SAMPLE_INGREDIENT_1 = "61c0c5a71d1f82001bdaaa6c"
    SAMPLE_INGREDIENT_2 = "61c0c5a71d1f82001bdaaa70"
    INVALID_INGREDIENT = "invalid_ingredient_hash"
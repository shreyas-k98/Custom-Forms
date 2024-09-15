FORM_CREATION_PAYLOAD = {
    "form_title": "New Form test",
    "fields": [
        {"field_name": "Name", "field_type": "text", "is_required": True, "order": 1},
        {"field_name": "Email", "field_type": "text", "is_required": False, "order": 2},
        {
            "field_name": "Contact",
            "field_type": "text",
            "is_required": True,
            "order": 3,
        },
        {
            "field_name": "Gender",
            "field_type": "radio",
            "is_required": False,
            "order": 4,
            "options": [
                {"label": "Male", "value": "M"},
                {"label": "Female", "value": "F"},
            ],
        },
    ],
}

USER_SIGNUP_PAYLOAD = {
    "name": "test_name",
    "email": "new@test.com",
    "username": "test_username",
    "password": "test_password",
}

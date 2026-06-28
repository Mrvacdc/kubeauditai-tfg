from app.security.passwords import hash_password, verify_password


def test_hash_password_should_not_store_plain_text():
    plain_password = "ExamplePassword123!"

    password_hash = hash_password(plain_password)

    assert password_hash != plain_password
    assert verify_password(plain_password, password_hash)


def test_verify_password_should_fail_with_invalid_password():
    password_hash = hash_password("ExamplePassword123!")

    assert not verify_password("WrongPassword123!", password_hash)

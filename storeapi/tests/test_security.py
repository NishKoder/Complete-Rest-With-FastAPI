import pytest

from storeapi import security


def test_password_hash():
    password = "password"
    hashed_password = security.get_password_hash(password)
    assert hashed_password != password
    assert security.verify_password(password, hashed_password)


@pytest.mark.asyncio
async def test_get_user_by_email(register_user):
    user_details = await register_user
    user = await security.get_user_by_email(
        user_details["email"]
    )  # pass the email string
    assert user["email"] == user_details["email"]


@pytest.mark.asyncio
async def test_get_user_by_email_no_user():
    user = await security.get_user_by_email("test@example.com")
    assert user is None


@pytest.mark.asyncio
async def test_authenticate_user(register_user):
    user_details = await register_user
    user = await security.authenticate_user(
        user_details["email"], user_details["password"]
    )
    assert user["email"] == user_details["email"]


@pytest.mark.asyncio
async def test_authenticate_user_no_user():
    with pytest.raises(security.credentials_exception.__class__):
        await security.authenticate_user("test@example.com", "1234")


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(register_user):
    user_details = await register_user
    with pytest.raises(security.credentials_exception.__class__):
        await security.authenticate_user(user_details["email"], "wrongpassword")


@pytest.mark.asyncio
async def test_get_current_user(register_user):
    user_details = await register_user
    token = security.create_access_token(user_details["email"])
    user = await security.get_current_user(token)
    assert user["email"] == user_details["email"]


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    with pytest.raises(security.credentials_exception.__class__):
        await security.get_current_user("invalidtoken")
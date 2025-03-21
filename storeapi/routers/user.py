import logging
from fastapi import APIRouter, HTTPException, status
from storeapi.models.user import UserIn
from storeapi.database import database, user_table
from storeapi.security import get_user_by_email, get_password_hash, authenticate_user, create_access_token


router = APIRouter()


@router.post("/register", status_code=201)
async def register(user: UserIn):
    logging.info(f"Registering user: {user.email}", extra={"email": user.email})
    user_exists = await get_user_by_email(user.email)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    hashed_password = get_password_hash(user.password)
    query = user_table.insert().values(
        email=user.email, password=hashed_password
    )
    logging.debug(f"Query: {query}")
    await database.execute(query)
    logging.info(f"User registered: {user.email}")
    return {"message": "User registered successfully"}


@router.post("/token")
async def login(user: UserIn):
    logging.info(f"Logging in user: {user.email}", extra={"email": user.email})
    user = await authenticate_user(user.email, user.password)
    token = create_access_token(user["email"])
    return {"access_token": token, "token_type": "bearer"}

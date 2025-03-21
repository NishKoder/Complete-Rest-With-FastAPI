import logging
from fastapi import APIRouter, HTTPException

from storeapi.database import comment_table, database, post_table
from storeapi.models.post import (
    Comment,
    CommentIn,
    UserPost,
    UserPostIn,
    UserPostWithComments,
)

router = APIRouter()

logging = logging.getLogger(__name__)

async def find_post(post_id: int) -> dict:
    logging.debug("Getting post with id %s", post_id)
    query = post_table.select().where(post_table.c.id == post_id)
    logging.debug("Query: %s", query)
    post = await database.fetch_one(query)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn):
    logging.debug("Creating post with data %s", post)
    data = post.dict()
    query = post_table.insert().values(data)
    logging.debug("Query: %s", query)
    last_post_id = await database.execute(query)
    new_post = {"id": last_post_id, **data}
    logging.debug("New post created: %s", new_post)
    return new_post


@router.get("/post", response_model=list[UserPost])
async def get_posts():
    logging.debug("Getting all posts")
    query = post_table.select()
    logging.debug("Query: %s", query)
    return await database.fetch_all(query)


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(comment: CommentIn):
    await find_post(comment.post_id)
    logging.debug("Creating comment with data %s", comment)
    data = comment.dict()
    query = comment_table.insert().values(data)
    logging.debug("Query: %s", query)
    last_comment_id = await database.execute(query)
    new_comment = {"id": last_comment_id, **data}
    return new_comment


@router.get("/post/{post_id}/comment", response_model=list[Comment])
async def get_comments(post_id: int):
    logging.debug("Getting comments for post with id %s", post_id)
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    logging.debug("Query: %s", query)
    return await database.fetch_all(query)


@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    logging.debug("Getting post with id %s", post_id)
    post = await find_post(post_id)
    logging.debug("Getting comments for post with id %s", post_id)
    return {"post": post, "comments": await get_comments(post_id)}

from fastapi import APIRouter, HTTPException

from storeapi.models.post import (
    Comment,
    CommentIn,
    UserPost,
    UserPostIn,
    UserPostWithComments,
)

router = APIRouter()


post_table = {}
comment_table = {}


def find_post(post_id: int):
    post = post_table.get(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn):
    data = post.dict()
    last_post_id = len(post_table)
    new_post = {"id": last_post_id, **data}
    post_table[last_post_id] = new_post
    return new_post


@router.get("/post", response_model=list[UserPost])
async def get_posts():
    return list(post_table.values())


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(comment: CommentIn):
    find_post(comment.post_id)
    data = comment.dict()
    last_comment_id = len(comment_table)
    new_comment = {"id": last_comment_id, **data}
    comment_table[last_comment_id] = new_comment
    return new_comment


@router.get("/post/{post_id}/comment", response_model=list[Comment])
async def get_comments(post_id: int):
    find_post(post_id)
    return [
        comment for comment in comment_table.values() if comment["post_id"] == post_id
    ]


@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    post = find_post(post_id)
    return {"post": post, "comments": await get_comments(post_id)}

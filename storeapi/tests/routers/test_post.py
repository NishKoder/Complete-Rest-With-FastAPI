import pytest
from httpx import AsyncClient

# Helper function to create a post
async def create_post(async_client: AsyncClient, body: str = "test body") -> dict:
    response = await async_client.post("/api/v1/posts/post", json={"body": body})
    assert response.status_code == 201
    return response.json()

@pytest.fixture()
async def created_post(async_client: AsyncClient) -> dict:
    return await create_post(async_client)

@pytest.mark.asyncio
async def test_create_post(async_client: AsyncClient) -> None:
    body = "test body"
    response = await async_client.post("/api/v1/posts/post", json={"body": body})
    assert response.status_code == 201
    result = response.json()
    # Check that an ID exists and the body is correct
    assert "id" in result and result["body"] == body

@pytest.mark.asyncio
async def test_create_post_missing_data(async_client: AsyncClient) -> None:
    response = await async_client.post("/api/v1/posts/post", json={})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_all_posts(async_client: AsyncClient) -> None:
    # Ensure there's at least one post by creating one
    await create_post(async_client, "first post")
    response = await async_client.get("/api/v1/posts/post")
    assert response.status_code == 200
    posts = response.json()
    assert isinstance(posts, list)
    assert len(posts) > 0

@pytest.mark.asyncio
async def test_create_comment(async_client: AsyncClient) -> None:
    # Create a post to comment on
    post = await create_post(async_client, "post for comment")
    post_id = post["id"]

    # Create a comment for the post
    comment_body = "test comment"
    response = await async_client.post(
        "/api/v1/posts/comment", json={"body": comment_body, "post_id": post_id}
    )
    assert response.status_code == 201
    comment = response.json()
    assert comment["body"] == comment_body
    assert comment["post_id"] == post_id

@pytest.mark.asyncio
async def test_create_comment_invalid_post(async_client: AsyncClient) -> None:
    # Attempt to add a comment for a non-existent post
    comment_body = "test comment"
    invalid_post_id = 999
    response = await async_client.post(
        "/api/v1/posts/comment", json={"body": comment_body, "post_id": invalid_post_id}
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_comments(async_client: AsyncClient) -> None:
    # Create a post and add multiple comments, then fetch them.
    post = await create_post(async_client, "post with comments")
    post_id = post["id"]

    comment_bodies = ["first comment", "second comment"]
    for body in comment_bodies:
        response = await async_client.post(
            "/api/v1/posts/comment", json={"body": body, "post_id": post_id}
        )
        assert response.status_code == 201

    # Fetch comments for the given post
    response = await async_client.get(f"/api/v1/posts/post/{post_id}/comment")
    assert response.status_code == 200
    comments = response.json()
    bodies = [comment["body"] for comment in comments]
    for body in comment_bodies:
        assert body in bodies

@pytest.mark.asyncio
async def test_get_post_with_comments(async_client: AsyncClient) -> None:
    # Create a post and add one comment, then retrieve the post with comments.
    post = await create_post(async_client, "post with single comment")
    post_id = post["id"]
    comment_body = "a comment for post details"
    comment_response = await async_client.post(
        "/api/v1/posts/comment", json={"body": comment_body, "post_id": post_id}
    )
    assert comment_response.status_code == 201

    # Retrieve the post along with its comments
    response = await async_client.get(f"/api/v1/posts/post/{post_id}")
    assert response.status_code == 200
    data = response.json()
    assert "post" in data and "comments" in data
    assert data["post"] == post

    # Verify the comment is present in the list
    comments = data["comments"]
    assert any(comment["body"] == comment_body for comment in comments)
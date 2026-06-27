"""JSONPlaceholder /posts 接口测试 —— CRUD 全场景覆盖。"""

import pytest
from utils.api_client import ApiClient

SAMPLE_POST = {"title": "测试标题", "body": "测试正文内容。", "userId": 1}


class TestPosts:
    """文章资源的增删改查与查询测试。"""

    def test_get_all_posts_returns_list(self, api_client: ApiClient) -> None:
        """GET /posts 返回 200 且列表包含 100 篇文章。"""
        response = api_client.get("/posts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 100

    def test_get_post_by_id(self, api_client: ApiClient) -> None:
        """GET /posts/1 返回预期文章及正确字段。"""
        response = api_client.get("/posts/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "title" in data
        assert "body" in data
        assert "userId" in data

    def test_get_post_not_found_returns_404(self, api_client: ApiClient) -> None:
        """GET /posts/999999 对不存在的文章返回 404。"""
        response = api_client.get("/posts/999999")
        assert response.status_code == 404

    @pytest.mark.smoke
    def test_create_post_returns_201(self, api_client: ApiClient) -> None:
        """POST /posts 创建新文章返回 201 并包含新 id。"""
        response = api_client.post("/posts", json=SAMPLE_POST)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == SAMPLE_POST["title"]
        assert data["userId"] == SAMPLE_POST["userId"]
        assert isinstance(data["id"], int)
        assert data["id"] > 0

    def test_update_post_returns_200(self, api_client: ApiClient) -> None:
        """PUT /posts/1 更新文章字段并返回 200。"""
        updates = {**SAMPLE_POST, "id": 1, "title": "更新后的标题"}
        response = api_client.put("/posts/1", json=updates)
        assert response.status_code == 200
        assert response.json()["title"] == "更新后的标题"

    def test_delete_post_returns_200(self, api_client: ApiClient) -> None:
        """DELETE /posts/1 返回 200（JSONPlaceholder 约定）。"""
        response = api_client.delete("/posts/1")
        assert response.status_code == 200

    def test_filter_posts_by_userid(self, api_client: ApiClient) -> None:
        """GET /posts?userId=1 仅返回属于用户 1 的文章。"""
        response = api_client.get("/posts", params={"userId": 1})
        assert response.status_code == 200
        posts = response.json()
        assert len(posts) > 0
        assert all(p["userId"] == 1 for p in posts)

    @pytest.mark.parametrize("post_id", [1, 2, 3])
    def test_multiple_posts_have_expected_schema(self, api_client: ApiClient, post_id: int) -> None:
        """参数化测试：验证多篇文章的响应结构一致。"""
        response = api_client.get(f"/posts/{post_id}")
        assert response.status_code == 200
        data = response.json()
        assert {"userId", "id", "title", "body"}.issubset(data.keys())

    def test_response_time_within_budget(self, api_client: ApiClient) -> None:
        """GET /posts 在 2 秒内完成响应。"""
        response = api_client.get("/posts")
        assert response.elapsed.total_seconds() < 2.0

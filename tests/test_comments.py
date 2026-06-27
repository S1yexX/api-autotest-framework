"""JSONPlaceholder /comments 接口测试。"""

from utils.api_client import ApiClient


class TestComments:
    """评论资源的查询与结构校验测试。"""

    def test_get_comments_for_post(self, api_client: ApiClient) -> None:
        """GET /posts/1/comments 返回属于文章 1 的评论列表。"""
        response = api_client.get("/posts/1/comments")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert all(c["postId"] == 1 for c in data)

    def test_get_single_comment_by_id(self, api_client: ApiClient) -> None:
        """GET /comments/1 返回 id 为 1 的评论。"""
        response = api_client.get("/comments/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "email" in data
        assert "name" in data
        assert "body" in data

    def test_comment_schema_has_all_required_fields(self, api_client: ApiClient) -> None:
        """验证评论响应包含所有必需字段。"""
        response = api_client.get("/comments/1")
        assert response.status_code == 200
        expected = {"postId", "id", "name", "email", "body"}
        assert expected.issubset(response.json().keys())

    def test_nonexistent_post_comments_returns_empty_list(self, api_client: ApiClient) -> None:
        """GET /posts/999999/comments 返回 200 及空数组。"""
        response = api_client.get("/posts/999999/comments")
        assert response.status_code == 200
        assert response.json() == []

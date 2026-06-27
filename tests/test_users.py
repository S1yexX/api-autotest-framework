"""JSONPlaceholder /users 接口测试。"""

from utils.api_client import ApiClient


class TestUsers:
    """用户资源的查询与校验测试。"""

    def test_get_all_users_returns_list(self, api_client: ApiClient) -> None:
        """GET /users 返回非空用户列表。"""
        response = api_client.get("/users")
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 1

    def test_get_user_by_id_returns_known_user(self, api_client: ApiClient) -> None:
        """GET /users/1 返回已知用户数据。"""
        response = api_client.get("/users/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Leanne Graham"
        assert data["username"] == "Bret"

    def test_get_user_not_found_returns_404(self, api_client: ApiClient) -> None:
        """GET /users/99999 对不存在的用户返回 404。"""
        response = api_client.get("/users/99999")
        assert response.status_code == 404

    def test_user_response_contains_nested_objects(self, api_client: ApiClient) -> None:
        """验证用户响应包含嵌套的 address 和 company 对象。"""
        response = api_client.get("/users/1")
        assert response.status_code == 200
        data = response.json()
        assert "address" in data
        assert "company" in data
        assert "street" in data["address"]
        assert "city" in data["address"]
        assert "name" in data["company"]

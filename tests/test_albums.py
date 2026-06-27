"""JSONPlaceholder /albums 与 /photos 接口测试。"""

from utils.api_client import ApiClient


class TestAlbums:
    """相册资源的查询与校验测试。"""

    def test_get_all_albums_returns_100_items(self, api_client: ApiClient) -> None:
        """GET /albums 返回 200 且恰好 100 个相册。"""
        response = api_client.get("/albums")
        assert response.status_code == 200
        albums = response.json()
        assert isinstance(albums, list)
        assert len(albums) == 100

    def test_get_photos_for_album(self, api_client: ApiClient) -> None:
        """GET /albums/1/photos 返回属于相册 1 的 50 张照片。"""
        response = api_client.get("/albums/1/photos")
        assert response.status_code == 200
        photos = response.json()
        assert isinstance(photos, list)
        assert len(photos) == 50
        assert all(p["albumId"] == 1 for p in photos)

    def test_photo_response_schema(self, api_client: ApiClient) -> None:
        """GET /photos/1 返回包含所有预期字段的照片。"""
        response = api_client.get("/photos/1")
        assert response.status_code == 200
        data = response.json()
        expected = {"albumId", "id", "title", "url", "thumbnailUrl"}
        assert expected.issubset(data.keys())

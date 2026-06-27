"""基于 requests.Session 的轻量 HTTP 客户端封装。

提供 get / post / put / delete 便捷方法，自动拼接 URL，
打印请求/响应摘要。测试用例直接调用，无 YAML 加载、
JSONPath 提取或 Allure 集成。
"""

from dataclasses import dataclass

import requests


@dataclass
class ApiConfig:
    """API 客户端配置。"""

    base_url: str
    timeout: int = 10
    default_headers: dict | None = None


class ApiClient:
    """共享 HTTP 客户端，复用 Session 并提供便捷方法。"""

    def __init__(self, config: ApiConfig) -> None:
        self.config = config
        self.session = requests.Session()
        headers = config.default_headers or {}
        headers.setdefault("Content-Type", "application/json")
        self.session.headers.update(headers)

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.config.base_url.rstrip('/')}{path}"
        kwargs.setdefault("timeout", self.config.timeout)
        response = self.session.request(method, url, **kwargs)
        print(f"\n>>> {method} {url}")
        print(f"<<< {response.status_code} ({response.elapsed.total_seconds():.3f}s)")
        return response

    def get(self, path: str, **kwargs) -> requests.Response:
        """发送 GET 请求，path 例如 '/posts/1'。"""
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        """发送 POST 请求。"""
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        """发送 PUT 请求。"""
        return self._request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        """发送 DELETE 请求。"""
        return self._request("DELETE", path, **kwargs)

    def close(self) -> None:
        """关闭底层 requests 会话。"""
        self.session.close()

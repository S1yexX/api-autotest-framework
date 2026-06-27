"""所有 API 测试的共享 fixture。"""

import pytest
from utils.api_client import ApiClient, ApiConfig

BASE_URL = "https://jsonplaceholder.typicode.com"


@pytest.fixture(scope="session")
def api_client():
    """创建全局复用的 ApiClient 实例，测试结束后自动关闭。"""
    config = ApiConfig(base_url=BASE_URL, timeout=10)
    client = ApiClient(config)
    yield client
    client.close()

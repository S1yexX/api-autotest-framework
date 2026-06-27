import requests
import json
from typing import Any, Dict, cast

from test_framework.logger import log_http
from test_framework.variable_extractor import recursive_replace


class HttpClient:
    """
    封装 Requests 库，提供以下能力：
    - Session 复用（连接池、Cookie 持久化）
    - 全局变量池 session_vars，实现跨用例接口关联
    - 请求前自动递归替换 ${变量} 占位符
    - 完整的请求/响应报文日志
    """

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url: str = base_url.rstrip("/")
        self.timeout: int = timeout
        self.session: requests.Session = requests.Session()
        # 全局用例变量池，session 级别共享，实现接口关联（如 token/id 传递）
        self.session_vars: Dict[str, Any] = {}

    def request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        # 递归替换请求内所有 ${变量} 占位符
        url = cast(str, recursive_replace(url, self.session_vars))
        kwargs = cast(dict, recursive_replace(kwargs, self.session_vars))

        # 如果 YAML 中已是绝对 URL（如 httpbin），则不拼接 base_url
        if url.startswith("http://") or url.startswith("https://"):
            full_url: str = url
        else:
            full_url = f"{self.base_url}{url}"

        # ===== 记录请求 =====
        log_http("===== 发起请求 =====")
        log_http(f"METHOD: {method.upper()}")
        log_http(f"URL: {full_url}")
        if kwargs.get("headers"):
            log_http(f"HEADERS: {kwargs['headers']}")
        if kwargs.get("json"):
            log_http(f"REQUEST BODY: {json.dumps(kwargs['json'], ensure_ascii=False)}")
        elif kwargs.get("data"):
            log_http(f"REQUEST DATA: {kwargs['data']}")

        # ===== 发送请求 =====
        try:
            resp = self.session.request(
                method=method,
                url=full_url,
                timeout=self.timeout,
                **kwargs,
            )
        except requests.exceptions.Timeout:
            log_http(f"请求超时 (>{self.timeout}s): {method.upper()} {full_url}")
            raise
        except requests.exceptions.ConnectionError:
            log_http(f"连接失败: {method.upper()} {full_url}")
            raise
        except requests.exceptions.RequestException as e:
            log_http(f"请求异常: {str(e)}")
            raise

        # ===== 记录响应 =====
        log_http("===== 响应结果 =====")
        log_http(f"STATUS CODE: {resp.status_code}")
        log_http(f"RESPONSE TIME: {resp.elapsed.total_seconds():.3f}s")
        log_http(f"RESPONSE BODY: {resp.text[:1000]}")
        return resp

from typing import Any, Dict, List

from jsonpath import search


def validate_response(resp, assertions: dict) -> bool:
    """
    根据断言规则验证 HTTP 响应。

    支持断言维度：
    - status_code: 状态码精确匹配
    - json: JSON 字段值匹配（支持 JSONPath 路径）
    - max_response_time: 响应时间上限（秒）

    :param resp: requests 响应对象
    :param assertions: YAML 中的 assert 字典
    :return: 校验通过返回 True
    :raises AssertionError: 校验失败时抛出，包含所有不匹配项详情
    """
    errors: List[str] = []
    resp_json: Dict[str, Any] = resp.json() if resp.content else {}

    # 1. 状态码断言
    if "status_code" in assertions:
        expected: int = assertions["status_code"]
        actual: int = resp.status_code
        if expected != actual:
            errors.append(f"状态码不匹配: 期望 {expected}, 实际 {actual}")

    # 2. JSON 字段断言
    if "json" in assertions:
        for field, expected_val in assertions["json"].items():
            path: str = f"$.{field}"
            actual_result = search(path, resp_json)
            if actual_result:
                actual_val = actual_result[0]
                if actual_val != expected_val:
                    errors.append(
                        f"字段 '{field}' 校验失败: 期望 '{expected_val}', 实际 '{actual_val}'"
                    )
            else:
                errors.append(f"字段 '{field}' 不存在于响应中 (JSONPath: {path})")

    # 3. 响应时间断言
    if "max_response_time" in assertions:
        max_time: float = assertions["max_response_time"]
        actual_time: float = resp.elapsed.total_seconds()
        if actual_time > max_time:
            errors.append(f"响应超时: 限制 {max_time}s, 实际 {actual_time:.3f}s")

    if errors:
        raise AssertionError("\n".join(errors))

    return True

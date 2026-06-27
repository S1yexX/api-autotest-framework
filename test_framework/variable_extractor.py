from typing import Any, Dict

from jsonpath import search


def extract_variable(response, extract_rule: dict) -> Any:
    """
    从响应中按 JSONPath 提取变量值。

    :param response: requests 响应对象
    :param extract_rule: {"name": "post_id", "jsonpath": "$.id"}
    :return: 提取到的第一个匹配值
    """
    # 安全解析 JSON：非 2xx 响应可能返回 HTML 而非 JSON
    try:
        resp_json = response.json()
    except Exception:
        raise ValueError(
            f"变量提取失败，响应非 JSON 格式 (status={response.status_code})"
        )
    path: str = extract_rule["jsonpath"]
    result = search(path, resp_json)
    if not result:
        raise ValueError(f"变量提取失败，JSONPath '{path}' 无匹配数据")
    return result[0]


def replace_variable_str(text: str, var_pool: Dict[str, Any]) -> Any:
    """
    对单个字符串执行 ${key} → 值 的替换。

    规则：
    - 若整个字符串就是 "${key}"，则返回变量原始类型（int/str/float 等）
    - 若 ${key} 是子串（如 "/posts/${id}"），则执行字符串替换
    - 非字符串或空值原样返回
    """
    if not text or not isinstance(text, str):
        return text
    for k, v in var_pool.items():
        placeholder = f"${{{k}}}"
        if text == placeholder:
            return v  # 保留原始类型（int → int, str → str）
        text = text.replace(placeholder, str(v))
    return text


def recursive_replace(data: Any, var_pool: Dict[str, Any]) -> Any:
    """
    递归遍历 dict / list / str，将其中所有 ${key} 占位符替换为变量池中的值。

    支持场景：
    - url 中的 ${post_id}
    - json body 中任意深度的 ${token}
    - headers 中的 ${auth_token}
    """
    if isinstance(data, str):
        return replace_variable_str(data, var_pool)
    elif isinstance(data, dict):
        new_dict: dict = {}
        for k, v in data.items():
            new_dict[k] = recursive_replace(v, var_pool)
        return new_dict
    elif isinstance(data, list):
        new_list: list = []
        for item in data:
            new_list.append(recursive_replace(item, var_pool))
        return new_list
    return data

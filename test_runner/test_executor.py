from contextlib import AbstractContextManager
from typing import Any, Dict, List, cast

import allure

from test_framework.response_validator import validate_response
from test_framework.variable_extractor import extract_variable, recursive_replace


def _step(title: str) -> AbstractContextManager[None]:
    """allure.step 的类型安全包装 — allure-pytest 无类型存根时消除 Pyright 报错。"""
    return allure.step(title)  # type: ignore[return-value]


def test_api(http_client: Any, yaml_case: Dict[str, Any]) -> None:
    """
    通用 YAML 驱动测试执行器 —— 框架唯一的测试函数。

    所有 YAML 用例均通过此函数执行，流程：
    1. 设置 Allure 报告元数据（epic/feature/story/title）
    2. 发送 HTTP 请求（自动替换 ${变量}）
    3. 提取响应变量存入全局变量池（接口关联）
    4. 执行响应断言校验
    """
    case_name: str = yaml_case["name"]
    allure_meta: Dict[str, str] = yaml_case.get("allure", {})

    # 设置 Allure 报告分层信息
    allure.dynamic.epic(allure_meta.get("epic", "未分类模块"))
    allure.dynamic.feature(allure_meta.get("feature", "未分类功能"))
    allure.dynamic.story(allure_meta.get("story", "未分类场景"))
    allure.dynamic.title(case_name)
    allure.attach(
        str(yaml_case),
        name="完整 YAML 用例",
        attachment_type=allure.attachment_type.TEXT,
    )

    # 获取请求参数
    req_params: Dict[str, Any] = yaml_case["request"]

    # Step 1: 发送 HTTP 请求
    with _step(f"发送 {req_params.get('method', 'GET').upper()} 请求"):
        resp = http_client.request(**req_params)

    # Step 2: 提取变量存入全局变量池
    extract_rules: List[dict] = yaml_case.get("extract", [])
    if extract_rules:
        with _step("提取接口返回变量"):
            for rule in extract_rules:
                var_name: str = rule["name"]
                var_value: Any = extract_variable(resp, rule)
                http_client.session_vars[var_name] = var_value
                allure.attach(
                    f"{var_name} = {var_value}",
                    name=f"提取变量 - {var_name}",
                )

    # Step 3: 执行断言校验（替换断言中的 ${变量} 后再校验）
    assert_rules_raw: Dict[str, Any] = yaml_case.get("assert", {})
    if assert_rules_raw:
        assert_rules = cast(
            dict,
            recursive_replace(assert_rules_raw, http_client.session_vars),
        )
        with _step("执行响应断言校验"):
            validate_response(resp, assert_rules)

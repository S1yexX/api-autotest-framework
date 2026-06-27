from typing import Any, Dict, Generator, List, Set, cast

import pytest
import yaml

from test_framework.http_client import HttpClient
from test_framework.yaml_loader import load_yaml_cases


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--env", default="dev", help="测试环境: dev / staging")
    parser.addoption("--cases", default="testcases", help="YAML用例根目录")


@pytest.fixture(scope="session")
def env_config(request: pytest.FixtureRequest) -> Dict[str, Any]:
    """加载环境配置（dev / staging）"""
    env: str = cast(str, request.config.getoption("--env"))
    env_file: str = f"config/env/{env}.yaml"
    with open(env_file, encoding="utf-8") as f:
        config: Dict[str, Any] = yaml.safe_load(f)
    return config


@pytest.fixture(scope="session")
def http_client(env_config: Dict[str, Any]) -> Generator[HttpClient, None, None]:
    """
    创建 Session 级别的全局 HTTP 客户端。
    整个测试会话共享同一个 Session 实例，实现：
    - TCP 连接池复用
    - Cookie 自动保持
    - session_vars 跨用例变量共享
    """
    client: HttpClient = HttpClient(
        base_url=env_config["base_url"],
        timeout=env_config.get("timeout", 30),
    )
    yield client
    client.session.close()


def _get_mark_expression(metafunc: pytest.Metafunc) -> str:
    """安全获取 -m 参数值，兼容不同 pytest 版本。"""
    # pytest 内部用 "markexpr" 存储 -m 参数
    try:
        return cast(str, metafunc.config.getoption("markexpr"))
    except (ValueError, AttributeError):
        pass
    # 回退：尝试直接读 -m
    try:
        return cast(str, metafunc.config.getoption("-m"))
    except (ValueError, AttributeError):
        pass
    return ""


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """
    动态参数化测试用例生成（pytest 钩子）。

    从 YAML 目录自动加载所有用例，无需为每个模块手写 Python 测试函数。
    将 YAML 中所有唯一 tags 注册为 pytest marker，支持 -m 筛选。
    当指定 -m smoke 时，仅加载 tags 中包含 "smoke" 的用例。
    """
    if "yaml_case" not in metafunc.fixturenames:
        return

    case_dir: str = cast(str, metafunc.config.getoption("--cases"))
    all_cases: List[Dict[str, Any]] = load_yaml_cases(case_dir)

    if not all_cases:
        pytest.skip(f"用例目录 '{case_dir}' 中未找到任何 YAML 用例")

    # 根据 -m 参数过滤用例（如 -m smoke 只保留 tags 含 "smoke" 的用例）
    mark_expr: str = _get_mark_expression(metafunc)
    if mark_expr:
        selected_cases = [
            case for case in all_cases
            if mark_expr in case.get("tags", [])
        ]
        if selected_cases:
            all_cases = selected_cases

    # 收集所有唯一标签，注册为 pytest marker
    all_tags: Set[str] = set()
    for case in all_cases:
        for tag in case.get("tags", []):
            all_tags.add(tag)

    # 初始化函数级 pytestmark（如果尚未存在）
    if not hasattr(metafunc.function, "pytestmark"):
        metafunc.function.pytestmark = []  # type: ignore[attr-defined]

    for tag in sorted(all_tags):
        metafunc.function.pytestmark.append(getattr(pytest.mark, tag))  # type: ignore[attr-defined]

    metafunc.parametrize(
        "yaml_case",
        all_cases,
        ids=[item["name"] for item in all_cases],
    )

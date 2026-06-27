# JSONPlaceholder 接口自动化测试

[![API Tests](https://github.com/S1yexX/api-autotest-framework/actions/workflows/test.yml/badge.svg)](https://github.com/S1yexX/api-autotest-framework/actions/workflows/test.yml)

基于 **pytest + Requests** 的接口自动化测试项目，测试目标为
[JSONPlaceholder](https://jsonplaceholder.typicode.com) 公开 REST API。

> 项目结构简洁、注释完善，适合作为实习简历中的实战项目展示。

## 测试范围

| 接口 | 覆盖内容 |
|------|----------|
| `/posts` | 增删改查、过滤查询、异常场景 |
| `/comments` | 按文章查询、按 ID 查询、响应结构校验 |
| `/users` | 全量查询、按 ID 查询、嵌套对象校验、404 处理 |
| `/albums` / `/photos` | 列表查询、关联过滤、响应结构校验 |

## 技术栈

- **pytest** — 测试框架与断言
- **requests** — HTTP 客户端，复用 Session
- **pytest-html** — 自包含 HTML 测试报告

没有 YAML 驱动、没有 Allure、没有多余依赖 —— 直接写 Python 测试。

## 快速开始

```bash
# 克隆项目
git clone https://github.com/S1yexX/api-autotest-framework.git
cd api-autotest-framework

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# 安装依赖
pip install -r requirements.txt

# 运行全部测试
pytest

# 仅运行冒烟测试
pytest -m smoke

# 打开 HTML 报告
open reports/report.html
```

## 项目结构

```
.
├── tests/               # pytest 测试用例（按接口资源拆分）
│   ├── conftest.py      # 共享 fixture（API 客户端初始化/清理）
│   ├── test_posts.py    # 文章 CRUD 测试
│   ├── test_comments.py # 评论查询测试
│   ├── test_users.py    # 用户查询测试
│   └── test_albums.py   # 相册与照片测试
├── utils/               # 通用工具模块
│   └── api_client.py    # 轻量 requests.Session 封装
├── reports/             # 生成的 HTML 报告（已 gitignore）
├── .github/workflows/   # GitHub Actions CI 流水线
├── requirements.txt     # Python 依赖
├── pytest.ini           # pytest 配置
└── README.md            # 本文件
```

## 关键实践

- **关注点分离**：测试逻辑在 `tests/`，公共设施在 `utils/`
- **Session 复用**：通过 `conftest.py` 提供全局复用的 `requests.Session`
- **CRUD 全覆盖**：posts 接口覆盖 GET / POST / PUT / DELETE 全部方法
- **异常场景**：不存在资源返回 404、越界查询返回空列表
- **结构校验**：断言响应 JSON 的必需字段完整
- **参数化测试**：使用 `@pytest.mark.parametrize` 实现数据驱动
- **性能断言**：通过 `response.elapsed` 校验响应时间
- **CI 集成**：push / PR 自动触发 GitHub Actions 执行测试

## CI/CD

`.github/workflows/test.yml` 在每次 push 和 PR 到 `main` 分支时自动运行全部测试，
HTML 报告可在 Actions 页面下载。

## License

MIT

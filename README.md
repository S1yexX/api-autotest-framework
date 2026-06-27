# YAML 零代码接口自动化测试框架

[![API Auto Test CI](https://github.com/S1yexX/api-autotest-framework/actions/workflows/test.yml/badge.svg)](https://github.com/S1yexX/api-autotest-framework/actions/workflows/test.yml)

## 项目简介

基于 **pytest + Requests + YAML + Allure** 打造轻量化零代码接口自动化框架。测试人员仅需编写 YAML 用例即可完成接口回归测试，**无需编写一行 Python 代码**。

内置多环境切换、跨用例接口关联（token/ID 传递）、JSONPath 变量提取、多维度断言、HTTP 报文日志持久化、Allure 分层可视化报告、GitHub Actions CI 定时自动回归。

> 本项目适合作为 **简历 GitHub 开源实战项目**，涵盖接口自动化全链路工程实践。

## 技术栈

| 技术 | 用途 |
|------|------|
| **pytest** | 测试框架，参数化驱动 |
| **Requests** | HTTP 请求库 |
| **PyYAML** | YAML 用例解析 |
| **jsonpath** | JSON 响应字段提取 |
| **Allure** | 可视化测试报告 |
| **GitHub Actions** | CI/CD 持续集成 |

## 目录架构

```
api-autotest-framework/
├── config/                         # 全局 + 多环境配置
│   ├── settings.yaml               # 框架全局配置
│   └── env/
│       ├── dev.yaml                # 开发环境（JSONPlaceholder）
│       └── staging.yaml            # 预发环境（Reqres）
├── testcases/                      # YAML 测试用例（零代码核心）
│   ├── jsonplaceholder/
│   │   ├── posts.yaml              # 文章 CRUD 用例
│   │   ├── comments.yaml           # 评论查询用例
│   │   └── users.yaml              # 用户管理用例
│   ├── reqres/
│   │   └── users.yaml              # Reqres 用户用例
│   └── httpbin/
│       └── debug.yaml              # Httpbin 调试用例
├── test_framework/                 # 底层核心引擎
│   ├── __init__.py
│   ├── http_client.py              # Requests 封装（Session + 日志 + 变量替换）
│   ├── yaml_loader.py              # YAML 用例加载器
│   ├── response_validator.py       # 响应断言引擎
│   ├── variable_extractor.py       # JSONPath 变量提取 + 递归替换
│   └── logger.py                   # HTTP 报文日志模块
├── test_runner/                    # pytest 执行层
│   ├── __init__.py
│   ├── conftest.py                 # Fixture + 动态用例生成
│   └── test_executor.py            # 通用测试执行器
├── test_data/                      # Excel 数据驱动文件（预留）
├── reports/                        # 测试报告输出
├── logs/                           # 接口运行日志
├── .github/workflows/
│   └── test.yml                    # CI 自动执行流水线
├── pytest.ini                      # pytest 配置
├── requirements.txt                # 依赖清单
└── README.md                       # 项目文档
```

## 快速上手

### 1. 环境准备

```bash
# 克隆仓库
git clone https://github.com/S1yexX/api-autotest-framework.git
cd api-autotest-framework

# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r requirements.txt
```

### 2. 执行用例

```bash
# 执行 dev 环境全部用例
pytest test_runner/ --env dev

# 仅执行冒烟用例
pytest test_runner/ --env dev -m smoke

# 按模块筛选（文章模块）
pytest test_runner/ --env dev -m posts

# 指定用例目录
pytest test_runner/ --env dev --cases testcases/reqres

# 并行执行（4 线程）
pytest test_runner/ --env dev -n 4
```

### 3. 生成 Allure 报告

```bash
# 执行用例并生成报告数据
pytest test_runner/ --env dev --alluredir=reports/allure-results

# 生成 HTML 报告
allure generate reports/allure-results -o reports/allure-report --clean

# 打开报告
allure open reports/allure-report
```

## YAML 用例编写规范

### 完整示例

```yaml
- name: "创建文章-正常场景"         # 用例名称（必填）
  tags: ["smoke", "posts", "positive"]  # 标签，支持 pytest -m 筛选
  allure:                               # Allure 报告分层（可选）
    epic: "JSONPlaceholder"
    feature: "文章管理"
    story: "新增文章"
  request:                              # HTTP 请求配置（必填）
    method: POST
    url: "/posts"
    json:
      title: "自动化测试文章"
      body: "YAML驱动接口自动化框架演示"
      userId: 1
  extract:                              # 变量提取（可选）
    - name: post_id                     # 变量名
      jsonpath: "$.id"                  # JSONPath 表达式
  assert:                               # 断言规则（可选）
    status_code: 201                    # 状态码断言
    json:                               # JSON 字段断言
      userId: 1
    max_response_time: 3                # 响应时间上限（秒）
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | ✅ | 用例名称，显示在 pytest 输出和 Allure 报告 |
| `tags` | - | 标签列表，用于 `pytest -m` 筛选 |
| `allure` | - | Allure 报告分层：epic / feature / story |
| `request` | ✅ | HTTP 请求：method、url、headers、params、json、data |
| `extract` | - | JSONPath 提取响应值，存入全局变量池 |
| `assert` | - | 断言：status_code、json、max_response_time |

### 变量引用（接口关联）

在 YAML 中通过 `${变量名}` 引用之前提取的变量：

```yaml
# 用例1：提取 post_id
- name: "创建文章"
  request:
    method: POST
    url: "/posts"
    json: { ... }
  extract:
    - name: post_id
      jsonpath: "$.id"

# 用例2：使用 post_id
- name: "查询文章"
  request:
    method: GET
    url: "/posts/${post_id}"    # 自动替换为实际 ID
  assert:
    status_code: 200
```

## 核心功能

- ✅ **零代码用例维护** — 纯 YAML 编写，无需 Python 代码
- ✅ **跨用例接口关联** — Session 级全局变量池，支持 token/ID 传递
- ✅ **多环境一键切换** — `--env dev|staging`
- ✅ **完整 HTTP 日志** — 请求/响应报文按天持久化落盘
- ✅ **多维度断言** — 状态码、JSON 字段、响应耗时
- ✅ **Allure 分层报告** — epic/feature/story 分组，自动附加请求报文和提取变量
- ✅ **GitHub Actions CI** — 提交触发 + 工作日定时自动执行 + 报告归档

## CI 持续集成

流水线配置：`.github/workflows/test.yml`

| 触发方式 | 说明 |
|----------|------|
| `push` | main 分支推送自动执行 |
| `pull_request` | PR 合入前自动回归 |
| `schedule` | 工作日 8:00 定时全量回归 |

CI 执行完成后，可在 Actions 页面下载 Allure 报告产物。

## 扩展方向

- [ ] 接口签名 / 鉴权 Token 统一封装
- [ ] 数据库结果校验模块
- [ ] Excel 数据驱动（已预留 `test_data/` 目录）
- [ ] 失败自动重试（已引入 tenacity）
- [ ] 钉钉 / 邮件测试结果通知
- [ ] 多线程分布式执行（已引入 pytest-xdist）

## License

MIT

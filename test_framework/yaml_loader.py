from pathlib import Path
from typing import Any, Dict, List, Union

import yaml


def load_yaml_cases(case_dir: str) -> List[Dict[str, Any]]:
    """
    递归加载目录下所有 YAML 用例文件，返回扁平化用例列表。
    每个用例自动附加 _source_file 字段标记来源文件。
    """
    all_cases: List[Dict[str, Any]] = []
    case_path = Path(case_dir)

    if not case_path.exists():
        raise FileNotFoundError(f"用例目录不存在: {case_dir}")

    for yaml_file in case_path.rglob("*.yaml"):
        with open(yaml_file, encoding="utf-8") as f:
            cases: Union[list, dict, None] = yaml.safe_load(f)
            if not cases:
                continue
            # 兼容单个用例和用例列表两种格式
            if isinstance(cases, dict):
                cases = [cases]
            for case in cases:
                case["_source_file"] = str(yaml_file.relative_to(case_dir))
            all_cases.extend(cases)

    return all_cases

"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": "Delegate when requirements, shared code dependencies, or dirty data need investigation before implementation.",
            "system_prompt": "You investigate only. Read the supplied requirements, README, docstrings and relevant files. Identify root causes, data quality issues and edge cases. Do not modify files. Return concise findings with file paths and evidence, and state any missing context.",
        },
        {
            "name": "implementer",
            "description": "Delegate when a diagnosed issue needs code changes or a reproducible data/log processing script and verification.",
            "system_prompt": "Implement the delegated task within its supplied scope. Read requirements first, fix shared root causes, and handle malformed data explicitly. Run relevant tests or validate generated outputs. Report only actual changes, commands and observed results; disclose remaining failures.",
        },
        {
            "name": "reviewer",
            "description": "Delegate before completion when changes or output files need an independent requirements and edge-case review.",
            "system_prompt": "Review independently without modifying files. Compare actual artifacts with every supplied requirement, README and docstring. Run relevant checks and examine edge cases. Return evidence for each defect and distinguish verified results from assumptions.",
        },
    ]

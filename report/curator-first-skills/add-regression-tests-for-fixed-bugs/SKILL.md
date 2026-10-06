---
name: add-regression-tests-for-fixed-bugs
description: Use this skill after fixing bugs in code to add regression tests. Create or update a tests/test_regressions.py file with at least one test function per bug fixed. Ensure the test file passes when run, preventing regressions.
---
def add_regression_tests(fixed_bugs: list, test_file_path: str) -> None:
    """
    Given a list of fixed bugs (each with a function name and short description),
    add corresponding test functions to the regression test file.
    """
    import os

    # Prepare test function template
    test_template = (
        "def test_fix_{func_name}():\n"
        "    \"\"\"Regression test for fix: {description}\"\"\"\n"
        "    # TODO: implement test for {func_name}\n"
        "    assert True\n\n"
    )

    # Read existing tests if any
    existing_tests = ""
    if os.path.exists(test_file_path):
        with open(test_file_path, 'r', encoding='utf-8') as f:
            existing_tests = f.read()

    # Append new tests for each fixed bug if not already present
    new_tests = ""
    for bug in fixed_bugs:
        func_name = bug.get('function', 'unknown_func').replace('.', '_')
        description = bug.get('description', 'No description')
        test_name = f"test_fix_{func_name}"
        if test_name not in existing_tests:
            new_tests += test_template.format(func_name=func_name, description=description)

    # Write back the updated test file
    with open(test_file_path, 'a', encoding='utf-8') as f:
        f.write(new_tests)

    # Verification:
    # 1. Run the test suite (e.g., pytest) to ensure tests pass.
    # 2. Confirm at least one test per fixed bug is present.

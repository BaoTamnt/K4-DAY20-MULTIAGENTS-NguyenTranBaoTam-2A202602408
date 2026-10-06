---
name: write-meaningful-regression-tests-for-fixed-bugs
description: Use this skill when adding regression tests after fixing bugs. Write at least one test function per bug fixed, placing them in a dedicated regression test file. Tests must call real functions with meaningful assertions that verify the bug fix.
---
- Create or open the file `tests/test_regressions.py`.
- For each bug fixed:
  - Write a test function named descriptively (e.g., `test_<bug_description>`).
  - The test must:
    - Call the actual function(s) involved in the bug.
    - Use realistic input data that triggers the previously failing behavior.
    - Assert expected outputs or side effects that confirm the bug is fixed.
  - Avoid placeholder tests or trivial assertions like `assert True`.
- Ensure tests cover edge cases related to the bug.
- Run the full test suite to verify all regression tests pass.
- Confirm the regression test file is included in the test discovery.
- Document the bug fix briefly in the test function’s docstring or comments.

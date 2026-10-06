---
name: enforce-type-hints-on-public-functions
description: Use this skill when reviewing or writing Python packages to ensure every public function (not starting with '_') has complete type annotations on all parameters and the return value. This improves code clarity, tooling support, and maintainability.
---
- Identify all public functions in the package (functions whose names do not start with an underscore).
- For each public function:
  - Check that every parameter has a type annotation.
  - Check that the function has a return type annotation.
- If any parameter or the return type is missing an annotation:
  - Add the appropriate type hint based on the function’s logic or documentation.
- Use standard typing constructs (e.g., `int`, `str`, `Optional`, `List`, `Dict`) as needed.
- Verify annotations are syntactically correct and import any required types from `typing`.
- Run a static type checker (e.g., `mypy`) on the package to confirm no missing or incompatible annotations.
- Confirm that all public functions now have full type hints.
- Document any assumptions or complex types in docstrings if necessary.

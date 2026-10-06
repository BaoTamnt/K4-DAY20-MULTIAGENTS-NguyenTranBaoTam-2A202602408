---
name: enforce-public-function-type-hints
description: Use this skill when reviewing or writing Python packages to ensure every public function (whose name does not start with '_') has complete type annotations on all parameters and the return value. This helps maintain code clarity and type safety.
---
def enforce_public_function_type_hints(source_code: str) -> list:
    """
    Check that all public functions in the given Python source code have type hints on all parameters and the return type.
    Returns a list of function names missing annotations.
    """
    import ast

    missing_annotations = []
    tree = ast.parse(source_code)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Skip private functions starting with '_'
            if node.name.startswith('_'):
                continue

            # Check parameters for annotations
            params = node.args.args + node.args.kwonlyargs
            # Also check vararg and kwarg if present
            if node.args.vararg:
                params.append(node.args.vararg)
            if node.args.kwarg:
                params.append(node.args.kwarg)

            params_missing = any(p.annotation is None for p in params)
            return_missing = node.returns is None

            if params_missing or return_missing:
                missing_annotations.append(node.name)

    return missing_annotations


def verify_type_hints(source_code: str) -> bool:
    """
    Verify that no public function is missing type hints.
    """
    missing = enforce_public_function_type_hints(source_code)
    return len(missing) == 0


# Verification steps:
# 1. Parse the source code of the package.
# 2. Identify all public functions (names not starting with '_').
# 3. Check that each parameter and the return value have type annotations.
# 4. Report any functions missing annotations.
# 5. Fix by adding appropriate type hints.

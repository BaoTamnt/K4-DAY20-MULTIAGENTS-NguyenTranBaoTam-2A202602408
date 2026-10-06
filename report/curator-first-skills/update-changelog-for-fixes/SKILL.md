---
name: update-changelog-for-fixes
description: Use this skill after fixing bugs to update the CHANGELOG.md file. Under the '## Unreleased' heading, add bullet points for each fix in the format '- fix(<function name>): <short description>'. Ensure at least three bullets for multiple fixes.
---
def update_changelog(fixes: list, changelog_path: str) -> None:
    """
    Add entries for each fix under the '## Unreleased' section in CHANGELOG.md.
    """
    import re

    # Read existing changelog content
    with open(changelog_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find '## Unreleased' section
    unreleased_match = re.search(r'(## Unreleased\s*\n)', content)
    if not unreleased_match:
        # If no Unreleased section, add it at the top
        content = "## Unreleased\n\n" + content
        unreleased_pos = len("## Unreleased\n")
    else:
        unreleased_pos = unreleased_match.end()

    # Prepare fix entries
    fix_lines = ""
    for fix in fixes:
        func_name = fix.get('function', 'unknown_func')
        description = fix.get('description', 'No description')
        line = f"- fix({func_name}): {description}\n"
        if line not in content:
            fix_lines += line

    if fix_lines:
        # Insert fix lines after '## Unreleased' heading
        content = content[:unreleased_pos] + fix_lines + content[unreleased_pos:]

    # Write back updated changelog
    with open(changelog_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Verification:
    # 1. Confirm '## Unreleased' section exists.
    # 2. Confirm at least one bullet per fix is present.
    # 3. Confirm format matches '- fix(<function name>): <short description>'.

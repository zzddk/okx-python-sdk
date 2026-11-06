"""Guard against silently shadowed tests in the unit suite.

Python lets a later class (or method) redefine an earlier one in the same
scope; pytest then collects only the last definition, so a duplicate name can
make a whole test case disappear without any error. ruff's F811 flags the
obvious case, but this guard states the intent directly and names both the
file and the duplicate name when it fails.
"""
import ast
import unittest
from pathlib import Path

# This file lives in test/unit/okxsdk/, so parents[1] is test/unit/.
UNIT_ROOT = Path(__file__).resolve().parents[1]


def _duplicate_names(names):
    """Return the sorted names that occur more than once in `names`."""
    seen = set()
    duplicates = set()
    for name in names:
        if name in seen:
            duplicates.add(name)
        seen.add(name)
    return sorted(duplicates)


class TestNoDuplicateTestClasses(unittest.TestCase):
    """No duplicate class names per file, no duplicate method names per class."""

    def test_no_duplicate_class_or_method_names(self):
        problems = []
        for path in sorted(UNIT_ROOT.rglob("*.py")):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"),
                                 filename=str(path))
            except SyntaxError:
                # A file that does not parse cannot shadow a collected test;
                # leave that to pytest's own collection to report.
                continue

            # A second module-level class with the same name shadows the first.
            class_names = [
                node.name for node in tree.body
                if isinstance(node, ast.ClassDef)
            ]
            for name in _duplicate_names(class_names):
                problems.append(f"{path}: duplicate class name {name!r}")

            # A second method with the same name shadows the first in a class.
            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                method_names = [
                    child.name for child in node.body
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                for name in _duplicate_names(method_names):
                    problems.append(
                        f"{path}: duplicate method name {name!r} "
                        f"in class {node.name!r}"
                    )

        self.assertFalse(
            problems,
            "Duplicate definitions silently drop collected tests:\n"
            + "\n".join(problems),
        )


if __name__ == '__main__':
    unittest.main()

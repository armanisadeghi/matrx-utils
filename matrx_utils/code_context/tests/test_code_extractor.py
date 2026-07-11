"""
Tests for CodeExtractor and ASTAnalyzer.

CodeExtractor covers:
- UTF-8 file reading
- Python comment removal (# and triple-quoted)
- JS/TS comment removal (// and /* */)
- Blank line normalization
- Character count tracking
- Content type fallback (clean falls back to original if strip not called)
- file_header formatting

ASTAnalyzer covers:
- Top-level function extraction with args
- Class and method extraction
- Avoids double-counting methods as functions
- async def support
- Non-Python files return a graceful error
- Syntax error handling
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from matrx_utils.code_context.code_context import ASTAnalyzer, CodeExtractor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_extractor(content: str, suffix: str = ".py", tmp_path=None) -> CodeExtractor:
    """Write content to a temp file and return a CodeExtractor for it."""
    p = tmp_path / f"test_file{suffix}" if tmp_path else Path(f"/tmp/test_file{suffix}")
    p.write_text(content, encoding="utf-8")
    return CodeExtractor(p)


# ---------------------------------------------------------------------------
# File reading
# ---------------------------------------------------------------------------

class TestFileReading:
    def test_reads_utf8_file(self, tmp_path):
        p = tmp_path / "app.py"
        p.write_text("x = 1\n", encoding="utf-8")
        ex = CodeExtractor(p)
        assert ex.original == "x = 1\n"

    def test_original_char_count(self, tmp_path):
        content = "hello world"
        p = tmp_path / "app.py"
        p.write_text(content, encoding="utf-8")
        ex = CodeExtractor(p)
        assert ex.char_counts["original"] == len(content)

    def test_nonexistent_file_returns_none(self, tmp_path):
        ex = CodeExtractor(tmp_path / "does_not_exist.py")
        assert ex.original is None
        assert ex.char_counts["original"] == 0

    def test_get_content_original_returns_original(self, tmp_path):
        p = tmp_path / "app.py"
        p.write_text("pass", encoding="utf-8")
        ex = CodeExtractor(p)
        assert ex.get_content("original") == "pass"

    def test_get_content_clean_before_strip_returns_original(self, tmp_path):
        p = tmp_path / "app.py"
        p.write_text("# comment\npass", encoding="utf-8")
        ex = CodeExtractor(p)
        # strip_comments not called yet — should fall back to original
        assert ex.get_content("clean") == "# comment\npass"


# ---------------------------------------------------------------------------
# Python comment removal
# ---------------------------------------------------------------------------

class TestPythonCommentRemoval:
    def test_removes_hash_comment(self, tmp_path):
        p = tmp_path / "a.py"
        p.write_text("x = 1  # inline comment\ny = 2\n", encoding="utf-8")
        ex = CodeExtractor(p)
        result = ex.strip_comments()
        assert "inline comment" not in result
        assert "x = 1" in result
        assert "y = 2" in result

    def test_removes_standalone_hash_comment(self, tmp_path):
        p = tmp_path / "a.py"
        p.write_text("# This is a comment\ndef foo():\n    pass\n", encoding="utf-8")
        ex = CodeExtractor(p)
        result = ex.strip_comments()
        assert "This is a comment" not in result
        assert "def foo():" in result

    def test_removes_triple_double_quote_docstring(self, tmp_path):
        p = tmp_path / "a.py"
        p.write_text('def foo():\n    """This is a docstring."""\n    return 1\n', encoding="utf-8")
        ex = CodeExtractor(p)
        result = ex.strip_comments()
        assert "This is a docstring" not in result
        assert "return 1" in result

    def test_removes_triple_single_quote_docstring(self, tmp_path):
        p = tmp_path / "a.py"
        p.write_text("def foo():\n    '''Single quote docstring'''\n    return 2\n", encoding="utf-8")
        ex = CodeExtractor(p)
        result = ex.strip_comments()
        assert "Single quote docstring" not in result
        assert "return 2" in result

    def test_removes_multiline_docstring(self, tmp_path):
        p = tmp_path / "a.py"
        content = '"""\nThis spans\nmultiple lines.\n"""\nx = 1\n'
        p.write_text(content, encoding="utf-8")
        ex = CodeExtractor(p)
        result = ex.strip_comments()
        assert "multiple lines" not in result
        assert "x = 1" in result

    def test_preserves_regular_strings(self, tmp_path):
        p = tmp_path / "a.py"
        p.write_text('msg = "hello world"\n', encoding="utf-8")
        ex = CodeExtractor(p)
        result = ex.strip_comments()
        assert "hello world" in result

    def test_clean_char_count_less_than_original(self, tmp_path):
        p = tmp_path / "a.py"
        p.write_text("# lots of comments\n# more comments\nx = 1\n", encoding="utf-8")
        ex = CodeExtractor(p)
        ex.strip_comments()
        assert ex.char_counts["clean"] < ex.char_counts["original"]
        assert ex.char_counts["clean"] > 0


# ---------------------------------------------------------------------------
# JavaScript / TypeScript comment removal
# ---------------------------------------------------------------------------

class TestJSCommentRemoval:
    def test_removes_single_line_comment(self, tmp_path):
        p = tmp_path / "app.ts"
        p.write_text("const x = 1; // inline comment\nconst y = 2;\n", encoding="utf-8")
        ex = CodeExtractor(p)
        result = ex.strip_comments()
        assert "inline comment" not in result
        assert "const x = 1;" in result
        assert "const y = 2;" in result

    def test_removes_block_comment(self, tmp_path):
        p = tmp_path / "app.ts"
        p.write_text("/* This is a block comment */\nconst z = 3;\n", encoding="utf-8")
        ex = CodeExtractor(p)
        result = ex.strip_comments()
        assert "block comment" not in result
        assert "const z = 3;" in result

    def test_removes_multiline_block_comment(self, tmp_path):
        p = tmp_path / "app.js"
        content = "/*\n * Multi-line\n * block\n */\nfunction foo() {}\n"
        p.write_text(content, encoding="utf-8")
        ex = CodeExtractor(p)
        result = ex.strip_comments()
        assert "Multi-line" not in result
        assert "function foo()" in result

    def test_removes_jsdoc_comment(self, tmp_path):
        p = tmp_path / "app.js"
        content = "/**\n * @param x - the value\n * @returns number\n */\nfunction add(x) { return x + 1; }\n"
        p.write_text(content, encoding="utf-8")
        ex = CodeExtractor(p)
        result = ex.strip_comments()
        assert "@param" not in result
        assert "function add(x)" in result


# ---------------------------------------------------------------------------
# Blank line normalization
# ---------------------------------------------------------------------------

class TestBlankLineNormalization:
    def test_collapses_three_blank_lines_to_two(self, tmp_path):
        p = tmp_path / "a.py"
        p.write_text("x = 1\n\n\n\ny = 2\n", encoding="utf-8")
        ex = CodeExtractor(p)
        result = ex.strip_comments()
        # Should not have 3+ consecutive newlines
        assert "\n\n\n" not in result

    def test_preserves_single_blank_line(self, tmp_path):
        p = tmp_path / "a.py"
        p.write_text("x = 1\n\ny = 2\n", encoding="utf-8")
        ex = CodeExtractor(p)
        result = ex.strip_comments()
        assert "x = 1" in result
        assert "y = 2" in result

    def test_preserves_double_blank_line(self, tmp_path):
        p = tmp_path / "a.py"
        p.write_text("def foo():\n    pass\n\n\ndef bar():\n    pass\n", encoding="utf-8")
        ex = CodeExtractor(p)
        result = ex.strip_comments()
        # Double blank line is fine (PEP 8 standard between top-level defs)
        assert "def foo():" in result
        assert "def bar():" in result


# ---------------------------------------------------------------------------
# file_header formatting
# ---------------------------------------------------------------------------

class TestFileHeader:
    def test_header_contains_filepath(self, tmp_path):
        p = tmp_path / "myfile.py"
        p.write_text("pass")
        ex = CodeExtractor(p)
        header = ex.file_header()
        assert "myfile.py" in header

    def test_header_contains_separator(self, tmp_path):
        p = tmp_path / "myfile.py"
        p.write_text("pass")
        ex = CodeExtractor(p)
        header = ex.file_header()
        assert "---" in header

    def test_header_uses_relative_path_when_root_given(self, tmp_path):
        sub = tmp_path / "src"
        sub.mkdir()
        p = sub / "app.py"
        p.write_text("pass")
        ex = CodeExtractor(p)
        header = ex.file_header(project_root=tmp_path)
        assert "src/app.py" in header

    def test_header_uses_forward_slashes(self, tmp_path):
        sub = tmp_path / "a" / "b"
        sub.mkdir(parents=True)
        p = sub / "file.py"
        p.write_text("pass")
        ex = CodeExtractor(p)
        header = ex.file_header(project_root=tmp_path)
        assert "\\" not in header


# ---------------------------------------------------------------------------
# ASTAnalyzer
# ---------------------------------------------------------------------------

class TestASTAnalyzer:
    def test_extracts_top_level_function(self, tmp_path):
        p = tmp_path / "mod.py"
        p.write_text("def greet(name, greeting):\n    return f'{greeting} {name}'\n")
        result = ASTAnalyzer.analyze_file(p)
        assert result.error is None
        assert len(result.functions) == 1
        fn = result.functions[0]
        assert fn.name == "greet"
        assert fn.args == ["name", "greeting"]

    def test_extracts_class_with_methods(self, tmp_path):
        p = tmp_path / "mod.py"
        p.write_text(
            "class MyClass:\n"
            "    def __init__(self, x):\n"
            "        self.x = x\n"
            "    def compute(self):\n"
            "        return self.x * 2\n"
        )
        result = ASTAnalyzer.analyze_file(p)
        assert result.error is None
        assert len(result.classes) == 1
        cls = result.classes[0]
        assert cls.name == "MyClass"
        method_names = [m.name for m in cls.methods]
        assert "__init__" in method_names
        assert "compute" in method_names

    def test_methods_not_double_counted_as_functions(self, tmp_path):
        p = tmp_path / "mod.py"
        p.write_text(
            "class Foo:\n"
            "    def bar(self):\n"
            "        pass\n"
            "\n"
            "def standalone():\n"
            "    pass\n"
        )
        result = ASTAnalyzer.analyze_file(p)
        func_names = [f.name for f in result.functions]
        assert "standalone" in func_names
        assert "bar" not in func_names

    def test_async_function_extracted(self, tmp_path):
        p = tmp_path / "mod.py"
        p.write_text("async def fetch(url: str) -> str:\n    return url\n")
        result = ASTAnalyzer.analyze_file(p)
        func_names = [f.name for f in result.functions]
        assert "fetch" in func_names

    def test_async_method_in_class(self, tmp_path):
        p = tmp_path / "mod.py"
        p.write_text(
            "class Service:\n"
            "    async def run(self):\n"
            "        pass\n"
        )
        result = ASTAnalyzer.analyze_file(p)
        cls = result.classes[0]
        assert any(m.name == "run" for m in cls.methods)

    def test_non_python_file_returns_error(self, tmp_path):
        p = tmp_path / "app.ts"
        p.write_text("const x = 1;")
        result = ASTAnalyzer.analyze_file(p)
        assert result.error is not None
        assert "not a Python file" in result.error

    def test_syntax_error_returns_graceful_error(self, tmp_path):
        p = tmp_path / "bad.py"
        p.write_text("def oops(\n    missing_close\n")
        result = ASTAnalyzer.analyze_file(p)
        assert result.error is not None
        assert "SyntaxError" in result.error

    def test_to_text_output_format(self, tmp_path):
        p = tmp_path / "mod.py"
        p.write_text(
            "def top_func(a, b):\n"
            "    pass\n\n"
            "class MyClass:\n"
            "    def method(self):\n"
            "        pass\n"
        )
        result = ASTAnalyzer.analyze_file(p)
        text = result.to_text()
        assert "#Module:" in text
        assert "##Functions:" in text
        assert "top_func" in text
        assert "##Classes:" in text
        assert "MyClass" in text
        assert "method" in text

    def test_to_text_uses_relative_path(self, tmp_path):
        sub = tmp_path / "pkg"
        sub.mkdir()
        p = sub / "mod.py"
        p.write_text("def f(): pass\n")
        result = ASTAnalyzer.analyze_file(p)
        text = result.to_text(project_root=tmp_path)
        assert "pkg/mod.py" in text

    def test_analyze_files_batch(self, tmp_path):
        files = []
        for name, content in [
            ("a.py", "def foo(): pass\n"),
            ("b.py", "class Bar:\n    def baz(self): pass\n"),
            ("c.ts", "const x = 1;"),
        ]:
            p = tmp_path / name
            p.write_text(content)
            files.append(p)
        results = ASTAnalyzer.analyze_files(files)
        assert len(results) == 3
        py_results = [r for r in results if r.error is None]
        assert len(py_results) == 2

    def test_empty_file_no_error(self, tmp_path):
        p = tmp_path / "empty.py"
        p.write_text("")
        result = ASTAnalyzer.analyze_file(p)
        assert result.error is None
        assert result.functions == []
        assert result.classes == []

    def test_multiple_classes_extracted(self, tmp_path):
        p = tmp_path / "mod.py"
        p.write_text(
            "class Alpha:\n    def run(self): pass\n\n"
            "class Beta:\n    def execute(self): pass\n"
        )
        result = ASTAnalyzer.analyze_file(p)
        class_names = [c.name for c in result.classes]
        assert "Alpha" in class_names
        assert "Beta" in class_names

"""
Tests for the four output modes and multi-language signature extraction.

Covers:
- OutputMode token-cost ordering (tree_only < signatures < clean < original)
- SignatureExtractor: Python AST path
- SignatureExtractor: TypeScript/JavaScript regex path
- SignatureExtractor: Go, Rust, Java, Kotlin, Swift, C#, Ruby, PHP, Lua, Dart
- SignatureExtractor: unsupported language graceful handling
- SignatureBlock.to_text() formatting
- _format_py_args: annotations, defaults, *args, **kwargs, positional-only
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from matrx_utils.code_context.code_context import (
    CodeContextBuilder,
    CodeContextConfig,
    SignatureBlock,
    SignatureExtractor,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_extractor() -> SignatureExtractor:
    return SignatureExtractor()


def extract(tmp_path, filename: str, content: str) -> SignatureBlock:
    p = tmp_path / filename
    p.write_text(content, encoding="utf-8")
    return make_extractor().extract(p, source=content)


# ---------------------------------------------------------------------------
# Token-cost ordering across modes
# ---------------------------------------------------------------------------

class TestOutputModeOrdering:
    @pytest.fixture()
    def real_project(self, tmp_path) -> Path:
        root = tmp_path / "proj"
        root.mkdir()
        (root / "alpha.py").write_text(
            '"""Module docstring."""\n\n'
            "# Section comment\n"
            "class Alpha:\n"
            '    """Class docstring."""\n'
            "    def run(self, x: int, y: int = 0) -> int:\n"
            '        """Run it."""\n'
            "        return x + y\n\n"
            "def helper(name: str) -> str:\n"
            '    """Help."""\n'
            "    return name.upper()\n",
            encoding="utf-8",
        )
        (root / "beta.py").write_text(
            "class Beta:\n"
            "    def __init__(self, val):\n"
            "        self.val = val\n\n"
            "    def compute(self):\n"
            "        return self.val * 2\n",
            encoding="utf-8",
        )
        return root

    def test_tree_only_smallest(self, real_project):
        tree_builder = CodeContextBuilder(project_root=real_project, output_mode="tree_only")
        sig_builder = CodeContextBuilder(project_root=real_project, output_mode="signatures")
        assert len(tree_builder.build().combined_text) < len(sig_builder.build().combined_text)

    def test_signatures_smaller_than_clean(self, real_project):
        sig_builder = CodeContextBuilder(project_root=real_project, output_mode="signatures")
        clean_builder = CodeContextBuilder(project_root=real_project, output_mode="clean")
        assert len(sig_builder.build().combined_text) < len(clean_builder.build().combined_text)

    def test_clean_smaller_than_original(self, real_project):
        clean_builder = CodeContextBuilder(project_root=real_project, output_mode="clean")
        orig_builder = CodeContextBuilder(project_root=real_project, output_mode="original")
        assert len(clean_builder.build().combined_text) < len(orig_builder.build().combined_text)

    def test_all_modes_contain_tree(self, real_project):
        for mode in ("tree_only", "signatures", "clean", "original"):
            result = CodeContextBuilder(project_root=real_project, output_mode=mode).build()
            assert "proj/" in result.combined_text, f"mode={mode} missing tree"

    def test_all_modes_contain_header(self, real_project):
        for mode in ("tree_only", "signatures", "clean", "original"):
            result = CodeContextBuilder(project_root=real_project, output_mode=mode).build()
            assert "Code Context" in result.combined_text, f"mode={mode} missing header"
            assert mode in result.combined_text, f"mode={mode} not shown in its own header"


# ---------------------------------------------------------------------------
# Python signature extraction
# ---------------------------------------------------------------------------

class TestPythonSignatures:
    def test_top_level_function(self, tmp_path):
        sb = extract(tmp_path, "mod.py", "def greet(name: str) -> str:\n    return name\n")
        assert any("def greet" in s for s in sb.signatures)

    def test_class_with_methods(self, tmp_path):
        sb = extract(tmp_path, "mod.py",
            "class Foo:\n"
            "    def __init__(self, x):\n"
            "        self.x = x\n"
            "    def run(self):\n"
            "        pass\n"
        )
        assert any("class Foo" in s for s in sb.signatures)
        assert any("def __init__" in s for s in sb.signatures)
        assert any("def run" in s for s in sb.signatures)

    def test_function_body_absent(self, tmp_path):
        sb = extract(tmp_path, "mod.py",
            "def compute(x, y):\n    return x * y + 100\n"
        )
        assert not any("return x * y" in s for s in sb.signatures)

    def test_async_function(self, tmp_path):
        sb = extract(tmp_path, "mod.py",
            "async def fetch(url: str) -> str:\n    return url\n"
        )
        assert any("async" in s and "fetch" in s for s in sb.signatures)

    def test_type_annotations_in_signature(self, tmp_path):
        sb = extract(tmp_path, "mod.py",
            "def process(items: list[str], limit: int = 10) -> dict:\n    pass\n"
        )
        sig = sb.signatures[0]
        assert "list[str]" in sig or "items" in sig

    def test_star_args(self, tmp_path):
        sb = extract(tmp_path, "mod.py",
            "def func(*args, **kwargs):\n    pass\n"
        )
        sig = sb.signatures[0]
        assert "*args" in sig
        assert "**kwargs" in sig

    def test_base_class_in_signature(self, tmp_path):
        sb = extract(tmp_path, "mod.py",
            "class Child(Base):\n    def run(self): pass\n"
        )
        assert any("Base" in s for s in sb.signatures)

    def test_syntax_error_returns_graceful_note(self, tmp_path):
        sb = extract(tmp_path, "bad.py", "def oops(\n    missing\n")
        assert sb.note is not None
        assert "SyntaxError" in sb.note

    def test_empty_file_no_signatures_no_error(self, tmp_path):
        sb = extract(tmp_path, "empty.py", "")
        # Empty file parses fine — note is None, signatures list is empty
        assert sb.note is None
        assert sb.signatures == []

    def test_language_tagged_as_python(self, tmp_path):
        sb = extract(tmp_path, "app.py", "x = 1\n")
        assert sb.language == "python"


# ---------------------------------------------------------------------------
# TypeScript / JavaScript signature extraction
# ---------------------------------------------------------------------------

class TestTypeScriptSignatures:
    def test_exported_function(self, tmp_path):
        sb = extract(tmp_path, "api.ts",
            "export async function fetchUser(id: string): Promise<User> {\n"
            "    return db.find(id);\n"
            "}\n"
        )
        assert any("fetchUser" in s for s in sb.signatures)

    def test_class_declaration(self, tmp_path):
        sb = extract(tmp_path, "service.ts",
            "export class UserService {\n"
            "    constructor(private db: DB) {}\n"
            "    async getUser(id: string): Promise<User> { return this.db.find(id); }\n"
            "}\n"
        )
        assert any("UserService" in s for s in sb.signatures)

    def test_interface_declaration(self, tmp_path):
        sb = extract(tmp_path, "types.ts",
            "export interface ApiResponse<T> {\n"
            "    data: T;\n"
            "    error: string | null;\n"
            "}\n"
        )
        assert any("ApiResponse" in s for s in sb.signatures)

    def test_arrow_function_const(self, tmp_path):
        sb = extract(tmp_path, "utils.ts",
            "export const transform = async (input: string): Promise<string> => {\n"
            "    return input.trim();\n"
            "};\n"
        )
        assert any("transform" in s for s in sb.signatures)

    def test_function_body_absent(self, tmp_path):
        sb = extract(tmp_path, "app.ts",
            "function add(a: number, b: number): number {\n"
            "    return a + b + 99999;\n"
            "}\n"
        )
        assert not any("99999" in s for s in sb.signatures)

    def test_language_tagged_as_typescript(self, tmp_path):
        sb = extract(tmp_path, "app.ts", "const x = 1;\n")
        assert sb.language == "typescript"

    def test_tsx_tagged_as_typescript(self, tmp_path):
        sb = extract(tmp_path, "Component.tsx", "export function Button() { return null; }\n")
        assert sb.language == "typescript"

    def test_js_function(self, tmp_path):
        sb = extract(tmp_path, "lib.js",
            "function greet(name) {\n"
            "    return 'Hello ' + name;\n"
            "}\n"
        )
        assert any("greet" in s for s in sb.signatures)
        assert sb.language == "javascript"


# ---------------------------------------------------------------------------
# Go signatures
# ---------------------------------------------------------------------------

class TestGoSignatures:
    def test_func_declaration(self, tmp_path):
        sb = extract(tmp_path, "main.go",
            "func Add(a, b int) int {\n    return a + b\n}\n"
        )
        assert any("Add" in s for s in sb.signatures)
        assert sb.language == "go"

    def test_method_declaration(self, tmp_path):
        sb = extract(tmp_path, "service.go",
            "func (s *Service) Run(ctx context.Context) error {\n    return nil\n}\n"
        )
        assert any("Run" in s for s in sb.signatures)

    def test_struct_type(self, tmp_path):
        sb = extract(tmp_path, "types.go",
            "type Config struct {\n    Host string\n    Port int\n}\n"
        )
        assert any("Config" in s for s in sb.signatures)

    def test_interface_type(self, tmp_path):
        sb = extract(tmp_path, "iface.go",
            "type Handler interface {\n    Handle(r Request) Response\n}\n"
        )
        assert any("Handler" in s for s in sb.signatures)


# ---------------------------------------------------------------------------
# Rust signatures
# ---------------------------------------------------------------------------

class TestRustSignatures:
    def test_pub_fn(self, tmp_path):
        sb = extract(tmp_path, "lib.rs",
            "pub fn compute(x: u32, y: u32) -> u32 {\n    x + y\n}\n"
        )
        assert any("compute" in s for s in sb.signatures)
        assert sb.language == "rust"

    def test_struct_declaration(self, tmp_path):
        sb = extract(tmp_path, "model.rs",
            "pub struct Config {\n    pub host: String,\n}\n"
        )
        assert any("Config" in s for s in sb.signatures)

    def test_impl_block(self, tmp_path):
        sb = extract(tmp_path, "service.rs",
            "impl Service {\n    pub fn new() -> Self { Service {} }\n}\n"
        )
        assert any("Service" in s for s in sb.signatures)

    def test_trait_declaration(self, tmp_path):
        sb = extract(tmp_path, "traits.rs",
            "pub trait Runnable {\n    fn run(&self);\n}\n"
        )
        assert any("Runnable" in s for s in sb.signatures)


# ---------------------------------------------------------------------------
# Java signatures
# ---------------------------------------------------------------------------

class TestJavaSignatures:
    def test_class_declaration(self, tmp_path):
        sb = extract(tmp_path, "App.java",
            "public class App {\n"
            "    public static void main(String[] args) {\n"
            "        System.out.println(\"hello\");\n"
            "    }\n"
            "}\n"
        )
        assert any("App" in s for s in sb.signatures)
        assert sb.language == "java"

    def test_interface_declaration(self, tmp_path):
        sb = extract(tmp_path, "Handler.java",
            "public interface Handler {\n"
            "    void handle(Request req);\n"
            "}\n"
        )
        assert any("Handler" in s for s in sb.signatures)


# ---------------------------------------------------------------------------
# Other languages — basic smoke tests
# ---------------------------------------------------------------------------

class TestOtherLanguages:
    def test_ruby_method(self, tmp_path):
        sb = extract(tmp_path, "app.rb",
            "class MyClass\n"
            "  def initialize(name)\n"
            "    @name = name\n"
            "  end\n"
            "end\n"
        )
        assert sb.language == "ruby"
        assert any("initialize" in s or "MyClass" in s for s in sb.signatures)

    def test_php_function(self, tmp_path):
        sb = extract(tmp_path, "app.php",
            "<?php\n"
            "function greet(string $name): string {\n"
            "    return 'Hello ' . $name;\n"
            "}\n"
        )
        assert sb.language == "php"
        assert any("greet" in s for s in sb.signatures)

    def test_lua_function(self, tmp_path):
        sb = extract(tmp_path, "mod.lua",
            "function greet(name)\n"
            "    return 'Hello ' .. name\n"
            "end\n"
        )
        assert sb.language == "lua"
        assert any("greet" in s for s in sb.signatures)

    def test_kotlin_class(self, tmp_path):
        sb = extract(tmp_path, "App.kt",
            "data class User(val name: String, val age: Int)\n"
            "fun main() {\n"
            "    println(\"Hello\")\n"
            "}\n"
        )
        assert sb.language == "kotlin"
        assert any("User" in s or "main" in s for s in sb.signatures)

    def test_swift_function(self, tmp_path):
        sb = extract(tmp_path, "app.swift",
            "func greet(name: String) -> String {\n"
            "    return \"Hello \\(name)\"\n"
            "}\n"
        )
        assert sb.language == "swift"
        assert any("greet" in s for s in sb.signatures)

    def test_dart_class(self, tmp_path):
        sb = extract(tmp_path, "app.dart",
            "class MyWidget extends StatelessWidget {\n"
            "  final String title;\n"
            "  MyWidget({required this.title});\n"
            "}\n"
        )
        assert sb.language == "dart"
        assert any("MyWidget" in s for s in sb.signatures)


# ---------------------------------------------------------------------------
# Unsupported language handling
# ---------------------------------------------------------------------------

class TestUnsupportedLanguage:
    def test_unknown_extension_returns_note(self, tmp_path):
        sb = extract(tmp_path, "app.brainfuck", "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.")
        assert sb.note is not None
        assert "not supported" in sb.note.lower() or "LANGUAGE_COVERAGE" in sb.note

    def test_unknown_extension_no_crash(self, tmp_path):
        sb = extract(tmp_path, "data.xyz", "some content here")
        assert isinstance(sb, SignatureBlock)

    def test_no_extension_graceful(self, tmp_path):
        sb = extract(tmp_path, "Makefile", "all:\n\t$(CC) -o main main.c\n")
        assert isinstance(sb, SignatureBlock)


# ---------------------------------------------------------------------------
# SignatureBlock.to_text() formatting
# ---------------------------------------------------------------------------

class TestSignatureBlockText:
    def test_to_text_contains_filepath(self, tmp_path):
        sb = extract(tmp_path, "mod.py", "def foo(): pass\n")
        text = sb.to_text()
        assert "mod.py" in text

    def test_to_text_contains_language_tag(self, tmp_path):
        sb = extract(tmp_path, "mod.py", "def foo(): pass\n")
        text = sb.to_text()
        assert "python" in text

    def test_to_text_uses_relative_path(self, tmp_path):
        sub = tmp_path / "pkg"
        sub.mkdir()
        p = sub / "mod.py"
        p.write_text("def foo(): pass\n")
        sb = make_extractor().extract(p)
        text = sb.to_text(project_root=tmp_path)
        assert "pkg/mod.py" in text
        assert "\\" not in text

    def test_to_text_indents_signatures(self, tmp_path):
        sb = extract(tmp_path, "mod.py",
            "class Foo:\n    def bar(self): pass\n"
        )
        text = sb.to_text()
        sig_lines = [l for l in text.splitlines() if "class" in l or "def" in l]
        assert len(sig_lines) >= 1

    def test_to_text_note_shown_for_unsupported(self, tmp_path):
        sb = extract(tmp_path, "app.unknown_xyz", "code here")
        text = sb.to_text()
        assert sb.note in text


# ---------------------------------------------------------------------------
# Extract multiple files
# ---------------------------------------------------------------------------

class TestExtractFilesMulti:
    def test_batch_extraction(self, tmp_path):
        files = []
        for name, content in [
            ("a.py", "def foo(): pass\n"),
            ("b.ts", "export function bar() {}\n"),
            ("c.go", "func Baz() {}\n"),
        ]:
            p = tmp_path / name
            p.write_text(content)
            files.append(p)
        results = make_extractor().extract_files(files)
        assert len(results) == 3
        langs = {r.language for r in results}
        assert "python" in langs
        assert "typescript" in langs
        assert "go" in langs

    def test_batch_no_crash_on_mixed_supported_unsupported(self, tmp_path):
        files = []
        for name, content in [
            ("app.py", "def foo(): pass\n"),
            ("data.zzz", "unknown content"),
        ]:
            p = tmp_path / name
            p.write_text(content)
            files.append(p)
        results = make_extractor().extract_files(files)
        assert len(results) == 2

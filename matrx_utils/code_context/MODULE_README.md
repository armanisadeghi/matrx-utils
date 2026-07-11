# `utils.code_context` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `utils/code_context` |
| Last generated | 2026-02-28 14:52 |
| Output file | `utils/code_context/MODULE_README.md` |
| Signature mode | `signatures` |


**Child READMEs detected** (signatures collapsed — see links for detail):

| README | |
|--------|---|
| [`utils/code_context/tests/MODULE_README.md`](utils/code_context/tests/MODULE_README.md) | last generated 2026-02-28 14:52 |
**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py utils/code_context --mode signatures
```

**To add permanent notes:** Write anywhere outside the `<!-- AUTO:... -->` blocks.
<!-- /AUTO:meta -->

<!-- HUMAN-EDITABLE: This section is yours. Agents & Humans can edit this section freely — it will not be overwritten. -->

## Architecture

### Layers

| File | Role |
|------|------|
| `code_context.py` | Everything extraction: `FileDiscovery`, `CodeExtractor`, `SignatureExtractor`, `FunctionCallAnalyzer`, `CodeContextBuilder` — all in one file |
| `generate_module_readme.py` | README orchestrator: builds each AUTO section by calling `CodeContextBuilder`, then surgically merges them into the existing file |

`generate_readme.py` (in `utils/local_dev_utils/`) is the human-facing trigger script — edit settings there, run it, done.

### Entry Points

- `CodeContextBuilder.build()` — programmatic use; returns a `CodeContextResult` with combined text, file list, stats
- `generate_module_readme.run()` — called by `generate_readme.py`; creates or updates a `MODULE_README.md`

### Call Flow (happy path)

```
generate_readme.py (edit settings here)
  → generate_module_readme.run(subdirectory, mode, scope, entry_points)
      → _build_meta()       → inline string
      → _build_tree()       → CodeContextBuilder(tree_only).build()
      → _build_signatures() → CodeContextBuilder(signatures).build()
                               └─ SignatureExtractor._extract_python()  [Python AST]
                               └─ SignatureExtractor._extract_regex()   [all other langs]
      → _build_call_graph() → CodeContextBuilder(call_graph=True).build()
                               └─ FunctionCallAnalyzer.analyze_files()  [Python AST]
      → _build_callers()    → rglob scan + ast.parse per candidate file
      → _merge_sections()   → regex replace AUTO blocks in existing file
      → write MODULE_README.md
```

### Key Design Decisions

- **Surgical merge, not full rewrite.** The `_merge_sections` function replaces only `<!-- AUTO:id -->` blocks in-place. Human-written content is structurally protected — it cannot be overwritten even if the generator crashes mid-run because the file is only written once at the end.
- **`__init__.py` is included.** These files carry the public export surface (`__all__`, re-exports). Excluding them hides the module's contract from consumers.
- **Pydantic fields show types + defaults.** The AST emits `field: Type = default` not just `field` — this answers "what is the shape of this model?" without reading the source.
- **Module-level constants and type aliases are emitted.** `Literal`, `StrEnum`, `TypeAlias` declarations at module scope are shown so consumers know what values are valid without reading the file.
- **Callers section is opt-in.** Set `ENTRY_POINTS` in `generate_readme.py` to get an auto-generated table of "who calls this module." Leave it `None` to skip.

### Output Modes (token cost reference)

| Mode | Token cost | Best for |
|------|-----------|---------|
| `tree_only` | ~1% | "What files exist?" |
| `signatures` | ~5–10% | Full API map, understanding dependencies |
| `clean` | ~70–80% | Code review, editing tasks |
| `original` | 100% | Debugging, when comments matter |


<!-- AUTO:tree -->
## Directory Tree

> Auto-generated. 11 files across 2 directories.

```
utils/code_context/
├── MODULE_README.md
├── __init__.py
├── code_context.py
├── generate_module_readme.py
├── tests/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── test_code_extractor.py
│   ├── test_file_discovery.py
│   ├── test_integration.py
│   ├── test_output_modes.py
│   ├── test_tree_generator.py
# excluded: 8 .md, 1 .yaml
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="{mode}"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.
> Submodules with their own `MODULE_README.md` are collapsed to a single stub line.

```
---
Filepath: utils/code_context/code_context.py  [python]

  OutputMode = Literal['tree_only', 'signatures', 'clean', 'original']
  class CodeContextConfig:
      def from_yaml(cls, config_path: Path = _CONFIG_PATH, preset: str | None = None, overrides: dict | None = None) -> 'CodeContextConfig'
      def _apply_preset(self, raw: dict, preset_name: str) -> None
      def _apply_overrides(self, overrides: dict) -> None
  class FileDiscovery:
      def __init__(self, cfg: CodeContextConfig) -> None
      def should_exclude_directory(self, dirname: str) -> bool
      def should_exclude_file(self, filename: str) -> bool
      def discover(self, root: str | Path, subdirectory: str | None = None, additional_files: list[str] | None = None) -> list[Path]
      def analyze(self, files: list[Path]) -> dict
  class DirectoryTree:
      def __init__(self, files: list[Path], cfg: CodeContextConfig, custom_root: str | Path | None = None, scan_root: str | Path | None = None) -> None
      def generate(self, project_root: Path | None = None) -> str
      def _resolve_root(self) -> Path
      def _build_file_nodes(self, structure: dict, root: Path) -> None
      def _add_all_dirs(self, root: Path, structure: dict) -> None
      def _prune(self, node: dict) -> bool
      def _render(self, node: dict, lines: list[str], depth: int) -> None
  class CodeExtractor:
      def __init__(self, file_path: str | Path) -> None
      def _load(self) -> None
      def strip_comments(self) -> str | None
      def get_content(self, mode: OutputMode) -> str | None
      def update_contents(self, new_contents: str) -> None
      def refresh_contents(self) -> None
      def char_counts(self) -> dict[str, int]
      def file_header(self, project_root: Path | None = None, language: str | None = None) -> str
      def _relative_display(self, project_root: Path | None) -> str
  class SignatureBlock:
      def to_text(self, project_root: Path | None = None) -> str
  class SignatureExtractor:
      def extract(self, path: Path, source: str | None = None) -> SignatureBlock
      def _extract_python(self, path: Path, source: str) -> SignatureBlock
      def _extract_regex(self, path: Path, lang: str, source: str) -> SignatureBlock
      def extract_files(self, files: list[Path], extractors: dict[Path, CodeExtractor] | None = None) -> list[SignatureBlock]
  class FunctionCallInfo:
  class FunctionCallGraph:
      def to_text(self, highlight: set[str] | None = None, concise: bool = False) -> str
  class FunctionCallAnalyzer:
      def __init__(self, ignore: list[str] | None = None, highlight: list[str] | None = None, include_method_calls: bool = True, include_private_methods: bool = False) -> None
      def analyze_file(self, path: Path, project_root: Path | None = None) -> FunctionCallGraph
      def analyze_files(self, files: list[Path], project_root: Path | None = None, scope: list[str] | None = None) -> list[FunctionCallGraph]
      def _module_name(self, path: Path, project_root: Path | None) -> str
  class _CallVisitor(ast.NodeVisitor):
      def __init__(self, module_name: str, ignore: set[str], include_method_calls: bool = True, include_private_methods: bool = False) -> None
      def visit_FunctionDef(self, node: ast.FunctionDef) -> None
      def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None
      def visit_Call(self, node: ast.Call) -> None
  class FunctionInfo:
  class ClassInfo:
  class ModuleAST:
      def to_text(self, project_root: Path | None = None) -> str
  class ASTAnalyzer:
      def analyze_file(path: Path, source: str | None = None) -> ModuleAST
      def analyze_files(files: list[Path], extractors: dict[Path, CodeExtractor] | None = None) -> list[ModuleAST]
  class FileNode:
  class CodeContextResult:
      def to_files_json(self, root: Path | None = None) -> dict
      def to_simple_json(self) -> dict
  class CodeContextBuilder:
      def __init__(self, project_root: str | Path, subdirectory: str | None = None, output_mode: OutputMode | None = None, preset: str | None = None, config_path: Path = _CONFIG_PATH, overrides: dict | None = None, additional_files: list[str] | None = None, custom_root: str | Path | None = None, show_all_tree_directories: bool | None = None, prune_empty_directories: bool | None = None, export_directory: str | None = None, prompt_prefix: str | None = None, prompt_suffix: str | None = None, parallel_workers: int = 8, call_graph: bool = False, call_graph_ignore: list[str] | None = None, call_graph_highlight: list[str] | None = None, call_graph_scope: list[str] | None = None, call_graph_include_methods: bool = True, call_graph_include_private: bool = False) -> None
      def build(self) -> CodeContextResult
      def _load_files_parallel(self, files: list[Path]) -> dict[Path, CodeExtractor]
      def _assemble(self, files: list[Path], extractors: dict[Path, CodeExtractor], tree: str, signature_blocks: list[SignatureBlock], call_graphs: list[FunctionCallGraph], mode: OutputMode) -> str
      def save(self, result: CodeContextResult, export_directory: str | None = None) -> Path | None
      def print_summary(self, result: CodeContextResult) -> None
  def _word_boundary_pattern(word: str) -> re.Pattern
  def _format_py_args(args: ast.arguments) -> str
  def _compact_rhs(node_value: ast.expr, full_rhs: str) -> str



---
Filepath: utils/code_context/generate_module_readme.py  [python]

  PROJECT_ROOT = Path(__file__).resolve().parents[2]
  def _find_child_readmes(subdirectory: str) -> list[Path]
  def _build_meta(subdirectory: str, output_path: Path, mode: str, scope: list[str] | None, child_readmes: list[Path] | None = None) -> str
  def _read_child_timestamp(readme_path: Path) -> str | None
  def _build_config_block(subdirectory: str, mode: OutputMode, scope: list[str] | None, project_noise: list[str] | None, include_call_graph: bool, entry_points: list[str] | None, call_graph_exclude: list[str] | None = None) -> str
  def _read_child_config(readme_path: Path) -> dict | None
  def _check_child_staleness(child_readmes: list[Path]) -> list[tuple[Path, str]]
  def _build_tree(subdirectory: str, child_readmes: list[Path] | None = None) -> str
  def _build_signatures(subdirectory: str, mode: OutputMode, child_readmes: list[Path] | None = None) -> str
  def _collapse_covered_sections(content: str, subdirectory: str, child_readmes: list[Path]) -> str
  def _covered_readme_for_module(module_dotted: str, child_readmes: list[Path]) -> Path | None
  def _collapse_call_graph_block(header: str, entries: list[str], readme: Path) -> str
  def _build_call_graph(subdirectory: str, scope: list[str] | None, project_noise: list[str] | None, child_readmes: list[Path] | None = None, call_graph_exclude: list[str] | None = None) -> str
  def _build_dependencies(subdirectory: str) -> str
  def _scan_external_imports(subdirectory: str) -> list[tuple[Path, set[str], set[str]]]
  def _discover_entry_points(subdirectory: str) -> dict[str, list[str]]
  def _get_module_callables(subdirectory: str) -> set[str]
  def _build_callers(subdirectory: str, entry_points: list[str] | None) -> str
  def _extract_auto_blocks(content: str) -> dict[str, str]
  def _wrap_auto(section_id: str, content: str) -> str
  def _merge_sections(existing: str, sections: dict[str, str]) -> str
  def _build_initial_file(subdirectory: str, output_path: Path, mode: OutputMode, scope: list[str] | None, project_noise: list[str] | None, include_call_graph: bool, entry_points: list[str] | None = None, call_graph_exclude: list[str] | None = None) -> str
  def run(subdirectory: str, output_path: Path, mode: OutputMode, scope: list[str] | None, project_noise: list[str] | None, include_call_graph: bool, entry_points: list[str] | None = None, call_graph_exclude: list[str] | None = None, force_refresh_children: bool = False) -> None
  def run_cascade(subdirectory: str, mode: OutputMode = 'signatures', child_mode: OutputMode = 'signatures', min_py_files: int = 5, scope: list[str] | None = None, project_noise: list[str] | None = None, include_call_graph: bool = False, entry_points: list[str] | None = None, call_graph_exclude: list[str] | None = None, force_refresh_children: bool = False, _depth: int = 0, _all_new: list[Path] | None = None) -> None
  def main() -> None
  def _walk(directory: Path) -> None
  def _rhs(line: str) -> str
  def replacer(m: re.Match) -> str
  def _is_excluded(module_name: str) -> bool



---
Filepath: utils/code_context/__init__.py  [python]




---
Submodule: utils/code_context/tests/  [6 files — full detail in utils/code_context/tests/MODULE_README.md]

```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** pytest, yaml
<!-- /AUTO:dependencies -->

<!-- AUTO:call_graph -->
## Call Graph

> Auto-generated. All Python files.
> Shows which functions call which. `async` prefix = caller is an async function.
> Method calls shown as `receiver.method()`. Private methods (`_`) excluded by default.

```
Function Call Graphs

# Call graph: utils.code_context.code_context
  Global Scope → sys.exit(1) (line 70)
  Global Scope → logging.getLogger(__name__) (line 72)
  Global Scope → utils.code_context.code_context.Path(__file__) (line 74)
  Global Scope → utils.code_context.code_context.frozenset({'isinstance', 'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 'tuple', 'type', 'hasattr', 'getattr', 'setattr', 'vars', 'dir', 'any', 'all', 'next', 'iter', 'zip', 'enumerate', 'range', 'sorted', 'reversed', 'sum', 'max', 'min', 'abs', 'round', 'super', 'print', 'repr', 'hash', 'ValueError', 'TypeError', 'RuntimeError', 'KeyError', 'AttributeError', 'IndexError', 'StopIteration', 'NotImplementedError', 'Exception', 'defaultdict', 'uuid4', 'Field'}) (line 90)
  Global Scope → utils.code_context.code_context.field() (line 134)
  Global Scope → utils.code_context.code_context.field() (line 135)
  Global Scope → utils.code_context.code_context.field() (line 136)
  Global Scope → utils.code_context.code_context.field() (line 137)
  Global Scope → utils.code_context.code_context.field() (line 138)
  Global Scope → utils.code_context.code_context.field() (line 141)
  Global Scope → utils.code_context.code_context.field() (line 142)
  Global Scope → utils.code_context.code_context.field() (line 143)
  Global Scope → utils.code_context.code_context.field() (line 156)
  Global Scope → utils.code_context.code_context.field() (line 159)
  Global Scope → utils.code_context.code_context.field() (line 160)
  Global Scope → utils.code_context.code_context.field() (line 161)
  Global Scope → utils.code_context.code_context.field() (line 162)
  Global Scope → utils.code_context.code_context.field() (line 163)
  utils.code_context.code_context.from_yaml → config_path.exists() (line 173)
  utils.code_context.code_context.from_yaml → utils.code_context.code_context.open(config_path) (line 174)
  utils.code_context.code_context.from_yaml → yaml.safe_load(f) (line 175)
  utils.code_context.code_context.from_yaml → logger.warning('config.yaml not found at %s; using built-in defaults', config_path) (line 177)
  utils.code_context.code_context.from_yaml → raw.get('exclude_directories', {}) (line 179)
  utils.code_context.code_context.from_yaml → raw.get('exclude_files', {}) (line 180)
  utils.code_context.code_context.from_yaml → raw.get('output', {}) (line 181)
  utils.code_context.code_context.from_yaml → utils.code_context.code_context.cls() (line 183)
  utils.code_context.code_context.from_yaml → excl_dirs.get('exact', []) (line 184)
  utils.code_context.code_context.from_yaml → excl_dirs.get('containing', []) (line 185)
  utils.code_context.code_context.from_yaml → excl_files.get('exact', []) (line 186)
  utils.code_context.code_context.from_yaml → excl_files.get('containing', []) (line 187)
  utils.code_context.code_context.from_yaml → raw.get('exclude_extensions', []) (line 188)
  utils.code_context.code_context.from_yaml → raw.get('include_extensions', []) (line 189)
  utils.code_context.code_context.from_yaml → raw.get('include_directories', []) (line 190)
  utils.code_context.code_context.from_yaml → raw.get('include_files', []) (line 191)
  utils.code_context.code_context.from_yaml → out.get('save_combined', True) (line 192)
  utils.code_context.code_context.from_yaml → out.get('save_individual', False) (line 193)
  utils.code_context.code_context.from_yaml → out.get('export_directory', './output') (line 194)
  utils.code_context.code_context.from_yaml → out.get('output_mode', out.get('content_type', 'clean')) (line 195)
  utils.code_context.code_context.from_yaml → out.get('content_type', 'clean') (line 195)
  utils.code_context.code_context.from_yaml → out.get('show_all_tree_directories', False) (line 196)
  utils.code_context.code_context.from_yaml → out.get('prune_empty_directories', False) (line 197)
  utils.code_context.code_context.from_yaml → out.get('include_text_output', True) (line 198)
  utils.code_context.code_context.from_yaml → out.get('project_root_display', True) (line 199)
  utils.code_context.code_context.from_yaml → raw.get('call_graph_project_noise', []) (line 200)
  utils.code_context.code_context.from_yaml → raw.get('extensions_for_analysis', ['.js', '.jsx', '.ts', '.tsx', '.mjs']) (line 201)
  utils.code_context.code_context.from_yaml → raw.get('remove_comments_for_extensions', ['.js', '.jsx', '.ts', '.tsx']) (line 202)
  utils.code_context.code_context.from_yaml → raw.get('alias_map', {}) (line 203)
  utils.code_context.code_context.from_yaml → raw.get('include_export_types', ['const', 'function', 'type', 'interface']) (line 204)
  utils.code_context.code_context.from_yaml → raw.get('ignore_export_list', []) (line 205)
  utils.code_context.code_context._apply_preset → raw.get('presets', {}) (line 233)
  utils.code_context.code_context._apply_preset → presets.get(preset_name, {}) (line 234)
  utils.code_context.code_context._apply_preset → logger.warning("Preset '%s' not found in config.yaml; ignoring.", preset_name) (line 236)
  utils.code_context.code_context._apply_preset → preset_data.get('override', False) (line 239)
  utils.code_context.code_context._apply_preset → yaml_path.split('.') (line 253)
  utils.code_context.code_context._apply_preset → value.get(k) (line 259)
  utils.code_context.code_context._apply_preset → target.append(item) (line 269)
  utils.code_context.code_context._apply_preset → preset_data.get('output', {}) (line 271)
  utils.code_context.code_context._apply_overrides → list_fields.items() (line 289)
  utils.code_context.code_context._apply_overrides → ops.get('add', []) (line 294)
  utils.code_context.code_context._apply_overrides → target.append(item) (line 296)
  utils.code_context.code_context._apply_overrides → ops.get('remove', []) (line 297)
  utils.code_context.code_context._apply_overrides → target.remove(item) (line 299)
  utils.code_context.code_context._word_boundary_pattern → re.compile('(^|[_\\- .])' + re.escape(word) + '([_\\- .]|$)', re.IGNORECASE) (line 317)
  utils.code_context.code_context._word_boundary_pattern → re.escape(word) (line 317)
  utils.code_context.code_context.__init__ → d.lower() (line 336)
  utils.code_context.code_context.__init__ → utils.code_context.code_context._word_boundary_pattern(w) (line 337)
  utils.code_context.code_context.__init__ → d.lower() (line 338)
  utils.code_context.code_context.__init__ → f.lower() (line 339)
  utils.code_context.code_context.__init__ → utils.code_context.code_context._word_boundary_pattern(w) (line 340)
  utils.code_context.code_context.__init__ → f.lower() (line 341)
  utils.code_context.code_context.__init__ → e.lower() (line 342)
  utils.code_context.code_context.__init__ → e.lower() (line 343)
  utils.code_context.code_context.should_exclude_directory → dirname.lower() (line 346)
  utils.code_context.code_context.should_exclude_directory → pat.search(low) (line 350)
  utils.code_context.code_context.should_exclude_file → filename.lower() (line 358)
  utils.code_context.code_context.should_exclude_file → pat.search(low) (line 362)
  utils.code_context.code_context.should_exclude_file → ...lower() (line 367)
  utils.code_context.code_context.should_exclude_file → utils.code_context.code_context.Path(filename) (line 367)
  utils.code_context.code_context.discover → utils.code_context.code_context.Path(root) (line 378)
  utils.code_context.code_context.discover → utils.code_context.code_context.Path(os.path.normpath(subdirectory.lstrip('/\\'))) (line 380)
  utils.code_context.code_context.discover → ...normpath(subdirectory.lstrip('/\\')) (line 380)
  utils.code_context.code_context.discover → subdirectory.lstrip('/\\') (line 380)
  utils.code_context.code_context.discover → target.exists() (line 385)
  utils.code_context.code_context.discover → logger.warning('Discovery target does not exist: %s', target) (line 386)
  utils.code_context.code_context.discover → os.walk(target) (line 392)
  utils.code_context.code_context.discover → self.should_exclude_directory(d) (line 393)
  utils.code_context.code_context.discover → utils.code_context.code_context.Path(dirpath) (line 395)
  utils.code_context.code_context.discover → fp.is_file() (line 396)
  utils.code_context.code_context.discover → self.should_exclude_file(fname) (line 398)
  utils.code_context.code_context.discover → ...lower() (line 403)
  utils.code_context.code_context.discover → found.append(fp) (line 406)
  utils.code_context.code_context.discover → utils.code_context.code_context.Path(af) (line 414)
  utils.code_context.code_context.discover → p.is_file() (line 415)
  utils.code_context.code_context.discover → found.append(p) (line 416)
  utils.code_context.code_context.discover → seen.add(p) (line 417)
  utils.code_context.code_context.analyze → dirs.add(f.parent) (line 425)
  utils.code_context.code_context.analyze → ext_counts.items() (line 431)
  utils.code_context.code_context.__init__ → utils.code_context.code_context.Path(custom_root) (line 465)
  utils.code_context.code_context.__init__ → utils.code_context.code_context.Path(scan_root) (line 466)
  utils.code_context.code_context.__init__ → utils.code_context.code_context.FileDiscovery(cfg) (line 467)
  utils.code_context.code_context.generate → replace('\\', '/') (line 486)
  utils.code_context.code_context.generate → root.relative_to(project_root) (line 486)
  utils.code_context.code_context.generate → join(lines) (line 494)
  utils.code_context.code_context._resolve_root → utils.code_context.code_context.Path(os.path.commonpath([str(f) for f in self._files])) (line 501)
  utils.code_context.code_context._resolve_root → ...commonpath([str(f) for f in self._files]) (line 501)
  utils.code_context.code_context._resolve_root → common.is_dir() (line 502)
  utils.code_context.code_context._build_file_nodes → f.relative_to(root) (line 507)
  utils.code_context.code_context._build_file_nodes → utils.code_context.code_context.Path(f.name) (line 509)
  utils.code_context.code_context._build_file_nodes → node.setdefault(part, {}) (line 513)
  utils.code_context.code_context._add_all_dirs → os.walk(root) (line 517)
  utils.code_context.code_context._add_all_dirs → ...should_exclude_directory(d) (line 518)
  utils.code_context.code_context._add_all_dirs → relative_to(root) (line 519)
  utils.code_context.code_context._add_all_dirs → utils.code_context.code_context.Path(dirpath) (line 519)
  utils.code_context.code_context._add_all_dirs → node.setdefault(part, {}) (line 524)
  utils.code_context.code_context._prune → node.items() (line 532)
  utils.code_context.code_context._prune → keys_to_delete.append(key) (line 536)
  utils.code_context.code_context._render → node.items() (line 543)
  utils.code_context.code_context._render → lines.append(f'{indent}├── {name}') (line 545)
  utils.code_context.code_context._render → lines.append(f'{indent}├── {name}/') (line 547)
  utils.code_context.code_context.__init__ → utils.code_context.code_context.Path(file_path) (line 569)
  utils.code_context.code_context._load → ...read_text() (line 578)
  utils.code_context.code_context._load → ...read_text() (line 581)
  utils.code_context.code_context._load → logger.error('Cannot read %s: %s', self.path, exc) (line 583)
  utils.code_context.code_context._load → logger.error('Cannot read %s: %s', self.path, exc) (line 586)
  utils.code_context.code_context.strip_comments → re.sub("'''[\\s\\S]*?'''", '', text) (line 596)
  utils.code_context.code_context.strip_comments → re.sub('"""[\\s\\S]*?"""', '', text) (line 597)
  utils.code_context.code_context.strip_comments → re.sub('#[^\\n]*', '', text) (line 599)
  utils.code_context.code_context.strip_comments → re.sub('/\\*[\\s\\S]*?\\*/', '', text) (line 602)
  utils.code_context.code_context.strip_comments → re.sub('//[^\\n]*', '', text) (line 604)
  utils.code_context.code_context.strip_comments → re.sub('--\\[\\[[\\s\\S]*?\\]\\]', '', text) (line 607)
  utils.code_context.code_context.strip_comments → re.sub('--[^\\n]*', '', text) (line 609)
  utils.code_context.code_context.strip_comments → re.sub('<!--[\\s\\S]*?-->', '', text) (line 612)
  utils.code_context.code_context.strip_comments → re.sub('\\n[ \\t]*\\n[ \\t]*\\n+', '\n\n', text) (line 615)
  utils.code_context.code_context._relative_display → replace('\\', '/') (line 651)
  utils.code_context.code_context._relative_display → ...relative_to(project_root) (line 651)
  Global Scope → utils.code_context.code_context.field() (line 666)
  utils.code_context.code_context.to_text → replace('\\', '/') (line 672)
  utils.code_context.code_context.to_text → ...relative_to(project_root) (line 672)
  utils.code_context.code_context.to_text → lines.append(f'  # {self.note}') (line 680)
  utils.code_context.code_context.to_text → lines.extend((f'  {s}' for s in self.signatures)) (line 681)
  utils.code_context.code_context.to_text → join(lines) (line 682)
  Global Scope → re.compile('^(class\\s+\\w[\\w\\d]*(?:\\s*\\([^)]*\\))?\\s*:)', re.MULTILINE) (line 726)
  Global Scope → re.compile('^(\\s*(?:async\\s+)?def\\s+\\w[\\w\\d]*\\s*\\([^)]*\\)\\s*(?:->\\s*[^:]+)?:)', re.MULTILINE) (line 727)
  Global Scope → re.compile('^(?:export\\s+)?(?:abstract\\s+)?(?:class|interface|enum|type)\\s+\\w[\\w\\d]*[^{;]*', re.MULTILINE) (line 731)
  Global Scope → re.compile('^(?:export\\s+)?(?:async\\s+)?function\\s*\\*?\\s*\\w[\\w\\d]*\\s*(?:<[^>]*>)?\\s*\\([^)]*\\)[^{;]*', re.MULTILINE) (line 732)
  Global Scope → re.compile('^\\s+(?:(?:public|private|protected|static|async|readonly|abstract|override)\\s+)*(?:readonly\\s+)?(?:\\w[\\w\\d]*)\\s*(?:<[^>]*>)?\\s*\\([^)]*\\)\\s*(?::\\s*[^{;]+)?(?=\\s*\\{|\\s*;)', re.MULTILINE) (line 733)
  Global Scope → re.compile('^(?:export\\s+)?const\\s+\\w[\\w\\d]*\\s*=\\s*(?:async\\s+)?\\([^)]*\\)\\s*(?::\\s*(?:Promise<[^>]+>|\\w[\\w\\d<>|?,\\s\\[\\]]+))?\\s*=>', re.MULTILINE) (line 734)
  Global Scope → re.compile('^(?:export\\s+)?(?:class|extends)\\s+\\w[\\w\\d]*[^{;]*', re.MULTILINE) (line 738)
  Global Scope → re.compile('^(?:export\\s+)?(?:async\\s+)?function\\s*\\*?\\s*\\w[\\w\\d]*\\s*\\([^)]*\\)', re.MULTILINE) (line 739)
  Global Scope → re.compile('^\\s+(?:async\\s+)?\\w[\\w\\d]*\\s*\\([^)]*\\)\\s*(?=\\{)', re.MULTILINE) (line 740)
  Global Scope → re.compile('^(?:export\\s+)?const\\s+\\w[\\w\\d]*\\s*=\\s*(?:async\\s+)?\\([^)]*\\)\\s*=>', re.MULTILINE) (line 741)
  Global Scope → re.compile('^func\\s+(?:\\([^)]+\\)\\s+)?\\w[\\w\\d]*\\s*\\([^)]*\\)[^{]*', re.MULTILINE) (line 745)
  Global Scope → re.compile('^type\\s+\\w[\\w\\d]*\\s+(?:struct|interface)[^{]*', re.MULTILINE) (line 746)
  Global Scope → re.compile('^(?:pub(?:\\([^)]+\\))?\\s+)?(?:async\\s+)?fn\\s+\\w[\\w\\d]*[^{]*', re.MULTILINE) (line 750)
  Global Scope → re.compile('^(?:pub\\s+)?(?:struct|enum|trait|impl(?:\\s+\\w[\\w\\d]*)?)\\s+\\w[\\w\\d]*[^{]*', re.MULTILINE) (line 751)
  Global Scope → re.compile('^(?:\\s+)?(?:(?:public|private|protected|static|final|abstract|synchronized|native|strictfp)\\s+)*(?:\\w[\\w\\d<>,\\[\\] ]+)\\s+\\w[\\w\\d]*\\s*\\([^)]*\\)(?:\\s+throws\\s+[^{]+)?(?=\\s*\\{)', re.MULTILINE) (line 755)
  Global Scope → re.compile('^(?:public|private|protected)?\\s*(?:abstract\\s+)?(?:class|interface|enum|record)\\s+\\w[\\w\\d]*[^{]*', re.MULTILINE) (line 756)
  Global Scope → re.compile('^(?:(?:public|private|protected|internal|open|abstract|override|data|sealed|inline|suspend)\\s+)*(?:fun|class|interface|object|enum\\s+class|data\\s+class|sealed\\s+class)\\s+\\w[\\w\\d]*[^{=]*', re.MULTILINE) (line 760)
  Global Scope → re.compile('^(?:(?:public|private|internal|open|fileprivate|final|override|mutating|static|class)\\s+)*(?:func|class|struct|protocol|enum|extension)\\s+\\w[\\w\\d]*[^{]*', re.MULTILINE) (line 764)
  Global Scope → re.compile('^(?![\\s#/])(?:(?:static|inline|extern|const|volatile|unsigned|signed)\\s+)*\\w[\\w\\d\\s\\*]+\\s+\\*?\\w[\\w\\d]*\\s*\\([^;)]*\\)(?=\\s*[{;])', re.MULTILINE) (line 768)
  Global Scope → re.compile('^(?:struct|union|enum|typedef)\\s+\\w[\\w\\d]*[^{;]*', re.MULTILINE) (line 769)
  Global Scope → re.compile('^(?![\\s#/])(?:(?:static|inline|virtual|explicit|constexpr|const|override|final|template[^>]*>\\s*)\\s+)*\\w[\\w\\d:<>,\\s\\*&]+\\s+\\*?\\w[\\w\\d]*\\s*\\([^;)]*\\)(?:\\s*const)?(?=\\s*[{;])', re.MULTILINE) (line 773)
  Global Scope → re.compile('^(?:class|struct|union|enum(?:\\s+class)?|namespace)\\s+\\w[\\w\\d]*[^{;]*', re.MULTILINE) (line 774)
  Global Scope → re.compile('^(?:\\s+)?(?:(?:public|private|protected|internal|static|virtual|override|abstract|async|sealed|readonly|partial)\\s+)*(?:\\w[\\w\\d<>,\\[\\] ?]+)\\s+\\w[\\w\\d]*\\s*\\([^)]*\\)(?=\\s*[{;])', re.MULTILINE) (line 778)
  Global Scope → re.compile('^(?:\\s+)?(?:public|private|protected|internal)?\\s*(?:abstract|static|partial)?\\s*(?:class|interface|struct|enum|record)\\s+\\w[\\w\\d]*[^{;]*', re.MULTILINE) (line 779)
  Global Scope → re.compile('^(?:\\s+)?def\\s+(?:self\\.)?\\w[\\w\\d?!]*(?:\\([^)]*\\))?', re.MULTILINE) (line 783)
  Global Scope → re.compile('^(?:class|module)\\s+\\w[\\w\\d:]*[^;]*', re.MULTILINE) (line 784)
  Global Scope → re.compile('^(?:\\s+)?(?:(?:public|private|protected|static|abstract|final)\\s+)*function\\s+\\w[\\w\\d]*\\s*\\([^)]*\\)(?:\\s*:\\s*\\??\\w[\\w\\d\\\\|]+)?', re.MULTILINE) (line 788)
  Global Scope → re.compile('^(?:abstract\\s+)?(?:class|interface|trait|enum)\\s+\\w[\\w\\d]*[^{;]*', re.MULTILINE) (line 789)
  Global Scope → re.compile('^(?:local\\s+)?function\\s+[\\w\\d.:]+\\s*\\([^)]*\\)', re.MULTILINE) (line 793)
  Global Scope → re.compile('^[\\w\\d.:]+\\s*=\\s*function\\s*\\([^)]*\\)', re.MULTILINE) (line 794)
  Global Scope → re.compile('^(?:\\s+)?(?:(?:def|val|var|class|object|trait|case\\s+class|sealed\\s+(?:class|trait))\\s+)\\w[\\w\\d]*[^{=]*', re.MULTILINE) (line 798)
  Global Scope → re.compile('^(?:\\s+)?(?:(?:static|final|const|abstract|override|late)\\s+)*\\w[\\w\\d?<>]+\\s+\\w[\\w\\d]*\\s*\\([^)]*\\)(?=\\s*[{;=>])', re.MULTILINE) (line 802)
  Global Scope → re.compile('^(?:abstract\\s+)?class\\s+\\w[\\w\\d]*[^{;]*', re.MULTILINE) (line 803)
  utils.code_context.code_context.extract → _LANG_MAP.get(path.suffix.lower(), 'unknown') (line 819)
  utils.code_context.code_context.extract → ...lower() (line 819)
  utils.code_context.code_context.extract → path.read_text() (line 823)
  utils.code_context.code_context.extract → path.read_text() (line 826)
  utils.code_context.code_context.extract → utils.code_context.code_context.SignatureBlock() (line 828)
  utils.code_context.code_context.extract → utils.code_context.code_context.SignatureBlock() (line 830)
  utils.code_context.code_context.extract → utils.code_context.code_context.SignatureBlock() (line 837)
  utils.code_context.code_context._extract_python → warnings.catch_warnings() (line 845)
  utils.code_context.code_context._extract_python → warnings.simplefilter('ignore') (line 846)
  utils.code_context.code_context._extract_python → ast.parse(source) (line 847)
  utils.code_context.code_context._extract_python → utils.code_context.code_context.SignatureBlock() (line 849)
  utils.code_context.code_context._extract_python → name.startswith('_') (line 864)
  utils.code_context.code_context._extract_python → ast.unparse(stmt.value) (line 866)
  utils.code_context.code_context._extract_python → name.isupper() (line 867)
  utils.code_context.code_context._extract_python → isupper() (line 867)
  utils.code_context.code_context._extract_python → c.isupper() (line 867)
  utils.code_context.code_context._extract_python → sigs.append(f'{name} = {rhs}') (line 871)
  utils.code_context.code_context._extract_python → name.startswith('_') (line 874)
  utils.code_context.code_context._extract_python → ast.unparse(stmt.value) (line 876)
  utils.code_context.code_context._extract_python → ast.unparse(stmt.annotation) (line 877)
  utils.code_context.code_context._extract_python → sigs.append(f'{name}: {ann}' + (f' = {rhs}' if rhs else '')) (line 880)
  utils.code_context.code_context._extract_python → ast.walk(tree) (line 882)
  utils.code_context.code_context._extract_python → join((ast.unparse(b) if hasattr(ast, 'unparse') else getattr(b, 'id', '?') for b in node.bases)) (line 884)
  utils.code_context.code_context._extract_python → ast.unparse(b) (line 885)
  utils.code_context.code_context._extract_python → sigs.append(f'class {node.name}({bases}):' if bases else f'class {node.name}:') (line 888)
  utils.code_context.code_context._extract_python → ast.unparse(b) (line 892)
  utils.code_context.code_context._extract_python → ...startswith('_') (line 904)
  utils.code_context.code_context._extract_python → ast.unparse(item.annotation) (line 907)
  utils.code_context.code_context._extract_python → ast.unparse(item.value) (line 917)
  utils.code_context.code_context._extract_python → re.search('\\bdefault=([^,)]+)', raw_default) (line 918)
  utils.code_context.code_context._extract_python → re.search('\\bdefault_factory=(\\w+)', raw_default) (line 919)
  utils.code_context.code_context._extract_python → raw_default.startswith('Field(') (line 920)
  utils.code_context.code_context._extract_python → strip() (line 922)
  utils.code_context.code_context._extract_python → field_kw_default.group(1) (line 922)
  utils.code_context.code_context._extract_python → strip() (line 926)
  utils.code_context.code_context._extract_python → field_kw_factory.group(1) (line 926)
  utils.code_context.code_context._extract_python → field_parts.append(f'{fname}: {ftype}{fdefault}' if ftype else fname) (line 931)
  utils.code_context.code_context._extract_python → sigs.append(f"    # fields: {', '.join(field_parts)}") (line 933)
  utils.code_context.code_context._extract_python → join(field_parts) (line 933)
  utils.code_context.code_context._extract_python → utils.code_context.code_context._format_py_args(item.args) (line 938)
  utils.code_context.code_context._extract_python → ast.unparse(item.returns) (line 939)
  utils.code_context.code_context._extract_python → sigs.append(f'    {prefix}def {item.name}({args}){ret}') (line 941)
  utils.code_context.code_context._extract_python → method_names.add(item.name) (line 942)
  utils.code_context.code_context._extract_python → ast.walk(tree) (line 944)
  utils.code_context.code_context._extract_python → utils.code_context.code_context._format_py_args(node.args) (line 948)
  utils.code_context.code_context._extract_python → ast.unparse(node.returns) (line 949)
  utils.code_context.code_context._extract_python → sigs.append(f'{prefix}def {node.name}({args}){ret}') (line 951)
  utils.code_context.code_context._extract_python → utils.code_context.code_context.SignatureBlock() (line 953)
  utils.code_context.code_context._extract_regex → _SIG_PATTERNS.get(lang, []) (line 956)
  utils.code_context.code_context._extract_regex → utils.code_context.code_context.SignatureBlock() (line 958)
  utils.code_context.code_context._extract_regex → pat.finditer(source) (line 963)
  utils.code_context.code_context._extract_regex → re.sub('\\s+', ' ', m.group(0).strip()) (line 964)
  utils.code_context.code_context._extract_regex → strip() (line 964)
  utils.code_context.code_context._extract_regex → m.group(0) (line 964)
  utils.code_context.code_context._extract_regex → seen.add(line) (line 966)
  utils.code_context.code_context._extract_regex → sigs.append(line) (line 967)
  utils.code_context.code_context._extract_regex → utils.code_context.code_context.SignatureBlock() (line 968)
  utils.code_context.code_context.extract_files → results.append(self.extract(f, source=source)) (line 978)
  utils.code_context.code_context.extract_files → self.extract(f) (line 978)
  utils.code_context.code_context._format_py_args → ast.unparse(a.annotation) (line 987)
  utils.code_context.code_context._format_py_args → ast.unparse(args.defaults[di]) (line 989)
  utils.code_context.code_context._format_py_args → parts.append(f'{a.arg}{ann}{dflt}') (line 990)
  utils.code_context.code_context._format_py_args → parts.append('/') (line 992)
  utils.code_context.code_context._format_py_args → ast.unparse(a.annotation) (line 996)
  utils.code_context.code_context._format_py_args → ast.unparse(args.defaults[di]) (line 998)
  utils.code_context.code_context._format_py_args → parts.append(f'{a.arg}{ann}{dflt}') (line 999)
  utils.code_context.code_context._format_py_args → ast.unparse(args.vararg.annotation) (line 1002)
  utils.code_context.code_context._format_py_args → parts.append(f'*{args.vararg.arg}{ann}') (line 1003)
  utils.code_context.code_context._format_py_args → parts.append('*') (line 1005)
  utils.code_context.code_context._format_py_args → ast.unparse(a.annotation) (line 1008)
  utils.code_context.code_context._format_py_args → ast.unparse(args.kw_defaults[i]) (line 1009)
  utils.code_context.code_context._format_py_args → parts.append(f'{a.arg}{ann}{dflt}') (line 1010)
  utils.code_context.code_context._format_py_args → ast.unparse(args.kwarg.annotation) (line 1013)
  utils.code_context.code_context._format_py_args → parts.append(f'**{args.kwarg.arg}{ann}') (line 1014)
  utils.code_context.code_context._format_py_args → join(parts) (line 1016)
  Global Scope → utils.code_context.code_context.field() (line 1036)
  utils.code_context.code_context.to_text → ...split('.') (line 1044)
  utils.code_context.code_context.to_text → ...split('.') (line 1048)
  utils.code_context.code_context.to_text → lines.append(f'  {marker}{async_prefix}{caller_name} → {callee_name} (line {call.line})') (line 1049)
  utils.code_context.code_context.to_text → join(call.arguments) (line 1052)
  utils.code_context.code_context.to_text → lines.append(f'  {marker}{caller} → {call.callee}({args}) (line {call.line})') (line 1053)
  utils.code_context.code_context.to_text → join(lines) (line 1054)
  utils.code_context.code_context.analyze_file → ...lower() (line 1082)
  utils.code_context.code_context.analyze_file → utils.code_context.code_context.FunctionCallGraph() (line 1083)
  utils.code_context.code_context.analyze_file → path.read_text() (line 1087)
  utils.code_context.code_context.analyze_file → utils.code_context.code_context.FunctionCallGraph() (line 1089)
  utils.code_context.code_context.analyze_file → warnings.catch_warnings() (line 1092)
  utils.code_context.code_context.analyze_file → warnings.simplefilter('ignore') (line 1093)
  utils.code_context.code_context.analyze_file → ast.parse(source) (line 1094)
  utils.code_context.code_context.analyze_file → utils.code_context.code_context.FunctionCallGraph() (line 1096)
  utils.code_context.code_context.analyze_file → utils.code_context.code_context._CallVisitor(module_name, self._ignore) (line 1098)
  utils.code_context.code_context.analyze_file → visitor.visit(tree) (line 1104)
  utils.code_context.code_context.analyze_file → utils.code_context.code_context.FunctionCallGraph() (line 1105)
  utils.code_context.code_context.analyze_files → ...lower() (line 1113)
  utils.code_context.code_context.analyze_files → self.analyze_file(f, project_root) (line 1117)
  utils.code_context.code_context._module_name → path.relative_to(project_root) (line 1122)
  utils.code_context.code_context._module_name → replace(os.sep, '.') (line 1123)
  utils.code_context.code_context._module_name → rel.with_suffix('') (line 1123)
  utils.code_context.code_context.visit_FunctionDef → self.generic_visit(node) (line 1150)
  utils.code_context.code_context.visit_AsyncFunctionDef → self.visit_FunctionDef(node) (line 1155)
  utils.code_context.code_context.visit_Call → ast.unparse(a) (line 1160)
  utils.code_context.code_context.visit_Call → ...append(FunctionCallInfo(caller=self.current_function, callee=f'{self.module_name}.{name}', arguments=args, line=node.lineno, is_async=self.current_is_async)) (line 1165)
  utils.code_context.code_context.visit_Call → utils.code_context.code_context.FunctionCallInfo() (line 1165)
  utils.code_context.code_context.visit_Call → attr.startswith('_') (line 1176)
  utils.code_context.code_context.visit_Call → ...append(FunctionCallInfo(caller=self.current_function, callee=callee, arguments=args, line=node.lineno, is_async=self.current_is_async)) (line 1185)
  utils.code_context.code_context.visit_Call → utils.code_context.code_context.FunctionCallInfo() (line 1185)
  utils.code_context.code_context.visit_Call → self.generic_visit(node) (line 1193)
  Global Scope → utils.code_context.code_context.field() (line 1210)
  Global Scope → utils.code_context.code_context.field() (line 1216)
  Global Scope → utils.code_context.code_context.field() (line 1217)
  utils.code_context.code_context.to_text → replace('\\', '/') (line 1225)
  utils.code_context.code_context.to_text → ...relative_to(project_root) (line 1225)
  utils.code_context.code_context.to_text → parts.append('## Functions:') (line 1233)
  utils.code_context.code_context.to_text → parts.append(f'  Function: {fn.name} — Args: {fn.args}') (line 1235)
  utils.code_context.code_context.to_text → parts.append('') (line 1236)
  utils.code_context.code_context.to_text → parts.append('## Classes:') (line 1238)
  utils.code_context.code_context.to_text → parts.append(f'  Class: {cls.name}') (line 1240)
  utils.code_context.code_context.to_text → parts.append(f'    Method: {m.name} — Args: {m.args}') (line 1242)
  utils.code_context.code_context.to_text → parts.append('') (line 1243)
  utils.code_context.code_context.to_text → strip() (line 1244)
  utils.code_context.code_context.to_text → join(parts) (line 1244)
  utils.code_context.code_context.analyze_file → ...lower() (line 1252)
  utils.code_context.code_context.analyze_file → utils.code_context.code_context.ModuleAST() (line 1253)
  utils.code_context.code_context.analyze_file → path.read_text() (line 1256)
  utils.code_context.code_context.analyze_file → utils.code_context.code_context.ModuleAST() (line 1258)
  utils.code_context.code_context.analyze_file → warnings.catch_warnings() (line 1260)
  utils.code_context.code_context.analyze_file → warnings.simplefilter('ignore') (line 1261)
  utils.code_context.code_context.analyze_file → ast.parse(source) (line 1262)
  utils.code_context.code_context.analyze_file → utils.code_context.code_context.ModuleAST() (line 1264)
  utils.code_context.code_context.analyze_file → ast.walk(tree) (line 1269)
  utils.code_context.code_context.analyze_file → methods.append(FunctionInfo(name=item.name, args=args, is_method=True)) (line 1275)
  utils.code_context.code_context.analyze_file → utils.code_context.code_context.FunctionInfo() (line 1275)
  utils.code_context.code_context.analyze_file → method_names.add(item.name) (line 1276)
  utils.code_context.code_context.analyze_file → classes.append(ClassInfo(name=node.name, methods=methods)) (line 1277)
  utils.code_context.code_context.analyze_file → utils.code_context.code_context.ClassInfo() (line 1277)
  utils.code_context.code_context.analyze_file → ast.walk(tree) (line 1280)
  utils.code_context.code_context.analyze_file → functions.append(FunctionInfo(name=node.name, args=args)) (line 1284)
  utils.code_context.code_context.analyze_file → utils.code_context.code_context.FunctionInfo() (line 1284)
  utils.code_context.code_context.analyze_file → utils.code_context.code_context.ModuleAST() (line 1286)
  utils.code_context.code_context.analyze_files → results.append(ASTAnalyzer.analyze_file(f, source=source)) (line 1296)
  utils.code_context.code_context.analyze_files → ASTAnalyzer.analyze_file(f) (line 1296)
  Global Scope → utils.code_context.code_context.field() (line 1314)
  Global Scope → utils.code_context.code_context.field() (line 1325)
  Global Scope → utils.code_context.code_context.field() (line 1326)
  Global Scope → utils.code_context.code_context.field() (line 1327)
  Global Scope → utils.code_context.code_context.field() (line 1328)
  Global Scope → utils.code_context.code_context.field() (line 1329)
  utils.code_context.code_context.to_files_json → f.relative_to(root) (line 1361)
  utils.code_context.code_context.to_files_json → utils.code_context.code_context.Path(f.name) (line 1363)
  utils.code_context.code_context.to_files_json → utils.code_context.code_context.Path(f.name) (line 1365)
  utils.code_context.code_context.to_files_json → node.setdefault(part, {}) (line 1370)
  utils.code_context.code_context.to_files_json → append(filename) (line 1373)
  utils.code_context.code_context.to_files_json → node.setdefault('_files', []) (line 1373)
  utils.code_context.code_context.to_files_json → append(str(f)) (line 1374)
  utils.code_context.code_context.to_files_json → node.setdefault('full_paths', []) (line 1374)
  utils.code_context.code_context.to_files_json → ...get(f) (line 1377)
  utils.code_context.code_context.to_simple_json → node.setdefault(part, {}) (line 1397)
  utils.code_context.code_context.__init__ → utils.code_context.code_context.Path(project_root) (line 1457)
  utils.code_context.code_context.__init__ → utils.code_context.code_context.Path(custom_root) (line 1460)
  utils.code_context.code_context.__init__ → CodeContextConfig.from_yaml(config_path) (line 1471)
  utils.code_context.code_context.build → utils.code_context.code_context.FileDiscovery(self.cfg) (line 1483)
  utils.code_context.code_context.build → discovery.discover(self.project_root) (line 1484)
  utils.code_context.code_context.build → discovery.analyze(files) (line 1489)
  utils.code_context.code_context.build → utils.code_context.code_context.Path(os.path.normpath(self.subdirectory.lstrip('/\\'))) (line 1495)
  utils.code_context.code_context.build → ...normpath(self.subdirectory.lstrip('/\\')) (line 1495)
  utils.code_context.code_context.build → ...lstrip('/\\') (line 1495)
  utils.code_context.code_context.build → generate() (line 1498)
  utils.code_context.code_context.build → utils.code_context.code_context.DirectoryTree(files, self.cfg, self.custom_root) (line 1498)
  utils.code_context.code_context.build → extractors.values() (line 1512)
  utils.code_context.code_context.build → ex.strip_comments() (line 1513)
  utils.code_context.code_context.build → utils.code_context.code_context.SignatureExtractor() (line 1516)
  utils.code_context.code_context.build → sig_extractor.extract_files(files, extractors) (line 1517)
  utils.code_context.code_context.build → merged_ignore.extend(self.cfg.call_graph_project_noise) (line 1522)
  utils.code_context.code_context.build → merged_ignore.extend(self.call_graph_ignore) (line 1524)
  utils.code_context.code_context.build → utils.code_context.code_context.FunctionCallAnalyzer() (line 1525)
  utils.code_context.code_context.build → analyzer.analyze_files(files, self.project_root) (line 1531)
  utils.code_context.code_context.build → extractors.get(f) (line 1541)
  utils.code_context.code_context.build → _LANG_MAP.get(f.suffix.lower()) (line 1542)
  utils.code_context.code_context.build → ...lower() (line 1542)
  utils.code_context.code_context.build → ...get('original', 0) (line 1543)
  utils.code_context.code_context.build → ...get('clean', 0) (line 1544)
  utils.code_context.code_context.build → sig_map.get(f) (line 1547)
  utils.code_context.code_context.build → utils.code_context.code_context.FileNode() (line 1550)
  utils.code_context.code_context.build → utils.code_context.code_context.CodeContextResult() (line 1558)
  utils.code_context.code_context._load → utils.code_context.code_context.CodeExtractor(path) (line 1577)
  utils.code_context.code_context._load_files_parallel → utils.code_context.code_context.ThreadPoolExecutor() (line 1579)
  utils.code_context.code_context._load_files_parallel → executor.submit(_load, f) (line 1580)
  utils.code_context.code_context._load_files_parallel → utils.code_context.code_context.as_completed(futures) (line 1581)
  utils.code_context.code_context._load_files_parallel → future.result() (line 1582)
  utils.code_context.code_context._assemble → parts.append(f'Code Context  [mode: {mode}  —  {_OUTPUT_MODE_LABELS[mode]}]\nScanned: {scanned}\n' + (f'{stats_line}\n' if stats_line else '')) (line 1601)
  utils.code_context.code_context._assemble → parts.append(self.prompt_prefix.strip()) (line 1608)
  utils.code_context.code_context._assemble → ...strip() (line 1608)
  utils.code_context.code_context._assemble → parts.append('') (line 1609)
  utils.code_context.code_context._assemble → parts.append(tree) (line 1611)
  utils.code_context.code_context._assemble → parts.append('') (line 1612)
  utils.code_context.code_context._assemble → sig_map.get(f) (line 1620)
  utils.code_context.code_context._assemble → _LANG_MAP.get(f.suffix.lower()) (line 1622)
  utils.code_context.code_context._assemble → ...lower() (line 1622)
  utils.code_context.code_context._assemble → parts.append(sb.to_text(self.project_root)) (line 1623)
  utils.code_context.code_context._assemble → sb.to_text(self.project_root) (line 1623)
  utils.code_context.code_context._assemble → extractors.get(f) (line 1627)
  utils.code_context.code_context._assemble → ex.get_content(mode) (line 1630)
  utils.code_context.code_context._assemble → _LANG_MAP.get(f.suffix.lower()) (line 1633)
  utils.code_context.code_context._assemble → ...lower() (line 1633)
  utils.code_context.code_context._assemble → parts.append(ex.file_header(self.project_root, language=lang)) (line 1634)
  utils.code_context.code_context._assemble → ex.file_header(self.project_root) (line 1634)
  utils.code_context.code_context._assemble → parts.append(content) (line 1635)
  utils.code_context.code_context._assemble → parts.append('\n\n---\nFunction Call Graphs\n') (line 1638)
  utils.code_context.code_context._assemble → parts.append(cg.to_text(highlight=highlight, concise=False)) (line 1642)
  utils.code_context.code_context._assemble → cg.to_text() (line 1642)
  utils.code_context.code_context._assemble → parts.append('') (line 1645)
  utils.code_context.code_context._assemble → parts.append(self.prompt_suffix.strip()) (line 1646)
  utils.code_context.code_context._assemble → ...strip() (line 1646)
  utils.code_context.code_context._assemble → join(parts) (line 1648)
  utils.code_context.code_context.save → utils.code_context.code_context.Path(export_directory or self.cfg.export_directory) (line 1651)
  utils.code_context.code_context.save → export_dir.mkdir() (line 1652)
  utils.code_context.code_context.save → strftime('%Y%m%d_%H%M%S') (line 1655)
  utils.code_context.code_context.save → datetime.now() (line 1655)
  utils.code_context.code_context.save → out_path.write_text(result.combined_text) (line 1659)
  utils.code_context.code_context.save → logger.info('Saved: %s', out_path) (line 1662)
  utils.code_context.code_context.save → ...get(f) (line 1667)
  utils.code_context.code_context.save → utils.code_context.code_context.CodeExtractor(f) (line 1669)
  utils.code_context.code_context.save → ex.strip_comments() (line 1671)
  utils.code_context.code_context.save → ex.get_content(result.output_mode) (line 1672)
  utils.code_context.code_context.save → ...get(f) (line 1674)
  utils.code_context.code_context.save → _LANG_MAP.get(f.suffix.lower()) (line 1675)
  utils.code_context.code_context.save → ...lower() (line 1675)
  utils.code_context.code_context.save → ind_path.write_text(ex.file_header(self.project_root, language=lang) + content) (line 1677)
  utils.code_context.code_context.save → ex.file_header(self.project_root) (line 1678)
  utils.code_context.code_context.save → json_path.write_text(_json.dumps(result.to_files_json(root=self.project_root), indent=2)) (line 1685)
  utils.code_context.code_context.save → _json.dumps(result.to_files_json(root=self.project_root)) (line 1686)
  utils.code_context.code_context.save → result.to_files_json() (line 1686)
  utils.code_context.code_context.save → logger.info('Saved structure JSON: %s', json_path) (line 1689)
  utils.code_context.code_context.print_summary → _OUTPUT_MODE_LABELS.get(result.output_mode, result.output_mode) (line 1695)
  utils.code_context.code_context.print_summary → ...values() (line 1702)
  utils.code_context.code_context.print_summary → ...values() (line 1703)
  Global Scope → utils.code_context.code_context.Path('/home/arman/projects/aidream') (line 1729)
  Global Scope → utils.code_context.code_context.Path('/tmp/code_context_output') (line 1732)
  Global Scope → logging.basicConfig() (line 1755)
  Global Scope → utils.code_context.code_context.CodeContextBuilder() (line 1757)
  Global Scope → builder.build() (line 1774)
  Global Scope → builder.print_summary(result) (line 1775)
  Global Scope → builder.save(result) (line 1776)
# Call graph: utils.code_context.generate_module_readme
  Global Scope → logging.getLogger(__name__) (line 69)
  Global Scope → resolve() (line 71)
  Global Scope → utils.code_context.generate_module_readme.Path(__file__) (line 71)
  Global Scope → re.compile('<!-- AUTO:(\\w+) -->(.*?)<!-- /AUTO:\\1 -->', re.DOTALL) (line 76)
  utils.code_context.generate_module_readme._walk → readme.exists() (line 133)
  utils.code_context.generate_module_readme._walk → found.append(readme) (line 134)
  utils.code_context.generate_module_readme._walk → directory.iterdir() (line 137)
  utils.code_context.generate_module_readme._walk → child.is_dir() (line 138)
  utils.code_context.generate_module_readme._walk → ...startswith(('.', '_')) (line 138)
  utils.code_context.generate_module_readme._walk → utils.code_context.generate_module_readme._walk(child) (line 139)
  utils.code_context.generate_module_readme._find_child_readmes → utils.code_context.generate_module_readme._walk(target) (line 143)
  utils.code_context.generate_module_readme._build_meta → strftime('%Y-%m-%d %H:%M') (line 158)
  utils.code_context.generate_module_readme._build_meta → datetime.now() (line 158)
  utils.code_context.generate_module_readme._build_meta → join(scope) (line 159)
  utils.code_context.generate_module_readme._build_meta → output_path.is_relative_to(PROJECT_ROOT) (line 164)
  utils.code_context.generate_module_readme._build_meta → output_path.relative_to(PROJECT_ROOT) (line 164)
  utils.code_context.generate_module_readme._build_meta → p.is_relative_to(PROJECT_ROOT) (line 170)
  utils.code_context.generate_module_readme._build_meta → p.relative_to(PROJECT_ROOT) (line 170)
  utils.code_context.generate_module_readme._build_meta → utils.code_context.generate_module_readme._read_child_timestamp(p) (line 172)
  utils.code_context.generate_module_readme._build_meta → rows.append(f'| [`{rel}`]({rel}) | {ts_note} |') (line 174)
  utils.code_context.generate_module_readme._build_meta → join(rows) (line 179)
  utils.code_context.generate_module_readme._read_child_timestamp → readme_path.read_text() (line 208)
  utils.code_context.generate_module_readme._read_child_timestamp → re.search('\\|\\s*Last generated\\s*\\|\\s*([^\\|]+)\\|', text) (line 209)
  utils.code_context.generate_module_readme._read_child_timestamp → strip() (line 211)
  utils.code_context.generate_module_readme._read_child_timestamp → m.group(1) (line 211)
  utils.code_context.generate_module_readme._check_child_staleness → utils.code_context.generate_module_readme._read_child_timestamp(readme) (line 227)
  utils.code_context.generate_module_readme._check_child_staleness → datetime.strptime(ts_str, '%Y-%m-%d %H:%M') (line 231)
  utils.code_context.generate_module_readme._check_child_staleness → subdir.rglob('*.py') (line 238)
  utils.code_context.generate_module_readme._check_child_staleness → py.stat() (line 239)
  utils.code_context.generate_module_readme._check_child_staleness → datetime.fromtimestamp(newest_mtime) (line 247)
  utils.code_context.generate_module_readme._check_child_staleness → readme.relative_to(PROJECT_ROOT) (line 250)
  utils.code_context.generate_module_readme._check_child_staleness → newest_file.relative_to(PROJECT_ROOT) (line 251)
  utils.code_context.generate_module_readme._check_child_staleness → total_seconds() (line 255)
  utils.code_context.generate_module_readme._check_child_staleness → warnings_out.append(f'  ⚠  {rel_readme} is STALE — {rel_file} modified {age} after last generation') (line 257)
  utils.code_context.generate_module_readme._build_tree → own_readme.exists() (line 271)
  utils.code_context.generate_module_readme._build_tree → readme_paths.append(str(own_readme)) (line 272)
  utils.code_context.generate_module_readme._build_tree → utils.code_context.generate_module_readme.CodeContextBuilder() (line 274)
  utils.code_context.generate_module_readme._build_tree → builder.build() (line 283)
  utils.code_context.generate_module_readme._build_tree → ...splitlines() (line 287)
  utils.code_context.generate_module_readme._build_tree → ln.startswith('Code Context') (line 289)
  utils.code_context.generate_module_readme._build_tree → ln.startswith('Scanned:') (line 289)
  utils.code_context.generate_module_readme._build_tree → ln.startswith('Files:') (line 289)
  utils.code_context.generate_module_readme._build_tree → tree_lines.append(ln) (line 292)
  utils.code_context.generate_module_readme._build_tree → strip() (line 294)
  utils.code_context.generate_module_readme._build_tree → join(tree_lines) (line 294)
  utils.code_context.generate_module_readme._build_tree → stats.get('total_files', len(result.files)) (line 296)
  utils.code_context.generate_module_readme._build_tree → stats.get('total_directories', len({f.parent for f in result.files})) (line 297)
  utils.code_context.generate_module_readme._build_tree → stats.get('excluded_by_extension', {}) (line 300)
  utils.code_context.generate_module_readme._build_tree → excluded.items() (line 305)
  utils.code_context.generate_module_readme._build_tree → join((f'{cnt} {ext}' for ext, cnt in parts)) (line 309)
  utils.code_context.generate_module_readme._build_signatures → utils.code_context.generate_module_readme.CodeContextBuilder() (line 328)
  utils.code_context.generate_module_readme._build_signatures → builder.build() (line 334)
  utils.code_context.generate_module_readme._build_signatures → text.find('\n---\n') (line 337)
  utils.code_context.generate_module_readme._build_signatures → strip() (line 339)
  utils.code_context.generate_module_readme._build_signatures → text.splitlines() (line 341)
  utils.code_context.generate_module_readme._build_signatures → strip() (line 342)
  utils.code_context.generate_module_readme._build_signatures → join(lines[4:]) (line 342)
  utils.code_context.generate_module_readme._build_signatures → utils.code_context.generate_module_readme._collapse_covered_sections(content, subdirectory, child_readmes) (line 352)
  utils.code_context.generate_module_readme._collapse_covered_sections → subdir_path.relative_to(PROJECT_ROOT) (line 395)
  utils.code_context.generate_module_readme._collapse_covered_sections → rel.as_posix() (line 398)
  utils.code_context.generate_module_readme._collapse_covered_sections → re.split('(?=^---$)', content) (line 404)
  utils.code_context.generate_module_readme._collapse_covered_sections → block.strip() (line 410)
  utils.code_context.generate_module_readme._collapse_covered_sections → re.search('^Filepath:\\s*(\\S+)', block, re.MULTILINE) (line 414)
  utils.code_context.generate_module_readme._collapse_covered_sections → output_blocks.append(block) (line 416)
  utils.code_context.generate_module_readme._collapse_covered_sections → fp_match.group(1) (line 419)
  utils.code_context.generate_module_readme._collapse_covered_sections → filepath.startswith(prefix) (line 424)
  utils.code_context.generate_module_readme._collapse_covered_sections → output_blocks.append(block) (line 429)
  utils.code_context.generate_module_readme._collapse_covered_sections → as_posix() (line 439)
  utils.code_context.generate_module_readme._collapse_covered_sections → readme_path.relative_to(PROJECT_ROOT) (line 439)
  utils.code_context.generate_module_readme._collapse_covered_sections → re.search(f'^Filepath:\\s*{re.escape(matched_prefix)}', b, re.MULTILINE) (line 446)
  utils.code_context.generate_module_readme._collapse_covered_sections → re.escape(matched_prefix) (line 446)
  utils.code_context.generate_module_readme._collapse_covered_sections → output_blocks.append(stub) (line 454)
  utils.code_context.generate_module_readme._collapse_covered_sections → emitted_stubs.add(matched_prefix) (line 455)
  utils.code_context.generate_module_readme._collapse_covered_sections → join(output_blocks) (line 457)
  utils.code_context.generate_module_readme._build_call_graph → utils.code_context.generate_module_readme.CodeContextBuilder() (line 465)
  utils.code_context.generate_module_readme._build_call_graph → builder.build() (line 476)
  utils.code_context.generate_module_readme._build_call_graph → text.find('Function Call Graphs') (line 478)
  utils.code_context.generate_module_readme._build_call_graph → strip() (line 482)
  utils.code_context.generate_module_readme._build_call_graph → join(scope) (line 483)
  utils.code_context.generate_module_readme._build_dependencies → utils.code_context.generate_module_readme.frozenset({'abc', 'aifc', 'argparse', 'array', 'ast', 'asynchat', 'asyncio', 'asyncore', 'atexit', 'base64', 'bdb', 'binascii', 'binhex', 'bisect', 'builtins', 'bz2', 'calendar', 'cgi', 'cgitb', 'chunk', 'cmath', 'cmd', 'code', 'codecs', 'codeop', 'colorsys', 'compileall', 'concurrent', 'configparser', 'contextlib', 'contextvars', 'copy', 'copyreg', 'cProfile', 'csv', 'ctypes', 'curses', 'dataclasses', 'datetime', 'dbm', 'decimal', 'difflib', 'dis', 'doctest', 'email', 'encodings', 'enum', 'errno', 'faulthandler', 'fcntl', 'filecmp', 'fileinput', 'fnmatch', 'fractions', 'ftplib', 'functools', 'gc', 'getopt', 'getpass', 'gettext', 'glob', 'grp', 'gzip', 'hashlib', 'heapq', 'hmac', 'html', 'http', 'idlelib', 'imaplib', 'imghdr', 'imp', 'importlib', 'inspect', 'io', 'ipaddress', 'itertools', 'json', 'keyword', 'lib2to3', 'linecache', 'locale', 'logging', 'lzma', 'mailbox', 'mailcap', 'marshal', 'math', 'mimetypes', 'mmap', 'modulefinder', 'multiprocessing', 'netrc', 'nis', 'nntplib', 'numbers', 'operator', 'optparse', 'os', 'pathlib', 'pdb', 'pickle', 'pickletools', 'pipes', 'pkgutil', 'platform', 'plistlib', 'poplib', 'posix', 'posixpath', 'pprint', 'profile', 'pstats', 'pty', 'pwd', 'py_compile', 'pyclbr', 'pydoc', 'queue', 'quopri', 'random', 're', 'readline', 'reprlib', 'resource', 'rlcompleter', 'runpy', 'sched', 'secrets', 'select', 'selectors', 'shelve', 'shlex', 'shutil', 'signal', 'site', 'smtpd', 'smtplib', 'sndhdr', 'socket', 'socketserver', 'spwd', 'sqlite3', 'sre_compile', 'sre_constants', 'sre_parse', 'ssl', 'stat', 'statistics', 'string', 'stringprep', 'struct', 'subprocess', 'sunau', 'symtable', 'sys', 'sysconfig', 'syslog', 'tabnanny', 'tarfile', 'telnetlib', 'tempfile', 'termios', 'test', 'textwrap', 'threading', 'time', 'timeit', 'tkinter', 'token', 'tokenize', 'tomllib', 'trace', 'traceback', 'tracemalloc', 'tty', 'turtle', 'turtledemo', 'types', 'typing', 'unicodedata', 'unittest', 'urllib', 'uu', 'uuid', 'venv', 'warnings', 'wave', 'weakref', 'webbrowser', 'wsgiref', 'xdrlib', 'xml', 'xmlrpc', 'zipapp', 'zipfile', 'zipimport', 'zlib', 'zoneinfo', '_thread', '__future__'}) (line 513)
  utils.code_context.generate_module_readme._build_dependencies → PROJECT_ROOT.iterdir() (line 556)
  utils.code_context.generate_module_readme._build_dependencies → item.is_dir() (line 557)
  utils.code_context.generate_module_readme._build_dependencies → ...startswith('.') (line 557)
  utils.code_context.generate_module_readme._build_dependencies → project_top_dirs.add(item.name) (line 558)
  utils.code_context.generate_module_readme._build_dependencies → item.is_file() (line 559)
  utils.code_context.generate_module_readme._build_dependencies → project_top_dirs.add(item.stem) (line 560)
  utils.code_context.generate_module_readme._build_dependencies → replace('\\', '.') (line 563)
  utils.code_context.generate_module_readme._build_dependencies → subdirectory.replace('/', '.') (line 563)
  utils.code_context.generate_module_readme._build_dependencies → target_dir.rglob('*.py') (line 568)
  utils.code_context.generate_module_readme._build_dependencies → py_file.read_text() (line 570)
  utils.code_context.generate_module_readme._build_dependencies → _warnings.catch_warnings() (line 571)
  utils.code_context.generate_module_readme._build_dependencies → _warnings.simplefilter('ignore') (line 572)
  utils.code_context.generate_module_readme._build_dependencies → _ast.parse(source) (line 573)
  utils.code_context.generate_module_readme._build_dependencies → _ast.walk(tree) (line 577)
  utils.code_context.generate_module_readme._build_dependencies → name.split('.') (line 591)
  utils.code_context.generate_module_readme._build_dependencies → name.startswith(target_module_prefix + '.') (line 595)
  utils.code_context.generate_module_readme._build_dependencies → name.split('.') (line 600)
  utils.code_context.generate_module_readme._build_dependencies → join(parts[:2]) (line 601)
  utils.code_context.generate_module_readme._build_dependencies → internal.add(label) (line 602)
  utils.code_context.generate_module_readme._build_dependencies → external.add(root) (line 604)
  utils.code_context.generate_module_readme._build_dependencies → lines.append(f"**External packages:** {', '.join(sorted(external))}") (line 611)
  utils.code_context.generate_module_readme._build_dependencies → join(sorted(external)) (line 611)
  utils.code_context.generate_module_readme._build_dependencies → lines.append(f"**Internal modules:** {', '.join(sorted(internal))}") (line 613)
  utils.code_context.generate_module_readme._build_dependencies → join(sorted(internal)) (line 613)
  utils.code_context.generate_module_readme._build_dependencies → lines.append('') (line 614)
  utils.code_context.generate_module_readme._build_dependencies → join(lines) (line 616)
  utils.code_context.generate_module_readme._build_callers → replace('\\', '.') (line 630)
  utils.code_context.generate_module_readme._build_callers → subdirectory.replace('/', '.') (line 630)
  utils.code_context.generate_module_readme._build_callers → PROJECT_ROOT.rglob('*.py') (line 636)
  utils.code_context.generate_module_readme._build_callers → py_file.relative_to(target_dir) (line 638)
  utils.code_context.generate_module_readme._build_callers → candidates.append(py_file) (line 646)
  utils.code_context.generate_module_readme._build_callers → py_file.read_text() (line 652)
  utils.code_context.generate_module_readme._build_callers → _warnings.catch_warnings() (line 661)
  utils.code_context.generate_module_readme._build_callers → _warnings.simplefilter('ignore') (line 662)
  utils.code_context.generate_module_readme._build_callers → _ast.parse(source) (line 663)
  utils.code_context.generate_module_readme._build_callers → _ast.walk(tree) (line 670)
  utils.code_context.generate_module_readme._build_callers → mod.startswith(module_path + '.') (line 673)
  utils.code_context.generate_module_readme._build_callers → imported_names.add(alias.asname or alias.name) (line 676)
  utils.code_context.generate_module_readme._build_callers → ...startswith(module_path + '.') (line 679)
  utils.code_context.generate_module_readme._build_callers → _ast.walk(tree) (line 687)
  utils.code_context.generate_module_readme._build_callers → called.add(node.func.id) (line 690)
  utils.code_context.generate_module_readme._build_callers → called.add(node.func.attr) (line 692)
  utils.code_context.generate_module_readme._build_callers → py_file.relative_to(PROJECT_ROOT) (line 699)
  utils.code_context.generate_module_readme._build_callers → rows.append((str(rel).replace('\\', '/'), fn)) (line 703)
  utils.code_context.generate_module_readme._build_callers → replace('\\', '/') (line 703)
  utils.code_context.generate_module_readme._build_callers → rows.sort() (line 708)
  utils.code_context.generate_module_readme._build_callers → join(table_lines) (line 718)
  utils.code_context.generate_module_readme._build_callers → utils.code_context.generate_module_readme.chr(10) (line 718)
  utils.code_context.generate_module_readme._extract_auto_blocks → m.group(1) (line 728)
  utils.code_context.generate_module_readme._extract_auto_blocks → m.group(2) (line 728)
  utils.code_context.generate_module_readme._extract_auto_blocks → _AUTO_PATTERN.finditer(content) (line 728)
  utils.code_context.generate_module_readme._wrap_auto → content.strip() (line 732)
  utils.code_context.generate_module_readme.replacer → m.group(1) (line 744)
  utils.code_context.generate_module_readme.replacer → utils.code_context.generate_module_readme._wrap_auto(sid, sections[sid]) (line 746)
  utils.code_context.generate_module_readme.replacer → m.group(0) (line 747)
  utils.code_context.generate_module_readme._merge_sections → _AUTO_PATTERN.sub(replacer, result) (line 749)
  utils.code_context.generate_module_readme._merge_sections → keys() (line 752)
  utils.code_context.generate_module_readme._merge_sections → utils.code_context.generate_module_readme._extract_auto_blocks(result) (line 752)
  utils.code_context.generate_module_readme._merge_sections → result.rstrip() (line 759)
  utils.code_context.generate_module_readme._merge_sections → utils.code_context.generate_module_readme._wrap_auto(sid, sections[sid]) (line 759)
  utils.code_context.generate_module_readme._build_initial_file → replace('\\', '.') (line 774)
  utils.code_context.generate_module_readme._build_initial_file → subdirectory.replace('/', '.') (line 774)
  utils.code_context.generate_module_readme._build_initial_file → utils.code_context.generate_module_readme._find_child_readmes(subdirectory) (line 775)
  utils.code_context.generate_module_readme._build_initial_file → parts.append(f'# `{module_name}` — Module Overview\n') (line 778)
  utils.code_context.generate_module_readme._build_initial_file → parts.append('> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.\n> Everything else is yours to edit freely and will never be overwritten.\n') (line 779)
  utils.code_context.generate_module_readme._build_initial_file → parts.append(_wrap_auto('meta', _build_meta(subdirectory, output_path, mode, scope, child_readmes or None))) (line 786)
  utils.code_context.generate_module_readme._build_initial_file → utils.code_context.generate_module_readme._wrap_auto('meta', _build_meta(subdirectory, output_path, mode, scope, child_readmes or None)) (line 786)
  utils.code_context.generate_module_readme._build_initial_file → utils.code_context.generate_module_readme._build_meta(subdirectory, output_path, mode, scope, child_readmes or None) (line 786)
  utils.code_context.generate_module_readme._build_initial_file → parts.append('') (line 789)
  utils.code_context.generate_module_readme._build_initial_file → parts.append(_ARCHITECTURE_STUB) (line 792)
  utils.code_context.generate_module_readme._build_initial_file → parts.append(_wrap_auto('tree', _build_tree(subdirectory, child_readmes or None))) (line 795)
  utils.code_context.generate_module_readme._build_initial_file → utils.code_context.generate_module_readme._wrap_auto('tree', _build_tree(subdirectory, child_readmes or None)) (line 795)
  utils.code_context.generate_module_readme._build_initial_file → utils.code_context.generate_module_readme._build_tree(subdirectory, child_readmes or None) (line 795)
  utils.code_context.generate_module_readme._build_initial_file → parts.append('') (line 796)
  utils.code_context.generate_module_readme._build_initial_file → parts.append(_wrap_auto('signatures', _build_signatures(subdirectory, mode, child_readmes or None))) (line 799)
  utils.code_context.generate_module_readme._build_initial_file → utils.code_context.generate_module_readme._wrap_auto('signatures', _build_signatures(subdirectory, mode, child_readmes or None)) (line 799)
  utils.code_context.generate_module_readme._build_initial_file → utils.code_context.generate_module_readme._build_signatures(subdirectory, mode, child_readmes or None) (line 799)
  utils.code_context.generate_module_readme._build_initial_file → parts.append('') (line 802)
  utils.code_context.generate_module_readme._build_initial_file → utils.code_context.generate_module_readme._build_call_graph(subdirectory, scope, project_noise) (line 806)
  utils.code_context.generate_module_readme._build_initial_file → parts.append(_wrap_auto('call_graph', cg)) (line 808)
  utils.code_context.generate_module_readme._build_initial_file → utils.code_context.generate_module_readme._wrap_auto('call_graph', cg) (line 808)
  utils.code_context.generate_module_readme._build_initial_file → parts.append('') (line 809)
  utils.code_context.generate_module_readme._build_initial_file → utils.code_context.generate_module_readme._build_callers(subdirectory, entry_points) (line 813)
  utils.code_context.generate_module_readme._build_initial_file → parts.append(_wrap_auto('callers', callers)) (line 815)
  utils.code_context.generate_module_readme._build_initial_file → utils.code_context.generate_module_readme._wrap_auto('callers', callers) (line 815)
  utils.code_context.generate_module_readme._build_initial_file → parts.append('') (line 816)
  utils.code_context.generate_module_readme._build_initial_file → utils.code_context.generate_module_readme._build_dependencies(subdirectory) (line 819)
  utils.code_context.generate_module_readme._build_initial_file → parts.append(_wrap_auto('dependencies', deps)) (line 821)
  utils.code_context.generate_module_readme._build_initial_file → utils.code_context.generate_module_readme._wrap_auto('dependencies', deps) (line 821)
  utils.code_context.generate_module_readme._build_initial_file → parts.append('') (line 822)
  utils.code_context.generate_module_readme._build_initial_file → join(parts) (line 824)
  utils.code_context.generate_module_readme.run → output_path.exists() (line 840)
  utils.code_context.generate_module_readme.run → output_path.read_text() (line 843)
  utils.code_context.generate_module_readme.run → _AUTO_PATTERN.search(existing) (line 847)
  utils.code_context.generate_module_readme.run → logger.info('Existing file has no AUTO blocks — treating as new: %s', output_path) (line 848)
  utils.code_context.generate_module_readme.run → utils.code_context.generate_module_readme._find_child_readmes(subdirectory) (line 852)
  utils.code_context.generate_module_readme.run → logger.info('Creating new README: %s', output_path) (line 855)
  utils.code_context.generate_module_readme.run → utils.code_context.generate_module_readme._build_initial_file(subdirectory, output_path, mode, scope, project_noise, include_call_graph) (line 856)
  utils.code_context.generate_module_readme.run → logger.info('Updating existing README: %s', output_path) (line 861)
  utils.code_context.generate_module_readme.run → output_path.read_text() (line 862)
  utils.code_context.generate_module_readme.run → utils.code_context.generate_module_readme._build_meta(subdirectory, output_path, mode, scope, child_readmes or None) (line 865)
  utils.code_context.generate_module_readme.run → utils.code_context.generate_module_readme._build_tree(subdirectory, child_readmes or None) (line 868)
  utils.code_context.generate_module_readme.run → utils.code_context.generate_module_readme._build_signatures(subdirectory, mode, child_readmes or None) (line 869)
  utils.code_context.generate_module_readme.run → utils.code_context.generate_module_readme._build_call_graph(subdirectory, scope, project_noise) (line 874)
  utils.code_context.generate_module_readme.run → utils.code_context.generate_module_readme._build_callers(subdirectory, entry_points) (line 879)
  utils.code_context.generate_module_readme.run → utils.code_context.generate_module_readme._build_dependencies(subdirectory) (line 883)
  utils.code_context.generate_module_readme.run → utils.code_context.generate_module_readme._merge_sections(existing, sections) (line 887)
  utils.code_context.generate_module_readme.run → ...mkdir() (line 889)
  utils.code_context.generate_module_readme.run → output_path.write_text(content) (line 890)
  utils.code_context.generate_module_readme.run → output_path.is_relative_to(PROJECT_ROOT) (line 892)
  utils.code_context.generate_module_readme.run → output_path.relative_to(PROJECT_ROOT) (line 892)
  utils.code_context.generate_module_readme.run → extra_sections.append('call_graph') (line 896)
  utils.code_context.generate_module_readme.run → extra_sections.append('callers') (line 898)
  utils.code_context.generate_module_readme.run → extra_sections.append('dependencies') (line 899)
  utils.code_context.generate_module_readme.run → join(extra_sections) (line 900)
  utils.code_context.generate_module_readme.run → utils.code_context.generate_module_readme._check_child_staleness(child_readmes) (line 907)
  utils.code_context.generate_module_readme.run_cascade → target.iterdir() (line 957)
  utils.code_context.generate_module_readme.run_cascade → child.is_dir() (line 958)
  utils.code_context.generate_module_readme.run_cascade → ...startswith(('.', '_')) (line 960)
  utils.code_context.generate_module_readme.run_cascade → child.rglob('*.py') (line 962)
  utils.code_context.generate_module_readme.run_cascade → candidates.append((child, py_count)) (line 964)
  utils.code_context.generate_module_readme.run_cascade → logger.warning('Permission denied reading %s', target) (line 966)
  utils.code_context.generate_module_readme.run_cascade → exists() (line 975)
  utils.code_context.generate_module_readme.run_cascade → path.relative_to(PROJECT_ROOT) (line 977)
  utils.code_context.generate_module_readme.run_cascade → child_readme.exists() (line 984)
  utils.code_context.generate_module_readme.run_cascade → subdir_path.relative_to(PROJECT_ROOT) (line 987)
  utils.code_context.generate_module_readme.run_cascade → utils.code_context.generate_module_readme.run() (line 989)
  utils.code_context.generate_module_readme.run_cascade → new_children.append(child_readme) (line 998)
  utils.code_context.generate_module_readme.run_cascade → utils.code_context.generate_module_readme.run() (line 1003)
  utils.code_context.generate_module_readme.main → argparse.ArgumentParser() (line 1023)
  utils.code_context.generate_module_readme.main → parser.add_argument('subdirectory') (line 1027)
  utils.code_context.generate_module_readme.main → parser.add_argument('--output') (line 1028)
  utils.code_context.generate_module_readme.main → parser.add_argument('--mode') (line 1033)
  utils.code_context.generate_module_readme.main → parser.add_argument('--call-graph-scope') (line 1039)
  utils.code_context.generate_module_readme.main → parser.add_argument('--project-noise') (line 1044)
  utils.code_context.generate_module_readme.main → parser.add_argument('--no-call-graph') (line 1049)
  utils.code_context.generate_module_readme.main → parser.add_argument('--cascade') (line 1054)
  utils.code_context.generate_module_readme.main → parser.add_argument('--cascade-min-files') (line 1062)
  utils.code_context.generate_module_readme.main → parser.add_argument('--cascade-child-mode') (line 1069)
  utils.code_context.generate_module_readme.main → parser.parse_args() (line 1076)
  utils.code_context.generate_module_readme.main → ...strip('/\\') (line 1078)
  utils.code_context.generate_module_readme.main → utils.code_context.generate_module_readme.Path(args.output) (line 1081)
  utils.code_context.generate_module_readme.main → output_path.is_absolute() (line 1082)
  utils.code_context.generate_module_readme.main → s.strip() (line 1087)
  utils.code_context.generate_module_readme.main → ...split(',') (line 1087)
  utils.code_context.generate_module_readme.main → s.strip() (line 1088)
  utils.code_context.generate_module_readme.main → ...split(',') (line 1088)
  utils.code_context.generate_module_readme.main → logging.basicConfig() (line 1091)
  utils.code_context.generate_module_readme.main → utils.code_context.generate_module_readme.run_cascade() (line 1094)
  utils.code_context.generate_module_readme.main → utils.code_context.generate_module_readme.run() (line 1104)
  Global Scope → utils.code_context.generate_module_readme.main() (line 1115)
# Call graph: utils.code_context.tests.test_integration
  Global Scope → ...insert(0, str(Path(__file__).parent.parent.parent.parent)) (line 14)
  Global Scope → utils.code_context.tests.test_integration.Path(__file__) (line 14)
  utils.code_context.tests.test_integration.simple_project → root.mkdir() (line 36)
  utils.code_context.tests.test_integration.simple_project → write_text("def main():\n    print('hello')\n\nmain()\n") (line 37)
  utils.code_context.tests.test_integration.simple_project → write_text('# utility functions\ndef helper(x):\n    return x * 2\n') (line 41)
  utils.code_context.tests.test_integration.simple_project → nm.mkdir() (line 46)
  utils.code_context.tests.test_integration.simple_project → write_text('module.exports = {}') (line 47)
  utils.code_context.tests.test_integration.simple_project → src.mkdir() (line 49)
  utils.code_context.tests.test_integration.simple_project → write_text('class Service:\n    def run(self):\n        pass\n') (line 50)
  utils.code_context.tests.test_integration.simple_project → write_text('') (line 54)
  utils.code_context.tests.test_integration.simple_project → pytest.fixture() (line 23)
  utils.code_context.tests.test_integration.multi_lang_project → root.mkdir() (line 61)
  utils.code_context.tests.test_integration.multi_lang_project → write_text('def start(): pass\n') (line 62)
  utils.code_context.tests.test_integration.multi_lang_project → write_text('export function init() {}\n') (line 63)
  utils.code_context.tests.test_integration.multi_lang_project → write_text('body { margin: 0; }\n') (line 64)
  utils.code_context.tests.test_integration.multi_lang_project → write_text('docs\n') (line 65)
  utils.code_context.tests.test_integration.multi_lang_project → pytest.fixture() (line 58)
  utils.code_context.tests.test_integration.nested_project → root.mkdir() (line 72)
  utils.code_context.tests.test_integration.nested_project → ...mkdir() (line 79)
  utils.code_context.tests.test_integration.nested_project → p.write_text(content) (line 80)
  utils.code_context.tests.test_integration.nested_project → pytest.fixture() (line 69)
  utils.code_context.tests.test_integration.test_build_returns_result → utils.code_context.tests.test_integration.CodeContextBuilder() (line 90)
  utils.code_context.tests.test_integration.test_build_returns_result → builder.build() (line 91)
  utils.code_context.tests.test_integration.test_included_files_excludes_node_modules → utils.code_context.tests.test_integration.CodeContextBuilder() (line 95)
  utils.code_context.tests.test_integration.test_included_files_excludes_node_modules → builder.build() (line 96)
  utils.code_context.tests.test_integration.test_included_files_excludes_init → utils.code_context.tests.test_integration.CodeContextBuilder() (line 100)
  utils.code_context.tests.test_integration.test_included_files_excludes_init → builder.build() (line 101)
  utils.code_context.tests.test_integration.test_included_files_contains_python_files → utils.code_context.tests.test_integration.CodeContextBuilder() (line 105)
  utils.code_context.tests.test_integration.test_included_files_contains_python_files → builder.build() (line 106)
  utils.code_context.tests.test_integration.test_combined_text_contains_tree → utils.code_context.tests.test_integration.CodeContextBuilder() (line 111)
  utils.code_context.tests.test_integration.test_combined_text_contains_tree → builder.build() (line 112)
  utils.code_context.tests.test_integration.test_output_header_present → utils.code_context.tests.test_integration.CodeContextBuilder() (line 117)
  utils.code_context.tests.test_integration.test_output_header_present → builder.build() (line 118)
  utils.code_context.tests.test_integration.test_stats_correct_file_count → utils.code_context.tests.test_integration.CodeContextBuilder() (line 123)
  utils.code_context.tests.test_integration.test_stats_correct_file_count → builder.build() (line 124)
  utils.code_context.tests.test_integration.test_tree_only_contains_tree → utils.code_context.tests.test_integration.CodeContextBuilder() (line 134)
  utils.code_context.tests.test_integration.test_tree_only_contains_tree → builder.build() (line 135)
  utils.code_context.tests.test_integration.test_tree_only_no_file_content → utils.code_context.tests.test_integration.CodeContextBuilder() (line 141)
  utils.code_context.tests.test_integration.test_tree_only_no_file_content → builder.build() (line 142)
  utils.code_context.tests.test_integration.test_tree_only_saves_file → utils.code_context.tests.test_integration.CodeContextBuilder() (line 148)
  utils.code_context.tests.test_integration.test_tree_only_saves_file → builder.build() (line 153)
  utils.code_context.tests.test_integration.test_tree_only_saves_file → builder.save(result) (line 154)
  utils.code_context.tests.test_integration.test_tree_only_saves_file → saved.exists() (line 156)
  utils.code_context.tests.test_integration.test_tree_only_output_mode_recorded → utils.code_context.tests.test_integration.CodeContextBuilder() (line 160)
  utils.code_context.tests.test_integration.test_tree_only_output_mode_recorded → builder.build() (line 161)
  utils.code_context.tests.test_integration.test_signatures_contains_tree → utils.code_context.tests.test_integration.CodeContextBuilder() (line 171)
  utils.code_context.tests.test_integration.test_signatures_contains_tree → builder.build() (line 172)
  utils.code_context.tests.test_integration.test_signatures_contains_function_names → utils.code_context.tests.test_integration.CodeContextBuilder() (line 176)
  utils.code_context.tests.test_integration.test_signatures_contains_function_names → builder.build() (line 177)
  utils.code_context.tests.test_integration.test_signatures_contains_class_name → utils.code_context.tests.test_integration.CodeContextBuilder() (line 182)
  utils.code_context.tests.test_integration.test_signatures_contains_class_name → builder.build() (line 183)
  utils.code_context.tests.test_integration.test_signatures_no_function_bodies → utils.code_context.tests.test_integration.CodeContextBuilder() (line 187)
  utils.code_context.tests.test_integration.test_signatures_no_function_bodies → builder.build() (line 188)
  utils.code_context.tests.test_integration.test_signatures_blocks_populated → utils.code_context.tests.test_integration.CodeContextBuilder() (line 193)
  utils.code_context.tests.test_integration.test_signatures_blocks_populated → builder.build() (line 194)
  utils.code_context.tests.test_integration.test_signatures_filepath_labels_present → utils.code_context.tests.test_integration.CodeContextBuilder() (line 198)
  utils.code_context.tests.test_integration.test_signatures_filepath_labels_present → builder.build() (line 199)
  utils.code_context.tests.test_integration.test_signatures_saves_file → utils.code_context.tests.test_integration.CodeContextBuilder() (line 204)
  utils.code_context.tests.test_integration.test_signatures_saves_file → builder.build() (line 209)
  utils.code_context.tests.test_integration.test_signatures_saves_file → builder.save(result) (line 210)
  utils.code_context.tests.test_integration.test_signatures_much_smaller_than_clean → utils.code_context.tests.test_integration.CodeContextBuilder() (line 215)
  utils.code_context.tests.test_integration.test_signatures_much_smaller_than_clean → utils.code_context.tests.test_integration.CodeContextBuilder() (line 216)
  utils.code_context.tests.test_integration.test_signatures_much_smaller_than_clean → sig_builder.build() (line 217)
  utils.code_context.tests.test_integration.test_signatures_much_smaller_than_clean → clean_builder.build() (line 218)
  utils.code_context.tests.test_integration.test_clean_strips_python_comments → utils.code_context.tests.test_integration.CodeContextBuilder() (line 228)
  utils.code_context.tests.test_integration.test_clean_strips_python_comments → builder.build() (line 229)
  utils.code_context.tests.test_integration.test_clean_contains_code → utils.code_context.tests.test_integration.CodeContextBuilder() (line 233)
  utils.code_context.tests.test_integration.test_clean_contains_code → builder.build() (line 234)
  utils.code_context.tests.test_integration.test_clean_contains_file_headers → utils.code_context.tests.test_integration.CodeContextBuilder() (line 238)
  utils.code_context.tests.test_integration.test_clean_contains_file_headers → builder.build() (line 239)
  utils.code_context.tests.test_integration.test_clean_saves_with_mode_in_filename → utils.code_context.tests.test_integration.CodeContextBuilder() (line 244)
  utils.code_context.tests.test_integration.test_clean_saves_with_mode_in_filename → builder.build() (line 249)
  utils.code_context.tests.test_integration.test_clean_saves_with_mode_in_filename → builder.save(result) (line 250)
  utils.code_context.tests.test_integration.test_original_preserves_comments → utils.code_context.tests.test_integration.CodeContextBuilder() (line 260)
  utils.code_context.tests.test_integration.test_original_preserves_comments → builder.build() (line 261)
  utils.code_context.tests.test_integration.test_original_saves_with_mode_in_filename → utils.code_context.tests.test_integration.CodeContextBuilder() (line 266)
  utils.code_context.tests.test_integration.test_original_saves_with_mode_in_filename → builder.build() (line 271)
  utils.code_context.tests.test_integration.test_original_saves_with_mode_in_filename → builder.save(result) (line 272)
  utils.code_context.tests.test_integration.test_original_output_mode_recorded → utils.code_context.tests.test_integration.CodeContextBuilder() (line 276)
  utils.code_context.tests.test_integration.test_original_output_mode_recorded → builder.build() (line 277)
  utils.code_context.tests.test_integration.test_prefix_prepended → utils.code_context.tests.test_integration.CodeContextBuilder() (line 287)
  utils.code_context.tests.test_integration.test_prefix_prepended → builder.build() (line 291)
  utils.code_context.tests.test_integration.test_suffix_appended → utils.code_context.tests.test_integration.CodeContextBuilder() (line 295)
  utils.code_context.tests.test_integration.test_suffix_appended → builder.build() (line 299)
  utils.code_context.tests.test_integration.test_prefix_appears_before_suffix → utils.code_context.tests.test_integration.CodeContextBuilder() (line 303)
  utils.code_context.tests.test_integration.test_prefix_appears_before_suffix → builder.build() (line 308)
  utils.code_context.tests.test_integration.test_prefix_appears_before_suffix → ...index('START') (line 309)
  utils.code_context.tests.test_integration.test_prefix_appears_before_suffix → ...index('END') (line 309)
  utils.code_context.tests.test_integration.test_prefix_works_in_tree_only_mode → utils.code_context.tests.test_integration.CodeContextBuilder() (line 312)
  utils.code_context.tests.test_integration.test_prefix_works_in_tree_only_mode → builder.build() (line 317)
  utils.code_context.tests.test_integration.test_subdirectory_limits_scan → utils.code_context.tests.test_integration.CodeContextBuilder() (line 327)
  utils.code_context.tests.test_integration.test_subdirectory_limits_scan → builder.build() (line 331)
  utils.code_context.tests.test_integration.test_subdirectory_tree_shows_scanned_dir → utils.code_context.tests.test_integration.CodeContextBuilder() (line 337)
  utils.code_context.tests.test_integration.test_subdirectory_tree_shows_scanned_dir → builder.build() (line 341)
  utils.code_context.tests.test_integration.test_additional_file_included_in_file_list → extra.write_text('EXTRA = True\n') (line 352)
  utils.code_context.tests.test_integration.test_additional_file_included_in_file_list → utils.code_context.tests.test_integration.CodeContextBuilder() (line 353)
  utils.code_context.tests.test_integration.test_additional_file_included_in_file_list → builder.build() (line 357)
  utils.code_context.tests.test_integration.test_additional_file_content_appears_in_original_mode → extra.write_text('EXTRA_MARKER_12345 = True\n') (line 362)
  utils.code_context.tests.test_integration.test_additional_file_content_appears_in_original_mode → utils.code_context.tests.test_integration.CodeContextBuilder() (line 363)
  utils.code_context.tests.test_integration.test_additional_file_content_appears_in_original_mode → builder.build() (line 368)
  utils.code_context.tests.test_integration.test_add_extra_exclude_directory → utils.code_context.tests.test_integration.CodeContextBuilder() (line 378)
  utils.code_context.tests.test_integration.test_add_extra_exclude_directory → builder.build() (line 382)
  utils.code_context.tests.test_integration.test_remove_default_exclude → utils.code_context.tests.test_integration.CodeContextBuilder() (line 386)
  utils.code_context.tests.test_integration.test_remove_default_exclude → builder.build() (line 390)
  utils.code_context.tests.test_integration.test_include_extensions_whitelist → utils.code_context.tests.test_integration.CodeContextBuilder() (line 394)
  utils.code_context.tests.test_integration.test_include_extensions_whitelist → builder.build() (line 398)
  utils.code_context.tests.test_integration.test_save_creates_combined_file → utils.code_context.tests.test_integration.CodeContextBuilder() (line 411)
  utils.code_context.tests.test_integration.test_save_creates_combined_file → builder.build() (line 415)
  utils.code_context.tests.test_integration.test_save_creates_combined_file → builder.save(result) (line 416)
  utils.code_context.tests.test_integration.test_save_creates_combined_file → saved.exists() (line 417)
  utils.code_context.tests.test_integration.test_saved_file_contains_tree_and_content → utils.code_context.tests.test_integration.CodeContextBuilder() (line 421)
  utils.code_context.tests.test_integration.test_saved_file_contains_tree_and_content → builder.build() (line 426)
  utils.code_context.tests.test_integration.test_saved_file_contains_tree_and_content → builder.save(result) (line 427)
  utils.code_context.tests.test_integration.test_saved_file_contains_tree_and_content → saved.read_text() (line 428)
  utils.code_context.tests.test_integration.test_save_creates_export_directory_if_missing → utils.code_context.tests.test_integration.CodeContextBuilder() (line 434)
  utils.code_context.tests.test_integration.test_save_creates_export_directory_if_missing → builder.build() (line 438)
  utils.code_context.tests.test_integration.test_save_creates_export_directory_if_missing → builder.save(result) (line 439)
  utils.code_context.tests.test_integration.test_save_creates_export_directory_if_missing → export_dir.exists() (line 440)
  utils.code_context.tests.test_integration.test_individual_save_creates_files → utils.code_context.tests.test_integration.CodeContextBuilder() (line 444)
  utils.code_context.tests.test_integration.test_individual_save_creates_files → builder.build() (line 451)
  utils.code_context.tests.test_integration.test_individual_save_creates_files → builder.save(result) (line 452)
  utils.code_context.tests.test_integration.test_individual_save_creates_files → export_dir.glob('*.txt') (line 453)
  utils.code_context.tests.test_integration.test_filename_includes_output_mode → utils.code_context.tests.test_integration.CodeContextBuilder() (line 459)
  utils.code_context.tests.test_integration.test_filename_includes_output_mode → builder.build() (line 464)
  utils.code_context.tests.test_integration.test_filename_includes_output_mode → builder.save(result) (line 465)
  utils.code_context.tests.test_integration.test_default_excludes_txt_and_css → utils.code_context.tests.test_integration.CodeContextBuilder() (line 475)
  utils.code_context.tests.test_integration.test_default_excludes_txt_and_css → builder.build() (line 476)
  utils.code_context.tests.test_integration.test_py_and_ts_included_when_ts_not_excluded → utils.code_context.tests.test_integration.CodeContextBuilder() (line 482)
  utils.code_context.tests.test_integration.test_py_and_ts_included_when_ts_not_excluded → builder.build() (line 486)
  utils.code_context.tests.test_integration.test_all_deep_files_discovered → utils.code_context.tests.test_integration.CodeContextBuilder() (line 498)
  utils.code_context.tests.test_integration.test_all_deep_files_discovered → builder.build() (line 502)
  utils.code_context.tests.test_integration.test_tree_shows_nested_structure → utils.code_context.tests.test_integration.CodeContextBuilder() (line 507)
  utils.code_context.tests.test_integration.test_tree_shows_nested_structure → builder.build() (line 511)
  utils.code_context.tests.test_integration.test_file_headers_use_relative_paths_original_mode → utils.code_context.tests.test_integration.CodeContextBuilder() (line 516)
  utils.code_context.tests.test_integration.test_file_headers_use_relative_paths_original_mode → builder.build() (line 521)
# Call graph: utils.code_context.tests.test_code_extractor
  Global Scope → ...insert(0, str(Path(__file__).parent.parent.parent.parent)) (line 27)
  Global Scope → utils.code_context.tests.test_code_extractor.Path(__file__) (line 27)
  utils.code_context.tests.test_code_extractor.make_extractor → utils.code_context.tests.test_code_extractor.Path(f'/tmp/test_file{suffix}') (line 38)
  utils.code_context.tests.test_code_extractor.make_extractor → p.write_text(content) (line 39)
  utils.code_context.tests.test_code_extractor.make_extractor → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 40)
  utils.code_context.tests.test_code_extractor.test_reads_utf8_file → p.write_text('x = 1\n') (line 50)
  utils.code_context.tests.test_code_extractor.test_reads_utf8_file → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 51)
  utils.code_context.tests.test_code_extractor.test_original_char_count → p.write_text(content) (line 57)
  utils.code_context.tests.test_code_extractor.test_original_char_count → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 58)
  utils.code_context.tests.test_code_extractor.test_nonexistent_file_returns_none → utils.code_context.tests.test_code_extractor.CodeExtractor(tmp_path / 'does_not_exist.py') (line 62)
  utils.code_context.tests.test_code_extractor.test_get_content_original_returns_original → p.write_text('pass') (line 68)
  utils.code_context.tests.test_code_extractor.test_get_content_original_returns_original → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 69)
  utils.code_context.tests.test_code_extractor.test_get_content_original_returns_original → ex.get_content('original') (line 70)
  utils.code_context.tests.test_code_extractor.test_get_content_clean_before_strip_returns_original → p.write_text('# comment\npass') (line 74)
  utils.code_context.tests.test_code_extractor.test_get_content_clean_before_strip_returns_original → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 75)
  utils.code_context.tests.test_code_extractor.test_get_content_clean_before_strip_returns_original → ex.get_content('clean') (line 77)
  utils.code_context.tests.test_code_extractor.test_removes_hash_comment → p.write_text('x = 1  # inline comment\ny = 2\n') (line 87)
  utils.code_context.tests.test_code_extractor.test_removes_hash_comment → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 88)
  utils.code_context.tests.test_code_extractor.test_removes_hash_comment → ex.strip_comments() (line 89)
  utils.code_context.tests.test_code_extractor.test_removes_standalone_hash_comment → p.write_text('# This is a comment\ndef foo():\n    pass\n') (line 96)
  utils.code_context.tests.test_code_extractor.test_removes_standalone_hash_comment → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 97)
  utils.code_context.tests.test_code_extractor.test_removes_standalone_hash_comment → ex.strip_comments() (line 98)
  utils.code_context.tests.test_code_extractor.test_removes_triple_double_quote_docstring → p.write_text('def foo():\n    """This is a docstring."""\n    return 1\n') (line 104)
  utils.code_context.tests.test_code_extractor.test_removes_triple_double_quote_docstring → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 105)
  utils.code_context.tests.test_code_extractor.test_removes_triple_double_quote_docstring → ex.strip_comments() (line 106)
  utils.code_context.tests.test_code_extractor.test_removes_triple_single_quote_docstring → p.write_text("def foo():\n    '''Single quote docstring'''\n    return 2\n") (line 112)
  utils.code_context.tests.test_code_extractor.test_removes_triple_single_quote_docstring → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 113)
  utils.code_context.tests.test_code_extractor.test_removes_triple_single_quote_docstring → ex.strip_comments() (line 114)
  utils.code_context.tests.test_code_extractor.test_removes_multiline_docstring → p.write_text(content) (line 121)
  utils.code_context.tests.test_code_extractor.test_removes_multiline_docstring → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 122)
  utils.code_context.tests.test_code_extractor.test_removes_multiline_docstring → ex.strip_comments() (line 123)
  utils.code_context.tests.test_code_extractor.test_preserves_regular_strings → p.write_text('msg = "hello world"\n') (line 129)
  utils.code_context.tests.test_code_extractor.test_preserves_regular_strings → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 130)
  utils.code_context.tests.test_code_extractor.test_preserves_regular_strings → ex.strip_comments() (line 131)
  utils.code_context.tests.test_code_extractor.test_clean_char_count_less_than_original → p.write_text('# lots of comments\n# more comments\nx = 1\n') (line 136)
  utils.code_context.tests.test_code_extractor.test_clean_char_count_less_than_original → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 137)
  utils.code_context.tests.test_code_extractor.test_clean_char_count_less_than_original → ex.strip_comments() (line 138)
  utils.code_context.tests.test_code_extractor.test_removes_single_line_comment → p.write_text('const x = 1; // inline comment\nconst y = 2;\n') (line 150)
  utils.code_context.tests.test_code_extractor.test_removes_single_line_comment → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 151)
  utils.code_context.tests.test_code_extractor.test_removes_single_line_comment → ex.strip_comments() (line 152)
  utils.code_context.tests.test_code_extractor.test_removes_block_comment → p.write_text('/* This is a block comment */\nconst z = 3;\n') (line 159)
  utils.code_context.tests.test_code_extractor.test_removes_block_comment → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 160)
  utils.code_context.tests.test_code_extractor.test_removes_block_comment → ex.strip_comments() (line 161)
  utils.code_context.tests.test_code_extractor.test_removes_multiline_block_comment → p.write_text(content) (line 168)
  utils.code_context.tests.test_code_extractor.test_removes_multiline_block_comment → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 169)
  utils.code_context.tests.test_code_extractor.test_removes_multiline_block_comment → ex.strip_comments() (line 170)
  utils.code_context.tests.test_code_extractor.test_removes_jsdoc_comment → p.write_text(content) (line 177)
  utils.code_context.tests.test_code_extractor.test_removes_jsdoc_comment → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 178)
  utils.code_context.tests.test_code_extractor.test_removes_jsdoc_comment → ex.strip_comments() (line 179)
  utils.code_context.tests.test_code_extractor.test_collapses_three_blank_lines_to_two → p.write_text('x = 1\n\n\n\ny = 2\n') (line 191)
  utils.code_context.tests.test_code_extractor.test_collapses_three_blank_lines_to_two → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 192)
  utils.code_context.tests.test_code_extractor.test_collapses_three_blank_lines_to_two → ex.strip_comments() (line 193)
  utils.code_context.tests.test_code_extractor.test_preserves_single_blank_line → p.write_text('x = 1\n\ny = 2\n') (line 199)
  utils.code_context.tests.test_code_extractor.test_preserves_single_blank_line → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 200)
  utils.code_context.tests.test_code_extractor.test_preserves_single_blank_line → ex.strip_comments() (line 201)
  utils.code_context.tests.test_code_extractor.test_preserves_double_blank_line → p.write_text('def foo():\n    pass\n\n\ndef bar():\n    pass\n') (line 207)
  utils.code_context.tests.test_code_extractor.test_preserves_double_blank_line → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 208)
  utils.code_context.tests.test_code_extractor.test_preserves_double_blank_line → ex.strip_comments() (line 209)
  utils.code_context.tests.test_code_extractor.test_header_contains_filepath → p.write_text('pass') (line 222)
  utils.code_context.tests.test_code_extractor.test_header_contains_filepath → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 223)
  utils.code_context.tests.test_code_extractor.test_header_contains_filepath → ex.file_header() (line 224)
  utils.code_context.tests.test_code_extractor.test_header_contains_separator → p.write_text('pass') (line 229)
  utils.code_context.tests.test_code_extractor.test_header_contains_separator → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 230)
  utils.code_context.tests.test_code_extractor.test_header_contains_separator → ex.file_header() (line 231)
  utils.code_context.tests.test_code_extractor.test_header_uses_relative_path_when_root_given → sub.mkdir() (line 236)
  utils.code_context.tests.test_code_extractor.test_header_uses_relative_path_when_root_given → p.write_text('pass') (line 238)
  utils.code_context.tests.test_code_extractor.test_header_uses_relative_path_when_root_given → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 239)
  utils.code_context.tests.test_code_extractor.test_header_uses_relative_path_when_root_given → ex.file_header() (line 240)
  utils.code_context.tests.test_code_extractor.test_header_uses_forward_slashes → sub.mkdir() (line 245)
  utils.code_context.tests.test_code_extractor.test_header_uses_forward_slashes → p.write_text('pass') (line 247)
  utils.code_context.tests.test_code_extractor.test_header_uses_forward_slashes → utils.code_context.tests.test_code_extractor.CodeExtractor(p) (line 248)
  utils.code_context.tests.test_code_extractor.test_header_uses_forward_slashes → ex.file_header() (line 249)
  utils.code_context.tests.test_code_extractor.test_extracts_top_level_function → p.write_text("def greet(name, greeting):\n    return f'{greeting} {name}'\n") (line 260)
  utils.code_context.tests.test_code_extractor.test_extracts_top_level_function → ASTAnalyzer.analyze_file(p) (line 261)
  utils.code_context.tests.test_code_extractor.test_extracts_class_with_methods → p.write_text('class MyClass:\n    def __init__(self, x):\n        self.x = x\n    def compute(self):\n        return self.x * 2\n') (line 270)
  utils.code_context.tests.test_code_extractor.test_extracts_class_with_methods → ASTAnalyzer.analyze_file(p) (line 277)
  utils.code_context.tests.test_code_extractor.test_methods_not_double_counted_as_functions → p.write_text('class Foo:\n    def bar(self):\n        pass\n\ndef standalone():\n    pass\n') (line 288)
  utils.code_context.tests.test_code_extractor.test_methods_not_double_counted_as_functions → ASTAnalyzer.analyze_file(p) (line 296)
  utils.code_context.tests.test_code_extractor.test_async_function_extracted → p.write_text('async def fetch(url: str) -> str:\n    return url\n') (line 303)
  utils.code_context.tests.test_code_extractor.test_async_function_extracted → ASTAnalyzer.analyze_file(p) (line 304)
  utils.code_context.tests.test_code_extractor.test_async_method_in_class → p.write_text('class Service:\n    async def run(self):\n        pass\n') (line 310)
  utils.code_context.tests.test_code_extractor.test_async_method_in_class → ASTAnalyzer.analyze_file(p) (line 315)
  utils.code_context.tests.test_code_extractor.test_non_python_file_returns_error → p.write_text('const x = 1;') (line 321)
  utils.code_context.tests.test_code_extractor.test_non_python_file_returns_error → ASTAnalyzer.analyze_file(p) (line 322)
  utils.code_context.tests.test_code_extractor.test_syntax_error_returns_graceful_error → p.write_text('def oops(\n    missing_close\n') (line 328)
  utils.code_context.tests.test_code_extractor.test_syntax_error_returns_graceful_error → ASTAnalyzer.analyze_file(p) (line 329)
  utils.code_context.tests.test_code_extractor.test_to_text_output_format → p.write_text('def top_func(a, b):\n    pass\n\nclass MyClass:\n    def method(self):\n        pass\n') (line 335)
  utils.code_context.tests.test_code_extractor.test_to_text_output_format → ASTAnalyzer.analyze_file(p) (line 342)
  utils.code_context.tests.test_code_extractor.test_to_text_output_format → result.to_text() (line 343)
  utils.code_context.tests.test_code_extractor.test_to_text_uses_relative_path → sub.mkdir() (line 353)
  utils.code_context.tests.test_code_extractor.test_to_text_uses_relative_path → p.write_text('def f(): pass\n') (line 355)
  utils.code_context.tests.test_code_extractor.test_to_text_uses_relative_path → ASTAnalyzer.analyze_file(p) (line 356)
  utils.code_context.tests.test_code_extractor.test_to_text_uses_relative_path → result.to_text() (line 357)
  utils.code_context.tests.test_code_extractor.test_analyze_files_batch → p.write_text(content) (line 368)
  utils.code_context.tests.test_code_extractor.test_analyze_files_batch → files.append(p) (line 369)
  utils.code_context.tests.test_code_extractor.test_analyze_files_batch → ASTAnalyzer.analyze_files(files) (line 370)
  utils.code_context.tests.test_code_extractor.test_empty_file_no_error → p.write_text('') (line 377)
  utils.code_context.tests.test_code_extractor.test_empty_file_no_error → ASTAnalyzer.analyze_file(p) (line 378)
  utils.code_context.tests.test_code_extractor.test_multiple_classes_extracted → p.write_text('class Alpha:\n    def run(self): pass\n\nclass Beta:\n    def execute(self): pass\n') (line 385)
  utils.code_context.tests.test_code_extractor.test_multiple_classes_extracted → ASTAnalyzer.analyze_file(p) (line 389)
# Call graph: utils.code_context.tests.test_tree_generator
  Global Scope → ...insert(0, str(Path(__file__).parent.parent.parent.parent)) (line 18)
  Global Scope → utils.code_context.tests.test_tree_generator.Path(__file__) (line 18)
  utils.code_context.tests.test_tree_generator.make_cfg → utils.code_context.tests.test_tree_generator.CodeContextConfig() (line 24)
  utils.code_context.tests.test_tree_generator.make_cfg → kwargs.items() (line 25)
  utils.code_context.tests.test_tree_generator.build_tree → utils.code_context.tests.test_tree_generator.make_cfg() (line 41)
  utils.code_context.tests.test_tree_generator.build_tree → generate() (line 42)
  utils.code_context.tests.test_tree_generator.build_tree → utils.code_context.tests.test_tree_generator.DirectoryTree(files, cfg, custom_root) (line 42)
  utils.code_context.tests.test_tree_generator.test_empty_file_list → utils.code_context.tests.test_tree_generator.make_cfg() (line 51)
  utils.code_context.tests.test_tree_generator.test_empty_file_list → utils.code_context.tests.test_tree_generator.build_tree([], cfg) (line 52)
  utils.code_context.tests.test_tree_generator.test_single_file_in_root → f.write_text('pass') (line 57)
  utils.code_context.tests.test_tree_generator.test_single_file_in_root → utils.code_context.tests.test_tree_generator.build_tree([f]) (line 58)
  utils.code_context.tests.test_tree_generator.test_multiple_files_appear → p.write_text('pass') (line 67)
  utils.code_context.tests.test_tree_generator.test_multiple_files_appear → files.append(p) (line 68)
  utils.code_context.tests.test_tree_generator.test_multiple_files_appear → utils.code_context.tests.test_tree_generator.build_tree(files) (line 69)
  utils.code_context.tests.test_tree_generator.test_nested_files_appear → sub.mkdir() (line 76)
  utils.code_context.tests.test_tree_generator.test_nested_files_appear → f.write_text('pass') (line 78)
  utils.code_context.tests.test_tree_generator.test_nested_files_appear → utils.code_context.tests.test_tree_generator.build_tree([f]) (line 80)
  utils.code_context.tests.test_tree_generator.test_unicode_box_drawing → f.write_text('pass') (line 87)
  utils.code_context.tests.test_tree_generator.test_unicode_box_drawing → utils.code_context.tests.test_tree_generator.build_tree([f]) (line 88)
  utils.code_context.tests.test_tree_generator.test_root_name_ends_with_slash → f.write_text('pass') (line 93)
  utils.code_context.tests.test_tree_generator.test_root_name_ends_with_slash → utils.code_context.tests.test_tree_generator.build_tree([f]) (line 94)
  utils.code_context.tests.test_tree_generator.test_root_name_ends_with_slash → result.splitlines() (line 95)
  utils.code_context.tests.test_tree_generator.test_root_name_ends_with_slash → first_line.endswith('/') (line 96)
  utils.code_context.tests.test_tree_generator.test_does_not_show_empty_sibling_dir → src.mkdir() (line 106)
  utils.code_context.tests.test_tree_generator.test_does_not_show_empty_sibling_dir → empty.mkdir() (line 108)
  utils.code_context.tests.test_tree_generator.test_does_not_show_empty_sibling_dir → f.write_text('pass') (line 110)
  utils.code_context.tests.test_tree_generator.test_does_not_show_empty_sibling_dir → utils.code_context.tests.test_tree_generator.make_cfg() (line 111)
  utils.code_context.tests.test_tree_generator.test_does_not_show_empty_sibling_dir → utils.code_context.tests.test_tree_generator.build_tree([f], cfg) (line 112)
  utils.code_context.tests.test_tree_generator.test_only_shows_paths_that_lead_to_included_files → ...mkdir() (line 118)
  utils.code_context.tests.test_tree_generator.test_only_shows_paths_that_lead_to_included_files → a.write_text('pass') (line 119)
  utils.code_context.tests.test_tree_generator.test_only_shows_paths_that_lead_to_included_files → b_dir.mkdir() (line 121)
  utils.code_context.tests.test_tree_generator.test_only_shows_paths_that_lead_to_included_files → utils.code_context.tests.test_tree_generator.make_cfg() (line 122)
  utils.code_context.tests.test_tree_generator.test_only_shows_paths_that_lead_to_included_files → utils.code_context.tests.test_tree_generator.build_tree([a], cfg) (line 123)
  utils.code_context.tests.test_tree_generator.test_shows_empty_sibling_dir → src.mkdir() (line 135)
  utils.code_context.tests.test_tree_generator.test_shows_empty_sibling_dir → empty.mkdir() (line 137)
  utils.code_context.tests.test_tree_generator.test_shows_empty_sibling_dir → f.write_text('pass') (line 139)
  utils.code_context.tests.test_tree_generator.test_shows_empty_sibling_dir → utils.code_context.tests.test_tree_generator.make_cfg() (line 140)
  utils.code_context.tests.test_tree_generator.test_shows_empty_sibling_dir → utils.code_context.tests.test_tree_generator.build_tree([f], cfg) (line 147)
  utils.code_context.tests.test_tree_generator.test_excluded_dirs_not_shown_in_full_mode → src.mkdir() (line 153)
  utils.code_context.tests.test_tree_generator.test_excluded_dirs_not_shown_in_full_mode → excl.mkdir() (line 155)
  utils.code_context.tests.test_tree_generator.test_excluded_dirs_not_shown_in_full_mode → f.write_text('pass') (line 157)
  utils.code_context.tests.test_tree_generator.test_excluded_dirs_not_shown_in_full_mode → utils.code_context.tests.test_tree_generator.make_cfg() (line 158)
  utils.code_context.tests.test_tree_generator.test_excluded_dirs_not_shown_in_full_mode → utils.code_context.tests.test_tree_generator.build_tree([f], cfg) (line 162)
  utils.code_context.tests.test_tree_generator.test_custom_root_overrides_common_prefix → src.mkdir() (line 174)
  utils.code_context.tests.test_tree_generator.test_custom_root_overrides_common_prefix → f.write_text('pass') (line 176)
  utils.code_context.tests.test_tree_generator.test_custom_root_overrides_common_prefix → utils.code_context.tests.test_tree_generator.make_cfg() (line 177)
  utils.code_context.tests.test_tree_generator.test_custom_root_overrides_common_prefix → utils.code_context.tests.test_tree_generator.build_tree([f], cfg) (line 178)
  utils.code_context.tests.test_tree_generator.test_custom_root_overrides_common_prefix → result.splitlines() (line 180)
  utils.code_context.tests.test_tree_generator.test_custom_root_different_from_file_location → deep.mkdir() (line 187)
  utils.code_context.tests.test_tree_generator.test_custom_root_different_from_file_location → f.write_text('pass') (line 189)
  utils.code_context.tests.test_tree_generator.test_custom_root_different_from_file_location → utils.code_context.tests.test_tree_generator.make_cfg() (line 190)
  utils.code_context.tests.test_tree_generator.test_custom_root_different_from_file_location → utils.code_context.tests.test_tree_generator.build_tree([f], cfg) (line 191)
  utils.code_context.tests.test_tree_generator.test_custom_root_different_from_file_location → result.splitlines() (line 192)
  utils.code_context.tests.test_tree_generator.test_entries_sorted_alphabetically → write_text('pass') (line 202)
  utils.code_context.tests.test_tree_generator.test_entries_sorted_alphabetically → utils.code_context.tests.test_tree_generator.build_tree([tmp_path / n for n in ['z_file.py', 'a_file.py', 'm_file.py']]) (line 203)
  utils.code_context.tests.test_tree_generator.test_entries_sorted_alphabetically → result.splitlines() (line 204)
  utils.code_context.tests.test_tree_generator.test_entries_sorted_alphabetically → l.split('── ') (line 206)
  utils.code_context.tests.test_tree_generator.test_directories_before_files → sub.mkdir() (line 211)
  utils.code_context.tests.test_tree_generator.test_directories_before_files → f_sub.write_text('pass') (line 213)
  utils.code_context.tests.test_tree_generator.test_directories_before_files → f_root.write_text('pass') (line 215)
  utils.code_context.tests.test_tree_generator.test_directories_before_files → utils.code_context.tests.test_tree_generator.build_tree([f_sub, f_root]) (line 216)
  utils.code_context.tests.test_tree_generator.test_directories_before_files → result.splitlines() (line 217)
  utils.code_context.tests.test_tree_generator.test_directories_before_files → l.split('── ') (line 218)
  utils.code_context.tests.test_tree_generator.test_depth_indentation_uses_pipe_chars → deep.mkdir() (line 232)
  utils.code_context.tests.test_tree_generator.test_depth_indentation_uses_pipe_chars → f.write_text('pass') (line 234)
  utils.code_context.tests.test_tree_generator.test_depth_indentation_uses_pipe_chars → utils.code_context.tests.test_tree_generator.build_tree([f]) (line 236)
  utils.code_context.tests.test_tree_generator.test_depth_indentation_uses_pipe_chars → result.splitlines() (line 237)
  utils.code_context.tests.test_tree_generator.test_multiple_files_same_dir_all_appear → sub.mkdir() (line 243)
  utils.code_context.tests.test_tree_generator.test_multiple_files_same_dir_all_appear → p.write_text('pass') (line 247)
  utils.code_context.tests.test_tree_generator.test_multiple_files_same_dir_all_appear → files.append(p) (line 248)
  utils.code_context.tests.test_tree_generator.test_multiple_files_same_dir_all_appear → utils.code_context.tests.test_tree_generator.build_tree(files) (line 249)
# Call graph: utils.code_context.tests.test_file_discovery
  Global Scope → ...insert(0, str(Path(__file__).parent.parent.parent.parent)) (line 17)
  Global Scope → utils.code_context.tests.test_file_discovery.Path(__file__) (line 17)
  utils.code_context.tests.test_file_discovery.make_cfg → utils.code_context.tests.test_file_discovery.CodeContextConfig() (line 23)
  utils.code_context.tests.test_file_discovery.make_cfg → kwargs.items() (line 24)
  utils.code_context.tests.test_file_discovery.test_excludes_exact_match → utils.code_context.tests.test_file_discovery.make_cfg() (line 35)
  utils.code_context.tests.test_file_discovery.test_excludes_exact_match → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 36)
  utils.code_context.tests.test_file_discovery.test_excludes_exact_match → fd.should_exclude_directory('node_modules') (line 37)
  utils.code_context.tests.test_file_discovery.test_case_insensitive_exact → utils.code_context.tests.test_file_discovery.make_cfg() (line 40)
  utils.code_context.tests.test_file_discovery.test_case_insensitive_exact → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 41)
  utils.code_context.tests.test_file_discovery.test_case_insensitive_exact → fd.should_exclude_directory('node_modules') (line 42)
  utils.code_context.tests.test_file_discovery.test_case_insensitive_exact → fd.should_exclude_directory('NODE_MODULES') (line 43)
  utils.code_context.tests.test_file_discovery.test_does_not_exclude_partial_name → utils.code_context.tests.test_file_discovery.make_cfg() (line 46)
  utils.code_context.tests.test_file_discovery.test_does_not_exclude_partial_name → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 47)
  utils.code_context.tests.test_file_discovery.test_does_not_exclude_partial_name → fd.should_exclude_directory('test') (line 48)
  utils.code_context.tests.test_file_discovery.test_does_not_exclude_partial_name → fd.should_exclude_directory('mytest') (line 51)
  utils.code_context.tests.test_file_discovery.test_empty_list_excludes_nothing → utils.code_context.tests.test_file_discovery.make_cfg() (line 54)
  utils.code_context.tests.test_file_discovery.test_empty_list_excludes_nothing → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 55)
  utils.code_context.tests.test_file_discovery.test_empty_list_excludes_nothing → fd.should_exclude_directory('anything') (line 56)
  utils.code_context.tests.test_file_discovery.test_git_excluded → utils.code_context.tests.test_file_discovery.make_cfg() (line 59)
  utils.code_context.tests.test_file_discovery.test_git_excluded → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 60)
  utils.code_context.tests.test_file_discovery.test_git_excluded → fd.should_exclude_directory('.git') (line 61)
  utils.code_context.tests.test_file_discovery.test_git_excluded → fd.should_exclude_directory('venv') (line 62)
  utils.code_context.tests.test_file_discovery.test_git_excluded → fd.should_exclude_directory('__pycache__') (line 63)
  utils.code_context.tests.test_file_discovery.test_git_excluded → fd.should_exclude_directory('src') (line 64)
  utils.code_context.tests.test_file_discovery.test_word_boundary_match_exact_word → utils.code_context.tests.test_file_discovery.make_cfg() (line 73)
  utils.code_context.tests.test_file_discovery.test_word_boundary_match_exact_word → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 74)
  utils.code_context.tests.test_file_discovery.test_word_boundary_match_exact_word → fd.should_exclude_directory('test') (line 75)
  utils.code_context.tests.test_file_discovery.test_word_boundary_match_prefix → utils.code_context.tests.test_file_discovery.make_cfg() (line 78)
  utils.code_context.tests.test_file_discovery.test_word_boundary_match_prefix → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 79)
  utils.code_context.tests.test_file_discovery.test_word_boundary_match_prefix → fd.should_exclude_directory('test_utils') (line 80)
  utils.code_context.tests.test_file_discovery.test_word_boundary_match_prefix → fd.should_exclude_directory('tests') (line 81)
  utils.code_context.tests.test_file_discovery.test_word_boundary_match_suffix → utils.code_context.tests.test_file_discovery.make_cfg() (line 84)
  utils.code_context.tests.test_file_discovery.test_word_boundary_match_suffix → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 85)
  utils.code_context.tests.test_file_discovery.test_word_boundary_match_suffix → fd.should_exclude_directory('unit_test') (line 86)
  utils.code_context.tests.test_file_discovery.test_word_boundary_does_not_match_mid_word → utils.code_context.tests.test_file_discovery.make_cfg() (line 89)
  utils.code_context.tests.test_file_discovery.test_word_boundary_does_not_match_mid_word → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 90)
  utils.code_context.tests.test_file_discovery.test_word_boundary_does_not_match_mid_word → fd.should_exclude_directory('protest') (line 92)
  utils.code_context.tests.test_file_discovery.test_word_boundary_dot_separator → utils.code_context.tests.test_file_discovery.make_cfg() (line 95)
  utils.code_context.tests.test_file_discovery.test_word_boundary_dot_separator → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 96)
  utils.code_context.tests.test_file_discovery.test_word_boundary_dot_separator → fd.should_exclude_directory('my.temp.dir') (line 97)
  utils.code_context.tests.test_file_discovery.test_word_boundary_dash_separator → utils.code_context.tests.test_file_discovery.make_cfg() (line 100)
  utils.code_context.tests.test_file_discovery.test_word_boundary_dash_separator → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 101)
  utils.code_context.tests.test_file_discovery.test_word_boundary_dash_separator → fd.should_exclude_directory('my-temp-dir') (line 102)
  utils.code_context.tests.test_file_discovery.test_multiple_patterns → utils.code_context.tests.test_file_discovery.make_cfg() (line 105)
  utils.code_context.tests.test_file_discovery.test_multiple_patterns → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 106)
  utils.code_context.tests.test_file_discovery.test_multiple_patterns → fd.should_exclude_directory('temp_files') (line 107)
  utils.code_context.tests.test_file_discovery.test_multiple_patterns → fd.should_exclude_directory('cache_dir') (line 108)
  utils.code_context.tests.test_file_discovery.test_multiple_patterns → fd.should_exclude_directory('src') (line 109)
  utils.code_context.tests.test_file_discovery.test_excludes_exact_filename → utils.code_context.tests.test_file_discovery.make_cfg() (line 118)
  utils.code_context.tests.test_file_discovery.test_excludes_exact_filename → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 119)
  utils.code_context.tests.test_file_discovery.test_excludes_exact_filename → fd.should_exclude_file('debug.log') (line 120)
  utils.code_context.tests.test_file_discovery.test_excludes_exact_filename → fd.should_exclude_file('__init__.py') (line 121)
  utils.code_context.tests.test_file_discovery.test_case_insensitive_filename → utils.code_context.tests.test_file_discovery.make_cfg() (line 124)
  utils.code_context.tests.test_file_discovery.test_case_insensitive_filename → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 125)
  utils.code_context.tests.test_file_discovery.test_case_insensitive_filename → fd.should_exclude_file('readme.md') (line 126)
  utils.code_context.tests.test_file_discovery.test_case_insensitive_filename → fd.should_exclude_file('README.MD') (line 127)
  utils.code_context.tests.test_file_discovery.test_does_not_exclude_different_file → utils.code_context.tests.test_file_discovery.make_cfg() (line 130)
  utils.code_context.tests.test_file_discovery.test_does_not_exclude_different_file → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 131)
  utils.code_context.tests.test_file_discovery.test_does_not_exclude_different_file → fd.should_exclude_file('app.log') (line 132)
  utils.code_context.tests.test_file_discovery.test_does_not_exclude_different_file → fd.should_exclude_file('main.py') (line 133)
  utils.code_context.tests.test_file_discovery.test_word_boundary_match_in_filename → utils.code_context.tests.test_file_discovery.make_cfg() (line 142)
  utils.code_context.tests.test_file_discovery.test_word_boundary_match_in_filename → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 143)
  utils.code_context.tests.test_file_discovery.test_word_boundary_match_in_filename → fd.should_exclude_file('initial.py') (line 144)
  utils.code_context.tests.test_file_discovery.test_word_boundary_match_in_filename → fd.should_exclude_file('initial_setup.py') (line 145)
  utils.code_context.tests.test_file_discovery.test_word_boundary_no_false_positive → utils.code_context.tests.test_file_discovery.make_cfg() (line 148)
  utils.code_context.tests.test_file_discovery.test_word_boundary_no_false_positive → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 149)
  utils.code_context.tests.test_file_discovery.test_word_boundary_no_false_positive → fd.should_exclude_file('init.py') (line 151)
  utils.code_context.tests.test_file_discovery.test_word_boundary_no_false_positive → fd.should_exclude_file('init_db.py') (line 152)
  utils.code_context.tests.test_file_discovery.test_word_boundary_no_false_positive → fd.should_exclude_file('initialize.py') (line 154)
  utils.code_context.tests.test_file_discovery.test_extension_blacklist → utils.code_context.tests.test_file_discovery.make_cfg() (line 163)
  utils.code_context.tests.test_file_discovery.test_extension_blacklist → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 164)
  utils.code_context.tests.test_file_discovery.test_extension_blacklist → fd.should_exclude_file('error.log') (line 165)
  utils.code_context.tests.test_file_discovery.test_extension_blacklist → fd.should_exclude_file('photo.jpg') (line 166)
  utils.code_context.tests.test_file_discovery.test_extension_blacklist → fd.should_exclude_file('app.py') (line 167)
  utils.code_context.tests.test_file_discovery.test_extension_case_insensitive → utils.code_context.tests.test_file_discovery.make_cfg() (line 170)
  utils.code_context.tests.test_file_discovery.test_extension_case_insensitive → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 171)
  utils.code_context.tests.test_file_discovery.test_extension_case_insensitive → fd.should_exclude_file('photo.JPG') (line 172)
  utils.code_context.tests.test_file_discovery.test_extension_case_insensitive → fd.should_exclude_file('photo.Jpg') (line 173)
  utils.code_context.tests.test_file_discovery.test_whitelist_overrides_blacklist → utils.code_context.tests.test_file_discovery.make_cfg() (line 176)
  utils.code_context.tests.test_file_discovery.test_whitelist_overrides_blacklist → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 180)
  utils.code_context.tests.test_file_discovery.test_whitelist_overrides_blacklist → fd.should_exclude_file('app.py') (line 182)
  utils.code_context.tests.test_file_discovery.test_whitelist_overrides_blacklist → fd.should_exclude_file('app.ts') (line 183)
  utils.code_context.tests.test_file_discovery.test_whitelist_overrides_blacklist → fd.should_exclude_file('style.css') (line 184)
  utils.code_context.tests.test_file_discovery.test_whitelist_only_allows_listed_extensions → utils.code_context.tests.test_file_discovery.make_cfg() (line 187)
  utils.code_context.tests.test_file_discovery.test_whitelist_only_allows_listed_extensions → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 188)
  utils.code_context.tests.test_file_discovery.test_whitelist_only_allows_listed_extensions → fd.should_exclude_file('main.py') (line 189)
  utils.code_context.tests.test_file_discovery.test_whitelist_only_allows_listed_extensions → fd.should_exclude_file('component.ts') (line 190)
  utils.code_context.tests.test_file_discovery.test_whitelist_only_allows_listed_extensions → fd.should_exclude_file('image.png') (line 191)
  utils.code_context.tests.test_file_discovery.test_whitelist_only_allows_listed_extensions → fd.should_exclude_file('data.json') (line 192)
  utils.code_context.tests.test_file_discovery.test_no_extension_file_with_blacklist → utils.code_context.tests.test_file_discovery.make_cfg() (line 195)
  utils.code_context.tests.test_file_discovery.test_no_extension_file_with_blacklist → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 196)
  utils.code_context.tests.test_file_discovery.test_no_extension_file_with_blacklist → fd.should_exclude_file('Makefile') (line 198)
  utils.code_context.tests.test_file_discovery.test_no_extension_file_with_blacklist → fd.should_exclude_file('script') (line 199)
  utils.code_context.tests.test_file_discovery.test_discovers_files_in_root → write_text("print('hello')") (line 208)
  utils.code_context.tests.test_file_discovery.test_discovers_files_in_root → write_text('def foo(): pass') (line 209)
  utils.code_context.tests.test_file_discovery.test_discovers_files_in_root → utils.code_context.tests.test_file_discovery.make_cfg() (line 210)
  utils.code_context.tests.test_file_discovery.test_discovers_files_in_root → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 211)
  utils.code_context.tests.test_file_discovery.test_discovers_files_in_root → fd.discover(tmp_path) (line 212)
  utils.code_context.tests.test_file_discovery.test_skips_excluded_directory → excl.mkdir() (line 219)
  utils.code_context.tests.test_file_discovery.test_skips_excluded_directory → write_text('module.exports = {}') (line 220)
  utils.code_context.tests.test_file_discovery.test_skips_excluded_directory → write_text('pass') (line 221)
  utils.code_context.tests.test_file_discovery.test_skips_excluded_directory → utils.code_context.tests.test_file_discovery.make_cfg() (line 222)
  utils.code_context.tests.test_file_discovery.test_skips_excluded_directory → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 223)
  utils.code_context.tests.test_file_discovery.test_skips_excluded_directory → fd.discover(tmp_path) (line 224)
  utils.code_context.tests.test_file_discovery.test_skips_excluded_file → write_text('pass') (line 230)
  utils.code_context.tests.test_file_discovery.test_skips_excluded_file → write_text('') (line 231)
  utils.code_context.tests.test_file_discovery.test_skips_excluded_file → utils.code_context.tests.test_file_discovery.make_cfg() (line 232)
  utils.code_context.tests.test_file_discovery.test_skips_excluded_file → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 233)
  utils.code_context.tests.test_file_discovery.test_skips_excluded_file → fd.discover(tmp_path) (line 234)
  utils.code_context.tests.test_file_discovery.test_subdirectory_restricts_scan → src.mkdir() (line 241)
  utils.code_context.tests.test_file_discovery.test_subdirectory_restricts_scan → write_text('pass') (line 242)
  utils.code_context.tests.test_file_discovery.test_subdirectory_restricts_scan → write_text('pass') (line 243)
  utils.code_context.tests.test_file_discovery.test_subdirectory_restricts_scan → utils.code_context.tests.test_file_discovery.make_cfg() (line 244)
  utils.code_context.tests.test_file_discovery.test_subdirectory_restricts_scan → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 245)
  utils.code_context.tests.test_file_discovery.test_subdirectory_restricts_scan → fd.discover(tmp_path) (line 246)
  utils.code_context.tests.test_file_discovery.test_additional_files_injected → write_text('pass') (line 252)
  utils.code_context.tests.test_file_discovery.test_additional_files_injected → ...mkdir() (line 254)
  utils.code_context.tests.test_file_discovery.test_additional_files_injected → extra.write_text('pass') (line 255)
  utils.code_context.tests.test_file_discovery.test_additional_files_injected → utils.code_context.tests.test_file_discovery.make_cfg() (line 256)
  utils.code_context.tests.test_file_discovery.test_additional_files_injected → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 257)
  utils.code_context.tests.test_file_discovery.test_additional_files_injected → fd.discover(tmp_path) (line 258)
  utils.code_context.tests.test_file_discovery.test_nonexistent_root_returns_empty → utils.code_context.tests.test_file_discovery.make_cfg() (line 264)
  utils.code_context.tests.test_file_discovery.test_nonexistent_root_returns_empty → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 265)
  utils.code_context.tests.test_file_discovery.test_nonexistent_root_returns_empty → fd.discover(tmp_path / 'does_not_exist') (line 266)
  utils.code_context.tests.test_file_discovery.test_analyze_returns_correct_stats → write_text('pass') (line 270)
  utils.code_context.tests.test_file_discovery.test_analyze_returns_correct_stats → write_text('pass') (line 271)
  utils.code_context.tests.test_file_discovery.test_analyze_returns_correct_stats → sub.mkdir() (line 273)
  utils.code_context.tests.test_file_discovery.test_analyze_returns_correct_stats → write_text('const x = 1;') (line 274)
  utils.code_context.tests.test_file_discovery.test_analyze_returns_correct_stats → utils.code_context.tests.test_file_discovery.make_cfg() (line 275)
  utils.code_context.tests.test_file_discovery.test_analyze_returns_correct_stats → utils.code_context.tests.test_file_discovery.FileDiscovery(cfg) (line 276)
  utils.code_context.tests.test_file_discovery.test_analyze_returns_correct_stats → fd.discover(tmp_path) (line 277)
  utils.code_context.tests.test_file_discovery.test_analyze_returns_correct_stats → fd.analyze(files) (line 278)
  utils.code_context.tests.test_file_discovery.test_add_exclude_directory → CodeContextConfig.from_yaml() (line 291)
  utils.code_context.tests.test_file_discovery.test_remove_exclude_directory → CodeContextConfig.from_yaml() (line 297)
  utils.code_context.tests.test_file_discovery.test_add_include_extension → CodeContextConfig.from_yaml() (line 303)
  utils.code_context.tests.test_file_discovery.test_no_duplicate_on_repeated_add → CodeContextConfig.from_yaml() (line 310)
  utils.code_context.tests.test_file_discovery.test_no_duplicate_on_repeated_add → ...count('.git') (line 313)
  utils.code_context.tests.test_file_discovery.test_remove_nonexistent_is_safe → CodeContextConfig.from_yaml() (line 316)
# Call graph: utils.code_context.tests.test_output_modes
  Global Scope → ...insert(0, str(Path(__file__).parent.parent.parent.parent)) (line 19)
  Global Scope → utils.code_context.tests.test_output_modes.Path(__file__) (line 19)
  utils.code_context.tests.test_output_modes.make_extractor → utils.code_context.tests.test_output_modes.SignatureExtractor() (line 34)
  utils.code_context.tests.test_output_modes.extract → p.write_text(content) (line 39)
  utils.code_context.tests.test_output_modes.extract → extract(p) (line 40)
  utils.code_context.tests.test_output_modes.extract → utils.code_context.tests.test_output_modes.make_extractor() (line 40)
  utils.code_context.tests.test_output_modes.real_project → root.mkdir() (line 51)
  utils.code_context.tests.test_output_modes.real_project → write_text('"""Module docstring."""\n\n# Section comment\nclass Alpha:\n    """Class docstring."""\n    def run(self, x: int, y: int = 0) -> int:\n        """Run it."""\n        return x + y\n\ndef helper(name: str) -> str:\n    """Help."""\n    return name.upper()\n') (line 52)
  utils.code_context.tests.test_output_modes.real_project → write_text('class Beta:\n    def __init__(self, val):\n        self.val = val\n\n    def compute(self):\n        return self.val * 2\n') (line 65)
  utils.code_context.tests.test_output_modes.real_project → pytest.fixture() (line 48)
  utils.code_context.tests.test_output_modes.test_tree_only_smallest → utils.code_context.tests.test_output_modes.CodeContextBuilder() (line 76)
  utils.code_context.tests.test_output_modes.test_tree_only_smallest → utils.code_context.tests.test_output_modes.CodeContextBuilder() (line 77)
  utils.code_context.tests.test_output_modes.test_tree_only_smallest → tree_builder.build() (line 78)
  utils.code_context.tests.test_output_modes.test_tree_only_smallest → sig_builder.build() (line 78)
  utils.code_context.tests.test_output_modes.test_signatures_smaller_than_clean → utils.code_context.tests.test_output_modes.CodeContextBuilder() (line 81)
  utils.code_context.tests.test_output_modes.test_signatures_smaller_than_clean → utils.code_context.tests.test_output_modes.CodeContextBuilder() (line 82)
  utils.code_context.tests.test_output_modes.test_signatures_smaller_than_clean → sig_builder.build() (line 83)
  utils.code_context.tests.test_output_modes.test_signatures_smaller_than_clean → clean_builder.build() (line 83)
  utils.code_context.tests.test_output_modes.test_clean_smaller_than_original → utils.code_context.tests.test_output_modes.CodeContextBuilder() (line 86)
  utils.code_context.tests.test_output_modes.test_clean_smaller_than_original → utils.code_context.tests.test_output_modes.CodeContextBuilder() (line 87)
  utils.code_context.tests.test_output_modes.test_clean_smaller_than_original → clean_builder.build() (line 88)
  utils.code_context.tests.test_output_modes.test_clean_smaller_than_original → orig_builder.build() (line 88)
  utils.code_context.tests.test_output_modes.test_all_modes_contain_tree → build() (line 92)
  utils.code_context.tests.test_output_modes.test_all_modes_contain_tree → utils.code_context.tests.test_output_modes.CodeContextBuilder() (line 92)
  utils.code_context.tests.test_output_modes.test_all_modes_contain_header → build() (line 97)
  utils.code_context.tests.test_output_modes.test_all_modes_contain_header → utils.code_context.tests.test_output_modes.CodeContextBuilder() (line 97)
  utils.code_context.tests.test_output_modes.test_top_level_function → utils.code_context.tests.test_output_modes.extract(tmp_path, 'mod.py', 'def greet(name: str) -> str:\n    return name\n') (line 108)
  utils.code_context.tests.test_output_modes.test_class_with_methods → utils.code_context.tests.test_output_modes.extract(tmp_path, 'mod.py', 'class Foo:\n    def __init__(self, x):\n        self.x = x\n    def run(self):\n        pass\n') (line 112)
  utils.code_context.tests.test_output_modes.test_function_body_absent → utils.code_context.tests.test_output_modes.extract(tmp_path, 'mod.py', 'def compute(x, y):\n    return x * y + 100\n') (line 124)
  utils.code_context.tests.test_output_modes.test_async_function → utils.code_context.tests.test_output_modes.extract(tmp_path, 'mod.py', 'async def fetch(url: str) -> str:\n    return url\n') (line 130)
  utils.code_context.tests.test_output_modes.test_type_annotations_in_signature → utils.code_context.tests.test_output_modes.extract(tmp_path, 'mod.py', 'def process(items: list[str], limit: int = 10) -> dict:\n    pass\n') (line 136)
  utils.code_context.tests.test_output_modes.test_star_args → utils.code_context.tests.test_output_modes.extract(tmp_path, 'mod.py', 'def func(*args, **kwargs):\n    pass\n') (line 143)
  utils.code_context.tests.test_output_modes.test_base_class_in_signature → utils.code_context.tests.test_output_modes.extract(tmp_path, 'mod.py', 'class Child(Base):\n    def run(self): pass\n') (line 151)
  utils.code_context.tests.test_output_modes.test_syntax_error_returns_graceful_note → utils.code_context.tests.test_output_modes.extract(tmp_path, 'bad.py', 'def oops(\n    missing\n') (line 157)
  utils.code_context.tests.test_output_modes.test_empty_file_no_signatures_no_error → utils.code_context.tests.test_output_modes.extract(tmp_path, 'empty.py', '') (line 162)
  utils.code_context.tests.test_output_modes.test_language_tagged_as_python → utils.code_context.tests.test_output_modes.extract(tmp_path, 'app.py', 'x = 1\n') (line 168)
  utils.code_context.tests.test_output_modes.test_exported_function → utils.code_context.tests.test_output_modes.extract(tmp_path, 'api.ts', 'export async function fetchUser(id: string): Promise<User> {\n    return db.find(id);\n}\n') (line 178)
  utils.code_context.tests.test_output_modes.test_class_declaration → utils.code_context.tests.test_output_modes.extract(tmp_path, 'service.ts', 'export class UserService {\n    constructor(private db: DB) {}\n    async getUser(id: string): Promise<User> { return this.db.find(id); }\n}\n') (line 186)
  utils.code_context.tests.test_output_modes.test_interface_declaration → utils.code_context.tests.test_output_modes.extract(tmp_path, 'types.ts', 'export interface ApiResponse<T> {\n    data: T;\n    error: string | null;\n}\n') (line 195)
  utils.code_context.tests.test_output_modes.test_arrow_function_const → utils.code_context.tests.test_output_modes.extract(tmp_path, 'utils.ts', 'export const transform = async (input: string): Promise<string> => {\n    return input.trim();\n};\n') (line 204)
  utils.code_context.tests.test_output_modes.test_function_body_absent → utils.code_context.tests.test_output_modes.extract(tmp_path, 'app.ts', 'function add(a: number, b: number): number {\n    return a + b + 99999;\n}\n') (line 212)
  utils.code_context.tests.test_output_modes.test_language_tagged_as_typescript → utils.code_context.tests.test_output_modes.extract(tmp_path, 'app.ts', 'const x = 1;\n') (line 220)
  utils.code_context.tests.test_output_modes.test_tsx_tagged_as_typescript → utils.code_context.tests.test_output_modes.extract(tmp_path, 'Component.tsx', 'export function Button() { return null; }\n') (line 224)
  utils.code_context.tests.test_output_modes.test_js_function → utils.code_context.tests.test_output_modes.extract(tmp_path, 'lib.js', "function greet(name) {\n    return 'Hello ' + name;\n}\n") (line 228)
  utils.code_context.tests.test_output_modes.test_func_declaration → utils.code_context.tests.test_output_modes.extract(tmp_path, 'main.go', 'func Add(a, b int) int {\n    return a + b\n}\n') (line 243)
  utils.code_context.tests.test_output_modes.test_method_declaration → utils.code_context.tests.test_output_modes.extract(tmp_path, 'service.go', 'func (s *Service) Run(ctx context.Context) error {\n    return nil\n}\n') (line 250)
  utils.code_context.tests.test_output_modes.test_struct_type → utils.code_context.tests.test_output_modes.extract(tmp_path, 'types.go', 'type Config struct {\n    Host string\n    Port int\n}\n') (line 256)
  utils.code_context.tests.test_output_modes.test_interface_type → utils.code_context.tests.test_output_modes.extract(tmp_path, 'iface.go', 'type Handler interface {\n    Handle(r Request) Response\n}\n') (line 262)
  utils.code_context.tests.test_output_modes.test_pub_fn → utils.code_context.tests.test_output_modes.extract(tmp_path, 'lib.rs', 'pub fn compute(x: u32, y: u32) -> u32 {\n    x + y\n}\n') (line 274)
  utils.code_context.tests.test_output_modes.test_struct_declaration → utils.code_context.tests.test_output_modes.extract(tmp_path, 'model.rs', 'pub struct Config {\n    pub host: String,\n}\n') (line 281)
  utils.code_context.tests.test_output_modes.test_impl_block → utils.code_context.tests.test_output_modes.extract(tmp_path, 'service.rs', 'impl Service {\n    pub fn new() -> Self { Service {} }\n}\n') (line 287)
  utils.code_context.tests.test_output_modes.test_trait_declaration → utils.code_context.tests.test_output_modes.extract(tmp_path, 'traits.rs', 'pub trait Runnable {\n    fn run(&self);\n}\n') (line 293)
  utils.code_context.tests.test_output_modes.test_class_declaration → utils.code_context.tests.test_output_modes.extract(tmp_path, 'App.java', 'public class App {\n    public static void main(String[] args) {\n        System.out.println("hello");\n    }\n}\n') (line 305)
  utils.code_context.tests.test_output_modes.test_interface_declaration → utils.code_context.tests.test_output_modes.extract(tmp_path, 'Handler.java', 'public interface Handler {\n    void handle(Request req);\n}\n') (line 316)
  utils.code_context.tests.test_output_modes.test_ruby_method → utils.code_context.tests.test_output_modes.extract(tmp_path, 'app.rb', 'class MyClass\n  def initialize(name)\n    @name = name\n  end\nend\n') (line 330)
  utils.code_context.tests.test_output_modes.test_php_function → utils.code_context.tests.test_output_modes.extract(tmp_path, 'app.php', "<?php\nfunction greet(string $name): string {\n    return 'Hello ' . $name;\n}\n") (line 341)
  utils.code_context.tests.test_output_modes.test_lua_function → utils.code_context.tests.test_output_modes.extract(tmp_path, 'mod.lua', "function greet(name)\n    return 'Hello ' .. name\nend\n") (line 351)
  utils.code_context.tests.test_output_modes.test_kotlin_class → utils.code_context.tests.test_output_modes.extract(tmp_path, 'App.kt', 'data class User(val name: String, val age: Int)\nfun main() {\n    println("Hello")\n}\n') (line 360)
  utils.code_context.tests.test_output_modes.test_swift_function → utils.code_context.tests.test_output_modes.extract(tmp_path, 'app.swift', 'func greet(name: String) -> String {\n    return "Hello \\(name)"\n}\n') (line 370)
  utils.code_context.tests.test_output_modes.test_dart_class → utils.code_context.tests.test_output_modes.extract(tmp_path, 'app.dart', 'class MyWidget extends StatelessWidget {\n  final String title;\n  MyWidget({required this.title});\n}\n') (line 379)
  utils.code_context.tests.test_output_modes.test_unknown_extension_returns_note → utils.code_context.tests.test_output_modes.extract(tmp_path, 'app.brainfuck', '++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.') (line 395)
  utils.code_context.tests.test_output_modes.test_unknown_extension_returns_note → ...lower() (line 397)
  utils.code_context.tests.test_output_modes.test_unknown_extension_no_crash → utils.code_context.tests.test_output_modes.extract(tmp_path, 'data.xyz', 'some content here') (line 400)
  utils.code_context.tests.test_output_modes.test_no_extension_graceful → utils.code_context.tests.test_output_modes.extract(tmp_path, 'Makefile', 'all:\n\t$(CC) -o main main.c\n') (line 404)
  utils.code_context.tests.test_output_modes.test_to_text_contains_filepath → utils.code_context.tests.test_output_modes.extract(tmp_path, 'mod.py', 'def foo(): pass\n') (line 414)
  utils.code_context.tests.test_output_modes.test_to_text_contains_filepath → sb.to_text() (line 415)
  utils.code_context.tests.test_output_modes.test_to_text_contains_language_tag → utils.code_context.tests.test_output_modes.extract(tmp_path, 'mod.py', 'def foo(): pass\n') (line 419)
  utils.code_context.tests.test_output_modes.test_to_text_contains_language_tag → sb.to_text() (line 420)
  utils.code_context.tests.test_output_modes.test_to_text_uses_relative_path → sub.mkdir() (line 425)
  utils.code_context.tests.test_output_modes.test_to_text_uses_relative_path → p.write_text('def foo(): pass\n') (line 427)
  utils.code_context.tests.test_output_modes.test_to_text_uses_relative_path → extract(p) (line 428)
  utils.code_context.tests.test_output_modes.test_to_text_uses_relative_path → utils.code_context.tests.test_output_modes.make_extractor() (line 428)
  utils.code_context.tests.test_output_modes.test_to_text_uses_relative_path → sb.to_text() (line 429)
  utils.code_context.tests.test_output_modes.test_to_text_indents_signatures → utils.code_context.tests.test_output_modes.extract(tmp_path, 'mod.py', 'class Foo:\n    def bar(self): pass\n') (line 434)
  utils.code_context.tests.test_output_modes.test_to_text_indents_signatures → sb.to_text() (line 437)
  utils.code_context.tests.test_output_modes.test_to_text_indents_signatures → text.splitlines() (line 438)
  utils.code_context.tests.test_output_modes.test_to_text_note_shown_for_unsupported → utils.code_context.tests.test_output_modes.extract(tmp_path, 'app.unknown_xyz', 'code here') (line 442)
  utils.code_context.tests.test_output_modes.test_to_text_note_shown_for_unsupported → sb.to_text() (line 443)
  utils.code_context.tests.test_output_modes.test_batch_extraction → p.write_text(content) (line 460)
  utils.code_context.tests.test_output_modes.test_batch_extraction → files.append(p) (line 461)
  utils.code_context.tests.test_output_modes.test_batch_extraction → extract_files(files) (line 462)
  utils.code_context.tests.test_output_modes.test_batch_extraction → utils.code_context.tests.test_output_modes.make_extractor() (line 462)
  utils.code_context.tests.test_output_modes.test_batch_no_crash_on_mixed_supported_unsupported → p.write_text(content) (line 476)
  utils.code_context.tests.test_output_modes.test_batch_no_crash_on_mixed_supported_unsupported → files.append(p) (line 477)
  utils.code_context.tests.test_output_modes.test_batch_no_crash_on_mixed_supported_unsupported → extract_files(files) (line 478)
  utils.code_context.tests.test_output_modes.test_batch_no_crash_on_mixed_supported_unsupported → utils.code_context.tests.test_output_modes.make_extractor() (line 478)
```
<!-- /AUTO:call_graph -->

<!-- AUTO:callers -->
## Upstream Callers

> Auto-discovered by scanning all project files that import from this module.
> Set `ENTRY_POINTS` in `generate_readme.py` to pin specific functions.

| Caller | Calls |
|--------|-------|
| `ai/tools/implementations/code.py` | `CodeContextBuilder()` |
| `mcp_server/tools/code/fetch.py` | `CodeContextBuilder()` |
| `utils/local_dev_utils/extract_code.py` | `CodeContextBuilder()` |
| `utils/local_dev_utils/next_test_dir_config.py` | `CodeContextBuilder()` |
| `utils/local_dev_utils/react_links_direct.py` | `CodeContextBuilder()` |
| `utils/react_analysis/get_and_analyze.py` | `CodeContextBuilder()` |
| `utils/local_dev_utils/generate_readme.py` | `run_cascade()` |
<!-- /AUTO:callers -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "utils/code_context",
  "mode": "signatures",
  "scope": null,
  "project_noise": null,
  "include_call_graph": false,
  "entry_points": null,
  "call_graph_exclude": [
    "tests"
  ]
}
```
<!-- /AUTO:config -->

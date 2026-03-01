# AST Upgrades — Completed

All five upgrades from the original task have been implemented in
`utils/code_context/code_context.py`. This file is kept as a record.

---

## Completed Items

### 1. Default ignore list + project noise config ✓
- Added `_DEFAULT_CALL_GRAPH_IGNORE` constant covering all Python builtins,
  common exception types, and stdlib noise (`defaultdict`, `uuid4`, `Field`).
- Added `call_graph_project_noise` field to `CodeContextConfig` and the
  corresponding key to `config.yaml` (pre-populated with `vcprint`, `clear_terminal`).
- `CodeContextBuilder.build()` merges defaults + project noise + caller-supplied ignore.

### 2. Method call visibility (`ast.Attribute`) ✓
- `_CallVisitor.visit_Call` now handles `ast.Attribute` nodes (method calls).
- `FunctionCallAnalyzer` accepts `include_method_calls=True` (default) and
  `include_private_methods=False` (default).
- `CodeContextBuilder` exposes `call_graph_include_methods` and
  `call_graph_include_private` params.
- Receiver name recovered where possible (`self.registry.get()` → `...registry.get()`).

### 3. `is_async` field on `FunctionCallInfo` ✓
- `FunctionCallInfo` has `is_async: bool = False`.
- `_CallVisitor` tracks whether the enclosing function is async and stamps each call.
- `FunctionCallGraph.to_text()` prefixes async callers with `async `.

### 4. Pydantic field extraction in signatures ✓
- `SignatureExtractor._extract_python` detects classes inheriting from `BaseModel`.
- Emits a compact `# fields: name1, name2, ...` comment line immediately after
  the class declaration.
- Uses `ast.AnnAssign` nodes; skips private fields.

### 5. Scope filter for `FunctionCallAnalyzer` ✓
- `FunctionCallAnalyzer.analyze_files()` accepts optional `scope: list[str]`.
- When set, only files whose stem matches are analyzed.
- `CodeContextBuilder` exposes `call_graph_scope: list[str] | None`.

---

## Bonus fix
- Fixed pre-existing bug: `FileNode` population used `s.signature` on `list[str]`
  items; corrected to `list(sb.signatures)`.

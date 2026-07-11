# Language Coverage

This document describes what `code_context.py` can do for each language in **signatures mode**.

All four modes (`tree_only`, `signatures`, `clean`, `original`) work for every file type — only
**signatures mode** has per-language differences.

---

## Comment stripping (`clean` mode)

Comment stripping works well for the following families:

| Pattern | Languages |
|---|---|
| `#` single-line | Python, Ruby, Shell, Perl, R, YAML, Makefile |
| `// ` single-line | JS, TS, Go, Rust, Java, Kotlin, Swift, C, C++, C#, PHP, Dart, Scala |
| `/* ... */` block | JS, TS, Go, Rust, Java, Kotlin, Swift, C, C++, C#, PHP, Dart, Scala |
| `''' ... '''` / `""" ... """` | Python |
| `<!-- ... -->` | HTML, XML, JSX, TSX |
| `-- comment` / `--[[ ... ]]` | Lua |

---

## Signatures mode — extraction quality

### Full support (AST or well-tested regex)

| Language | Extensions | Method | Quality |
|---|---|---|---|
| **Python** | `.py` | stdlib `ast` module | Excellent — exact signatures with type annotations, defaults, `*args`, `**kwargs`, return types |
| **TypeScript** | `.ts`, `.tsx` | regex | Good — classes, interfaces, enums, exported functions, arrow function consts, method signatures |
| **JavaScript** | `.js`, `.jsx`, `.mjs` | regex | Good — classes, functions, arrow function consts, methods |
| **Go** | `.go` | regex | Good — `func` declarations including receiver methods, `struct`/`interface`/`type` declarations |
| **Rust** | `.rs` | regex | Good — `fn`, `struct`, `enum`, `trait`, `impl` blocks |
| **Java** | `.java` | regex | Good — class/interface/enum/record declarations, method signatures |
| **Kotlin** | `.kt`, `.kts` | regex | Good — `fun`, `class`, `interface`, `object`, `data class`, `sealed class` |
| **Swift** | `.swift` | regex | Good — `func`, `class`, `struct`, `protocol`, `enum`, `extension` |
| **C** | `.c`, `.h` | regex | Good — function declarations, `struct`/`union`/`enum`/`typedef` |
| **C++** | `.cpp`, `.cc`, `.cxx`, `.hpp` | regex | Good — function/method declarations, `class`/`struct`/`namespace` |
| **C#** | `.cs` | regex | Good — method signatures, `class`/`interface`/`struct`/`enum`/`record` |
| **Ruby** | `.rb` | regex | Good — `def`/`def self.`, `class`/`module` |
| **PHP** | `.php` | regex | Good — `function`, `class`/`interface`/`trait`/`enum` |
| **Lua** | `.lua` | regex | Good — `function`, method-style assignments |
| **Scala** | `.scala` | regex | Good — `def`/`val`/`var`/`class`/`object`/`trait`/`case class` |
| **Dart** | `.dart` | regex | Good — `class`, method/function declarations |

### Partial support (generic fallback — tree + file listed, no signatures extracted)

These languages are recognised by extension but have no regex patterns defined.
The file still appears in the output with a note directing here.

| Language | Extensions | Status |
|---|---|---|
| **R** | `.r` | No patterns — R function syntax (`foo <- function(...)`) not yet implemented |
| **Elixir** | `.ex`, `.exs` | No patterns — `def`/`defmodule` regex not yet implemented |
| **Haskell** | `.hs` | No patterns — complex type signature syntax not yet implemented |
| **Erlang** | `.erl` | No patterns — `function/arity` syntax not yet implemented |

### Not recognised (completely unknown extension)

Any file with an extension not in the language map will show:

```
# <path>  [unknown (.xyz)]
  # signature extraction not supported for this language; see LANGUAGE_COVERAGE.md
```

The file is still counted in the tree and stats. Only signatures are missing.

---

## Known limitations

### TypeScript / JavaScript
- **Generic type parameters** in method signatures may be partially captured when they contain
  nested `<>` (e.g. `Map<string, Array<User>>`). The signature line is still extracted but may
  be truncated at a closing `>`.
- **Decorators** (`@Injectable()`, `@Component()`) are not extracted as standalone entries.
  The decorated class/function signature itself is still captured.
- **Overloaded function signatures** — only the implementation signature is captured, not
  the overload declarations.

### C / C++
- **Preprocessor macros** that expand to function-like constructs are not captured.
- **Templates** with complex constraints (`requires`, `concept`) may have truncated signatures.
- Header-only inline functions with complex return types may produce noisy output.

### Java
- **Annotations** on methods (e.g. `@Override`, `@Bean`) are not captured as part of the
  signature line.
- **Nested classes** are captured but their indentation context is not preserved.

### Regex-based languages (general)
- All non-Python extraction is best-effort regex. It works well on clean, standard-style code
  but may miss or partially capture:
  - Unusual formatting (everything on one line, unconventional spacing)
  - Heavily macro-expanded code
  - Minified source

### Python
- Python extraction uses the stdlib `ast` module and is highly reliable for valid Python 3.x.
- **Type annotations with forward references** (string literals) are preserved as-is.
- Files with syntax errors produce a graceful note instead of crashing.

---

## Adding a new language

To add signature extraction for a new language:

1. Add the extension → language mapping in `_LANG_MAP` in `code_context.py`.
2. Add the language to `_SUPPORTED_LANGS`.
3. Add one or more `re.compile(...)` patterns to `_SIG_PATTERNS[language]`.
4. Add tests in `tests/test_output_modes.py` following the existing pattern.

Regex tips:
- Use `re.MULTILINE` so `^` anchors to line starts.
- Match the full declaration line up to (but not including) the opening `{` or `:`.
- Capture enough context to be unambiguous (access modifiers, keywords, name, params).
- Use `[^{;]*` or similar to stop before the body.

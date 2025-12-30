# matrx-utils

A comprehensive collection of Python utilities designed to complement the AI Matrx platform.

## Overview

matrx-utils provides a curated set of utility functions and tools that enhance the AI Matrx ecosystem. This repository serves as a centralized library of commonly used functionality, allowing for easy integration across the main AI Matrx application and related projects.

## Features

- **Logging utilities** - Enhanced logging capabilities
- **Print utilities** - Advanced printing and formatting tools
- **Code analysis** - Tools for analyzing and processing code
- **Markdown processing** - Utilities for working with markdown content
- **Object manipulation** - Helper functions for working with Python objects
- **Data conversion** - Tools for converting between different data formats
- **Additional utilities** - Various other Python utility-level tools

## Purpose

This library is designed to provide instant access to a powerful set of utilities without requiring additional code setup. All utilities have been customized and configured specifically for the AI Matrx platform ecosystem.

## Installation

### From PyPI (recommended)

```bash
pip install matrx-utils
# or with uv
uv add matrx-utils
```

### From GitHub (for development)

```bash
pip install git+https://github.com/armanisadeghi/matrx-utils.git
```

## Quick Start

```python
import matrx_utils

# Example usage will be added as the library develops
```

## Contributing

This project is part of the AI Matrx ecosystem. Contributions and suggestions are welcome.

## License

[License information to be added]

## Related Projects

- [AI Matrx](https://github.com/armanisadeghi/ai-matrx) - Main AI Matrx platform repository


## Publishing a New Version

### Automated PyPI Publishing (Current Process)

The package automatically publishes to PyPI when you push a version tag. Here's the workflow:

1. **Make and test your changes locally**
   ```bash
   # Test your changes
   ```

2. **Update the version in pyproject.toml**
   ```toml
   version = "1.0.3"  # Increment appropriately
   ```

3. **Commit and push changes**
   ```bash
   git add .
   git commit -m "Add new feature - v1.0.3"
   git push origin main
   ```

4. **Create and push the version tag**
   ```bash
   git tag v1.0.3
   git push origin v1.0.3
   ```

5. **GitHub Actions automatically:**
   - Verifies the tag matches pyproject.toml version
   - Builds the package
   - Publishes to PyPI

6. **Update dependent projects**
   
   In projects like AI Dream, simply update the version:
   ```bash
   uv add matrx-utils@1.0.3
   # or manually in pyproject.toml:
   # matrx-utils = "^1.0.3"
   ```

### Version History

Check current tags: `git tag`

Example output:
```
v1.0.0
v1.0.1
v1.0.2
```

### Important Notes

- **Always update pyproject.toml version before tagging**
- The GitHub Action will fail if tag version ≠ pyproject.toml version
- Semantic versioning: MAJOR.MINOR.PATCH (e.g., v1.0.3)
- Tags trigger automatic PyPI publishing
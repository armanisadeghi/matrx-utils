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


## Updating to a new version

1. Make local updates, test them and confirm they are good.
    - Check current tags: git tag
    - Identify the next tag to be used
2. commit and Push all updates
    - git commit -m "update some feature - v1.0.2"
    - git push origin main
3. Tag the commit:
    - git tag v1.0.2
    - git push origin v1.0.2
4. Confirm tags are properly updates:
    - git tag
    - Example:
        v1.0.0
        v1.0.2
5. Make updates to apps that need the updated version:
    - AI Dream pyproject.toml Example: 
    - Before: matrx-utils = { git = "https://github.com/armanisadeghi/matrx-utils", rev = "v1.0.0" }
    - After: matrx-utils = { git = "https://github.com/armanisadeghi/matrx-utils", rev = "v1.0.2" }
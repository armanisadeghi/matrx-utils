# MATRX Utils

A collection of utility functions and tools for data handling and database operations.

## Features

- Data Transformation and Handling
- Database Operations and Management
- Common Utility Functions
- File Management
- Cloud Provider Integration
- Socket Operations

## Installation

```bash
pip install matrx-utils
```

## Quick Start

```python
from matrx_utils import DataTransformer, FileManager

# Use the DataTransformer
transformer = DataTransformer()
# Transform your data...

# Use the FileManager
file_manager = FileManager()
# Manage your files...
```

## Documentation

### Data Handling

The `data_handling` module provides tools for transforming and processing data:

```python
from matrx_utils.data_handling import DataTransformer

transformer = DataTransformer()
# Use transformer methods...
```

### Common Utilities

The `common` module provides various utility functions:

```python
from matrx_utils.common import vcprint, FileManager

# Use fancy printing
vcprint("Hello, World!")

# Use file management
file_manager = FileManager()
```

### Database Operations

The `database` module provides database management capabilities:

```python
from matrx_utils.database import manager

# Use database manager...
```

## Requirements

- Python 3.11 or higher
- See `setup.py` for full list of dependencies

## License

This project is licensed under the MIT License - see the LICENSE file for details.

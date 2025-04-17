matrx_orm/
│
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── base.py
│   ├── fields.py
│   └── relations.py
│
├── operations/
│   ├── __init__.py
│   ├── create.py
│   ├── read.py
│   ├── update.py
│   └── delete.py
│
├── query/
│   ├── __init__.py
│   ├── builder.py
│   └── executor.py
│
├── adapters/
│   ├── __init__.py
│   ├── local.py
│   └── supabase.py
│
├── utils/
│   ├── __init__.py
│   ├── connection_pool.py
│   └── type_converters.py
│
└── migrations/
    ├── __init__.py
    └── manager.py


# Wow: https://claude.ai/chat/77ce9cf0-bb8e-4608-8820-1ca253fe2680

orm/
│
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── base.py
│   ├── fields.py
│   ├── relations.py
│   ├── validation.py
│   └── signals.py
│
├── operations/
│   ├── __init__.py
│   ├── create.py
│   ├── read.py
│   ├── update.py
│   └── delete.py
│
├── query/
│   ├── __init__.py
│   ├── builder.py
│   ├── executor.py
│   └── optimizations.py
│
├── adapters/
│   ├── __init__.py
│   ├── base.py
│   ├── postgresql.py
│   └── supabase.py
│
├── utils/
│   ├── __init__.py
│   ├── connection_pool.py
│   ├── type_converters.py
│   ├── cache.py
│   └── logging.py
│
├── migrations/
│   ├── __init__.py
│   └── manager.py
│
├── cli/
│   ├── __init__.py
│   └── commands.py
│
├── middleware/
│   ├── __init__.py
│   └── base.py
│
├── exceptions.py
├── transactions.py
│
├── tests/
│   ├── __init__.py
│   ├── test_core/
│   ├── test_operations/
│   ├── test_query/
│   ├── test_adapters/
│   └── test_migrations/
│
├── docs/
│   ├── getting_started.md
│   ├── api_reference.md
│   ├── migration_guide.md
│   └── advanced_usage.md
│
└── examples/
    ├── basic_crud/
    ├── complex_queries/
    └── multi_table_operations/

# Repository reminders

- Run the full test suite with `make test` (or `python scripts/run_tests_parallel.py tests/`). It shards pytest across worker processes and is much faster than running `pytest` directly.
- Use direct `pytest` invocations for focused test files or cases only.

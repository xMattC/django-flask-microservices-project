### Testing Structure

Service-specific tests are located within each service directory and validate isolated application behaviour.

The root `tests/` directory contains platform-level tests, including:

- `smoke/smoke-tests.sh` pre deployment verification
- `System/test_system_e2e.py` workflow tests spanning multiple services

See: [Testing Documentation](../docs/testing.md)

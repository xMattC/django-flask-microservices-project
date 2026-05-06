## Service Setup

- Setup service (Flask/FastAPI + Docker)
- Add DB (if needed)
- Add wait-for-db
- Add health endpoints
- Add logging
- Add base error handling
- Add OpenAPI/Swagger setup
- Add CI
- Add README

## Domain Implementation

- Implement core endpoints
- Add manual validation for first pass
- Add basic API docs
- Add request schemas
- Add response schemas
- Replace manual validation with schema validation where appropriate
- Add service layer
- Add tests (unit + API)

## Integration

- Add user context handling (`X-User-ID`)
- Add shared auth/user-context helper
- Document required integration headers
- Add integration tests (web → service)
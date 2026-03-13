<!-- TOC START -->

- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
  - [RESTful URL Design](#restful-url-design)
  - [HTTP Status Codes](#http-status-codes)
  - [SQL Injection Prevention](#sql-injection-prevention)
  - [N+1 Query Prevention](#n1-query-prevention)
  - [Indexing Strategy](#indexing-strategy)
  - [Transactions](#transactions)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

---

name: backend-api-patterns
description: REST API design and database query patterns — endpoint design, status codes, SQL injection prevention, N+1 prevention, indexing, transactions. Use when building or optimizing API endpoints or database queries.

---

# Backend API & Query Patterns

**Reviewed**: 2026-02-17 | **Scope**: Disabled skill revival — consolidates 2 disabled skills

## Scope

- API endpoints in `flext-auth/`, `cmd/flext-control-panel/`
- Database query patterns across FLEXT subprojects
- Data access layers and repository patterns

## References

- `AGENTS.md` — canonical governance source
- <https://restfulapi.net/>
- `.claude/skills/lib-pydantic-v2/SKILL.md` — request/response validation
- `.claude/skills/flext-patterns/SKILL.md` — r for API responses

## Rules

- Use resource-based URLs: `/users/{id}`, not `/getUser`.
- Return appropriate HTTP status codes (201 for creation, 404 for not found, 422 for validation).
- Always use parameterized queries — never string interpolation for SQL.
- Prevent N+1 queries with eager loading (`selectinload`, `joinedload`).
- Add database indexes for columns used in WHERE, JOIN, and ORDER BY clauses.

## Instructions

### RESTful URL Design

```
GET    /api/v1/users          # list
POST   /api/v1/users          # create
GET    /api/v1/users/{id}     # read
PUT    /api/v1/users/{id}     # replace
PATCH  /api/v1/users/{id}     # partial update
DELETE /api/v1/users/{id}     # delete
```

### HTTP Status Codes

| Code | Meaning           | Use For                              |
| ---- | ----------------- | ------------------------------------ |
| 200  | OK                | Successful GET/PUT/PATCH             |
| 201  | Created           | Successful POST                      |
| 204  | No Content        | Successful DELETE                    |
| 400  | Bad Request       | Malformed request                    |
| 401  | Unauthorized      | Missing/invalid auth                 |
| 403  | Forbidden         | Valid auth, insufficient permissions |
| 404  | Not Found         | Resource doesn't exist               |
| 422  | Unprocessable     | Validation failed                    |
| 429  | Too Many Requests | Rate limit exceeded                  |
| 500  | Internal Error    | Unexpected server failure            |

### SQL Injection Prevention

```python
# SAFE: parameterized query
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# SQLAlchemy ORM (inherently safe)
user = session.query(User).filter(User.id == user_id).first()

# NEVER: string interpolation
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")  # SQL injection!
```

### N+1 Query Prevention

```python
from sqlalchemy.orm import selectinload

# BAD: N+1 — fetches posts separately for each user
users = session.query(User).all()
for user in users:
    print(user.posts)  # triggers a query per user

# GOOD: eager loading — 2 queries total
users = session.query(User).options(selectinload(User.posts)).all()
```

### Indexing Strategy

```python
from sqlalchemy import Index


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    status = Column(String, index=True)

    __table_args__ = (Index("ix_users_status_created", "status", "created_at"),)
```

### Transactions

```python
from contextlib import contextmanager


@contextmanager
def transaction(session):
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise


with transaction(session) as s:
    s.add(user)
    s.add(audit_log)
```

## Workflow

1. Design resource URLs following REST conventions.
2. Define request/response models with Pydantic.
3. Use parameterized queries for all database access.
4. Add indexes for query patterns identified during development.
5. Profile queries in development to catch N+1 patterns.
6. Wrap multi-step mutations in transactions.

## Examples

Good:

```python
@app.get("/api/v1/users/{user_id}")
async def get_user(user_id: int) -> UserResponse:
    user = await repo.find(user_id)
    if not user:
        raise HTTPException(status_code=404)
    return UserResponse(user)
```

Why good: RESTful URL, proper 404 handling, Pydantic validation.

Bad:

```python
@app.post("/api/getUser")
async def get_user(data: dict):
    user = db.execute(f"SELECT * FROM users WHERE id = {data['id']}")
    return user
```

Why bad: POST for read, verb in URL, raw dict input, SQL injection, no validation.

## Verification

```bash
rg -n "execute\(f\"|execute\(\".*\+|\.format\(" --glob "**/*.py" | grep -i "select\|insert\|update\|delete"
rg -n "selectinload\|joinedload\|subqueryload" --glob "**/*.py"
```

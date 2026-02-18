---
name: backend-data-patterns
description: Database model design and migration patterns — naming, constraints, relationships, indexes, Alembic migrations, zero-downtime deployments. Use when defining models or creating database migrations.
---

# Backend Data Patterns

**Reviewed**: 2026-02-17 | **Scope**: Disabled skill revival — consolidates 2 disabled skills

## Scope

- Database models and migrations across FLEXT subprojects
- Schema definitions in `flext-auth/`, `flext-dbt-ldif/`
- Alembic migration files

## References

- <https://docs.sqlalchemy.org/en/20/>
- <https://alembic.sqlalchemy.org/en/latest/>
- `.claude/skills/lib-pydantic-v2/SKILL.md` — model validation patterns

## Rules

- Use singular table names matching the model class: `User` → `user`.
- Always add `created_at` and `updated_at` timestamps to persistent models.
- Define constraints at the database level (NOT NULL, UNIQUE, CHECK) — not just in application code.
- Make migrations reversible — every `upgrade()` must have a matching `downgrade()`.
- Never run data-destructive operations without a reversible migration plan.

## Instructions

### Model Design

```python
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

### Relationships

```python
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="posts")

class User(Base):
    # ...
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
```

### Indexes

```python
from sqlalchemy import Index

class User(Base):
    __tablename__ = "user"
    # ...
    __table_args__ = (
        Index("ix_user_email", "email", unique=True),
        Index("ix_user_status_created", "status", "created_at"),
    )
```

### Alembic Migration

```python
def upgrade() -> None:
    op.add_column("user", sa.Column("phone", sa.String(20), nullable=True))
    op.create_index("ix_user_phone", "user", ["phone"])

def downgrade() -> None:
    op.drop_index("ix_user_phone", table_name="user")
    op.drop_column("user", "phone")
```

### Zero-Downtime Column Addition

```python
# Step 1: Add nullable column (no lock)
def upgrade() -> None:
    op.add_column("user", sa.Column("new_field", sa.String(50), nullable=True))

# Step 2: Backfill data (separate migration)
def upgrade() -> None:
    op.execute("UPDATE user SET new_field = 'default' WHERE new_field IS NULL")

# Step 3: Add constraint (separate migration)
def upgrade() -> None:
    op.alter_column("user", "new_field", nullable=False)
```

### Idempotent Data Migrations

```python
def upgrade() -> None:
    op.execute("""
        UPDATE user SET status = 'active'
        WHERE status IS NULL
        AND created_at > '2024-01-01'
    """)
```

## Workflow

1. Design model with proper types, constraints, and relationships.
2. Generate Alembic migration: `alembic revision --autogenerate -m "description"`.
3. Review generated migration — verify both upgrade and downgrade.
4. Test migration: apply, verify, rollback, verify again.
5. For large tables, split into multi-step zero-downtime migrations.

## Examples

Good:

```python
op.add_column("user", sa.Column("role", sa.String(20), server_default="viewer", nullable=False))
```

Why good: uses `server_default` to avoid table lock on existing rows.

Bad:

```python
op.add_column("user", sa.Column("role", sa.String(20), nullable=False))
```

Why bad: adding NOT NULL column without default locks the table and fails on existing rows.

## Verification

```bash
rg -n "def upgrade\|def downgrade" --glob "*.py" | head -20
rg -n "nullable=False" --glob "**/*.py" | grep "add_column"
rg -n "server_default\|ondelete\|onupdate" --glob "**/*.py"
```

---
name: database-skill
description: Create and manage database tables, migrations, and schema design for backend services. Use for SQL-based persistent storage.
---

# Database Skill

## Instructions

1. **Schema Design**
   - Design tables for users, tasks, and related entities
   - Define primary keys, foreign keys, and indexes
   - Ensure data types are appropriate for fields (strings, timestamps, booleans, etc.)

2. **Migrations**
   - Implement migrations for schema updates
   - Keep migration history organized and versioned
   - Ensure backward compatibility when possible

3. **Table Management**
   - Create, update, and delete tables safely
   - Optimize table structure for queries and performance
   - Enforce constraints (unique, not null, foreign keys)

4. **Database Interaction**
   - Ensure ORM (SQLModel) models reflect schema accurately
   - Validate queries and transactions for correctness
   - Handle data integrity and consistency across tables

## Best Practices
- Use descriptive table and column names
- Avoid redundant data
- Index frequently queried columns
- Keep migration scripts idempotent and reviewable
- Test schema changes in a safe environment before production

## Example Schema
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  title VARCHAR(200) NOT NULL,
  description TEXT,
  completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

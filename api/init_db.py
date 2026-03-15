"""
Database schema initialization script.

Creates all necessary tables for the Vercel deployment:
- users: Authentication and user profiles
- user_backgrounds: Learning preferences and background info
- conversation_histories: RAG chat history

This script is idempotent - it can be run multiple times safely.
Use before first deployment or after database reset.

Run: python api/init_db.py
"""

import asyncio
import asyncpg
import os
from datetime import datetime


DATABASE_URL = os.getenv("DATABASE_URL", "")


async def initialize_database():
    """Create all database tables."""

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set")

    conn = await asyncpg.connect(DATABASE_URL)

    try:
        # Create users table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
            CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
        """)

        print("✅ Created 'users' table")

        # Create user_backgrounds table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_backgrounds (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                software_background VARCHAR(50) DEFAULT 'beginner',
                hardware_background VARCHAR(50) DEFAULT 'none',
                ros_experience VARCHAR(50) DEFAULT 'none',
                python_level VARCHAR(50) DEFAULT 'beginner',
                learning_goal VARCHAR(50) DEFAULT 'career',
                available_hardware VARCHAR(255) DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_user_backgrounds_user_id
            ON user_backgrounds(user_id);
        """)

        print("✅ Created 'user_backgrounds' table")

        # Create conversation_histories table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS conversation_histories (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                conversation_id UUID NOT NULL,
                role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant')),
                message TEXT NOT NULL,
                tokens_used INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_conversation_histories_user_id
            ON conversation_histories(user_id);

            CREATE INDEX IF NOT EXISTS idx_conversation_histories_conversation_id
            ON conversation_histories(conversation_id);

            CREATE INDEX IF NOT EXISTS idx_conversation_histories_created_at
            ON conversation_histories(created_at);
        """)

        print("✅ Created 'conversation_histories' table")

        # Verify tables exist
        tables = await conn.fetch("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        print("\n📊 Database tables:")
        for table in tables:
            print(f"   - {table['table_name']}")

        print("\n✅ Database initialized successfully!")

    except asyncpg.DuplicateTableError as e:
        print(f"⚠️  Table already exists: {str(e)}")
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    try:
        asyncio.run(initialize_database())
    except Exception as e:
        print(f"❌ Failed to initialize database: {str(e)}")
        exit(1)

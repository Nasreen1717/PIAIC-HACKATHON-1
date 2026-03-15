-- RAG Chatbot PostgreSQL Schema
-- Version: 1.0.0
-- Date: 2026-01-27
-- Platform: Neon Postgres 14+
-- Dependencies: pgvector extension (for semantic search on message embeddings)

-- Enable pgvector extension for embedding storage
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- CONVERSATIONS TABLE
-- ============================================================================
-- Represents a user session/conversation with the chatbot.
-- Contains metadata about the conversation (title, created_at, etc.)

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    title VARCHAR(500),
    metadata JSONB DEFAULT '{}',

    -- Constraints
    CONSTRAINT uk_session_id UNIQUE (session_id),
    CONSTRAINT valid_user_id CHECK (user_id != ''),
    CONSTRAINT valid_session_id CHECK (session_id != ''),
    CONSTRAINT valid_timestamps CHECK (created_at <= updated_at)
);

-- Indexes for conversation queries
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);

COMMENT ON TABLE conversations IS 'User sessions/conversations with the RAG chatbot';
COMMENT ON COLUMN conversations.id IS 'Unique conversation identifier';
COMMENT ON COLUMN conversations.user_id IS 'Identifier from Docusaurus (user account or hashed IP)';
COMMENT ON COLUMN conversations.session_id IS 'HTTP session cookie or browser fingerprint; must be unique';
COMMENT ON COLUMN conversations.title IS 'Auto-generated title from first question; e.g., "Understanding ROS 2 Actions"';
COMMENT ON COLUMN conversations.metadata IS 'JSON metadata: module_context, device, model_version, etc.';

-- ============================================================================
-- MESSAGES TABLE
-- ============================================================================
-- Individual Q&A exchanges within conversations.
-- Stores user queries and assistant responses with embeddings for semantic search.

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT fk_conversation_id FOREIGN KEY (conversation_id)
        REFERENCES conversations(id) ON DELETE CASCADE,
    CONSTRAINT valid_role CHECK (role IN ('user', 'assistant')),
    CONSTRAINT non_empty_content CHECK (content != '')
);

-- Indexes for message queries
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
-- Vector similarity search index using IVFFLAT
CREATE INDEX idx_messages_embedding_ivfflat ON messages
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

COMMENT ON TABLE messages IS 'Individual user queries and assistant responses within conversations';
COMMENT ON COLUMN messages.id IS 'Unique message identifier';
COMMENT ON COLUMN messages.conversation_id IS 'Foreign key to parent conversation';
COMMENT ON COLUMN messages.role IS '"user" for queries, "assistant" for responses';
COMMENT ON COLUMN messages.content IS 'Full text of question (1-2000 chars) or response (≤4000 chars)';
COMMENT ON COLUMN messages.embedding IS 'OpenAI text-embedding-3-small for semantic caching/search';
COMMENT ON COLUMN messages.metadata IS 'Role-specific: selected_text, retrieval_chunks, generation_time_ms, etc.';

-- ============================================================================
-- CITATIONS TABLE
-- ============================================================================
-- Structured references to textbook sources for each response.
-- Provides academic integrity and enables verification.

CREATE TABLE citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL,
    chapter_number INT NOT NULL,
    section_title VARCHAR(500) NOT NULL,
    subsection VARCHAR(500),
    page_reference INT,
    docusaurus_url VARCHAR(1024) NOT NULL,
    confidence_score FLOAT DEFAULT 1.0,
    ieee_formatted_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT fk_message_id FOREIGN KEY (message_id)
        REFERENCES messages(id) ON DELETE CASCADE,
    CONSTRAINT valid_chapter CHECK (chapter_number BETWEEN 1 AND 12),
    CONSTRAINT valid_confidence CHECK (confidence_score BETWEEN 0.0 AND 1.0),
    CONSTRAINT valid_url CHECK (docusaurus_url LIKE '/docs/%'),
    CONSTRAINT non_empty_section CHECK (section_title != ''),
    CONSTRAINT non_empty_ieee CHECK (ieee_formatted_text != '')
);

-- Indexes for citation queries
CREATE INDEX idx_citations_message_id ON citations(message_id);
CREATE INDEX idx_citations_chapter ON citations(chapter_number);
CREATE INDEX idx_citations_docusaurus_url ON citations(docusaurus_url);

COMMENT ON TABLE citations IS 'IEEE-formatted citations referencing textbook sources';
COMMENT ON COLUMN citations.id IS 'Unique citation identifier';
COMMENT ON COLUMN citations.message_id IS 'Foreign key to assistant message';
COMMENT ON COLUMN citations.chapter_number IS 'Physical AI textbook chapter (1-12)';
COMMENT ON COLUMN citations.section_title IS 'Section heading in textbook';
COMMENT ON COLUMN citations.docusaurus_url IS 'Direct link to section in published book';
COMMENT ON COLUMN citations.confidence_score IS 'Confidence in citation match (1.0 = direct, 0.7 = topic)';
COMMENT ON COLUMN citations.ieee_formatted_text IS 'Pre-formatted IEEE citation: "[N] Chapter X, Section Y"';

-- ============================================================================
-- EMBEDDING_BATCHES TABLE
-- ============================================================================
-- Tracking for OpenAI Batch API jobs for content ingestion.
-- Enables monitoring, retry logic, and cost tracking.

CREATE TABLE embedding_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id VARCHAR(255) UNIQUE,
    status VARCHAR(50) NOT NULL,
    chunk_count INT DEFAULT 0,
    chapters_included INT[] DEFAULT ARRAY[]::INT[],
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    cost_usd DECIMAL(10, 4) DEFAULT 0.00,

    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('submitted', 'processing', 'completed', 'failed')),
    CONSTRAINT valid_chunk_count CHECK (chunk_count >= 0),
    CONSTRAINT valid_cost CHECK (cost_usd >= 0),
    CONSTRAINT completion_logic CHECK (
        (status IN ('submitted', 'processing') AND completed_at IS NULL) OR
        (status IN ('completed', 'failed') AND completed_at IS NOT NULL)
    )
);

-- Indexes for batch tracking
CREATE INDEX idx_embedding_batches_batch_id ON embedding_batches(batch_id);
CREATE INDEX idx_embedding_batches_status ON embedding_batches(status);
CREATE INDEX idx_embedding_batches_submitted_at ON embedding_batches(submitted_at DESC);

COMMENT ON TABLE embedding_batches IS 'Tracking for OpenAI Batch API embedding jobs';
COMMENT ON COLUMN embedding_batches.id IS 'Unique batch tracking identifier';
COMMENT ON COLUMN embedding_batches.batch_id IS 'OpenAI Batch API job ID; e.g., "batch_abc123xyz"';
COMMENT ON COLUMN embedding_batches.status IS 'submitted | processing | completed | failed';
COMMENT ON COLUMN embedding_batches.chapters_included IS 'Array of chapter numbers (1-12) processed';
COMMENT ON COLUMN embedding_batches.cost_usd IS 'Cost calculation: (token_count / 1M) * $0.02';

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Recent conversations for a user
CREATE OR REPLACE VIEW v_user_recent_conversations AS
SELECT
    c.id,
    c.user_id,
    c.title,
    c.created_at,
    c.updated_at,
    (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) AS message_count,
    (SELECT content FROM messages
     WHERE conversation_id = c.id AND role = 'user'
     ORDER BY created_at DESC LIMIT 1) AS last_question
FROM conversations c
ORDER BY c.updated_at DESC;

COMMENT ON VIEW v_user_recent_conversations IS
'Recent conversations with message counts and last question preview';

-- Citation statistics by chapter
CREATE OR REPLACE VIEW v_citation_statistics AS
SELECT
    c.chapter_number,
    COUNT(*) AS citation_count,
    AVG(c.confidence_score) AS avg_confidence,
    MIN(c.created_at) AS first_cited_at,
    MAX(c.created_at) AS last_cited_at
FROM citations c
GROUP BY c.chapter_number
ORDER BY citation_count DESC;

COMMENT ON VIEW v_citation_statistics IS
'Analytics: citation frequency and confidence by chapter';

-- Batch processing status summary
CREATE OR REPLACE VIEW v_batch_status_summary AS
SELECT
    status,
    COUNT(*) AS batch_count,
    SUM(chunk_count) AS total_chunks,
    SUM(cost_usd) AS total_cost,
    MAX(submitted_at) AS most_recent
FROM embedding_batches
GROUP BY status;

COMMENT ON VIEW v_batch_status_summary IS
'Summary of embedding batch processing status';

-- ============================================================================
-- FUNCTIONS FOR MAINTENANCE
-- ============================================================================

-- Function to auto-update conversation.updated_at on message insert
CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to call the function
DROP TRIGGER IF EXISTS trigger_update_conversation_timestamp ON messages;
CREATE TRIGGER trigger_update_conversation_timestamp
AFTER INSERT ON messages
FOR EACH ROW
EXECUTE FUNCTION update_conversation_timestamp();

COMMENT ON FUNCTION update_conversation_timestamp() IS
'Auto-update conversation.updated_at when new message is inserted';

-- Function to cleanup old embedding batches
CREATE OR REPLACE FUNCTION cleanup_old_batches()
RETURNS TABLE (deleted_count INT) AS $$
BEGIN
    DELETE FROM embedding_batches
    WHERE status = 'failed' AND created_at < CURRENT_TIMESTAMP - INTERVAL '7 days';

    RETURN QUERY SELECT ROW_COUNT()::INT;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_old_batches() IS
'Delete failed batches older than 7 days (for maintenance)';

-- ============================================================================
-- INITIAL DATA SETUP (Optional - for testing/development)
-- ============================================================================

-- Note: In production, these would be populated by the application layer.
-- Uncomment below for development/testing database setup.

/*
-- Example test conversation
INSERT INTO conversations (user_id, session_id, title, metadata)
VALUES (
    'test@example.com',
    'test_session_123',
    'Test Conversation',
    '{"module_context": 1, "device": "desktop"}'::jsonb
);

-- Example test messages (to be populated after conversations insert)
-- INSERT INTO messages (conversation_id, role, content, metadata)
-- VALUES (...)
*/

-- ============================================================================
-- SCHEMA VERSION INFORMATION
-- ============================================================================

COMMENT ON SCHEMA public IS
'RAG Chatbot PostgreSQL Schema - v1.0.0 (2026-01-27)
Tables: conversations, messages, citations, embedding_batches
Extensions: pgvector (for vector embeddings)
Author: Physical AI Chatbot Team';

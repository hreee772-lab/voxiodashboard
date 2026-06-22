-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. clients
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name TEXT NOT NULL,
    company_email TEXT NOT NULL,
    domain TEXT,
    logo_url TEXT,
    plan TEXT CHECK (plan IN ('free', 'starter', 'pro', 'enterprise')) DEFAULT 'free',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT CHECK (role IN ('admin', 'specialist', 'super_admin')) DEFAULT 'specialist',
    department TEXT,
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. widget_config
CREATE TABLE widget_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    primary_color TEXT DEFAULT '#000000',
    position TEXT DEFAULT 'bottom-right',
    greeting_message TEXT,
    channels_enabled TEXT CHECK (channels_enabled IN ('voice', 'chat', 'both')) DEFAULT 'both',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. bot_config
CREATE TABLE bot_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    bot_name TEXT DEFAULT 'Voicera Assistant',
    default_greeting TEXT,
    system_prompt TEXT,
    blacklisted_topics TEXT,
    max_clarifying_questions INTEGER DEFAULT 3,
    escalation_message TEXT,
    voice_model TEXT,
    stt_model TEXT,
    chat_response_length TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. kb_documents
CREATE TABLE kb_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    file_type TEXT CHECK (file_type IN ('pdf', 'docx', 'txt', 'url')) NOT NULL,
    file_url TEXT,
    status TEXT CHECK (status IN ('processing', 'ready', 'failed')) DEFAULT 'processing',
    chunk_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. kb_chunks
CREATE TABLE kb_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    document_id UUID REFERENCES kb_documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. sessions (Created before kb_gaps due to foreign key dependency)
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    customer_name TEXT,
    customer_email TEXT,
    issue_type TEXT,
    channel TEXT CHECK (channel IN ('voice', 'chat')),
    status TEXT CHECK (status IN ('active', 'resolved', 'escalated', 'closed')) DEFAULT 'active',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    transcript JSONB,
    recording_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. kb_gaps
CREATE TABLE kb_gaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    frequency INTEGER DEFAULT 1,
    is_filled BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. tickets
CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    customer_name TEXT,
    customer_email TEXT,
    issue_type TEXT,
    issue_summary TEXT,
    department TEXT,
    status TEXT CHECK (status IN ('open', 'active', 'resolved', 'closed')) DEFAULT 'open',
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    closed_at TIMESTAMPTZ
);

-- 10. bookings
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID REFERENCES tickets(id) ON DELETE CASCADE,
    specialist_id UUID REFERENCES users(id) ON DELETE CASCADE,
    customer_name TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    scheduled_at TIMESTAMPTZ NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    status TEXT CHECK (status IN ('pending', 'confirmed', 'completed', 'no_show', 'rescheduled')) DEFAULT 'pending',
    calendar_event_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 11. routing_rules
CREATE TABLE routing_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    issue_type TEXT NOT NULL,
    department TEXT NOT NULL,
    specialist_ids JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 12. availability
CREATE TABLE availability (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    specialist_id UUID REFERENCES users(id) ON DELETE CASCADE,
    day_of_week INTEGER CHECK (day_of_week >= 0 AND day_of_week <= 6),
    is_available BOOLEAN DEFAULT true,
    start_time TIME,
    end_time TIME,
    timezone TEXT DEFAULT 'UTC',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 13. email_logs
CREATE TABLE email_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    ticket_id UUID REFERENCES tickets(id) ON DELETE CASCADE,
    recipient_email TEXT NOT NULL,
    email_type TEXT CHECK (email_type IN ('escalation', 'booking_confirmation', 'resolution', 'no_show', 'rescheduling')),
    status TEXT CHECK (status IN ('sent', 'failed')),
    sent_at TIMESTAMPTZ DEFAULT NOW()
);

-- 14. integrations
CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    crm_type TEXT CHECK (crm_type IN ('hubspot', 'salesforce', 'zendesk', 'zoho', 'freshdesk', 'custom')),
    mcp_server_url TEXT,
    auth_token_encrypted TEXT,
    allowed_fields JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 15. subscriptions
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    plan TEXT CHECK (plan IN ('free', 'starter', 'pro', 'enterprise')),
    status TEXT CHECK (status IN ('active', 'cancelled', 'past_due')),
    razorpay_subscription_id TEXT,
    razorpay_customer_id TEXT,
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 16. waitlist
CREATE TABLE waitlist (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    source TEXT DEFAULT 'landing_page',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- Create Indexes
-- ==========================================
CREATE INDEX ix_kb_chunks_embedding ON kb_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX ix_sessions_client_status ON sessions(client_id, status);
CREATE INDEX ix_tickets_client_status_assigned ON tickets(client_id, status, assigned_to);
CREATE INDEX ix_users_client_role ON users(client_id, role);

-- ==========================================
-- Enable Row Level Security (RLS)
-- ==========================================
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE widget_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE bot_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE kb_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE kb_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE kb_gaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE routing_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE availability ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE waitlist ENABLE ROW LEVEL SECURITY;

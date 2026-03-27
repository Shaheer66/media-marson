
CREATE TABLE IF NOT EXISTS books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    pre_outline_notes TEXT,
    status TEXT DEFAULT 'drafting_outline', -- 'drafting_outline', 'completed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chapters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id UUID REFERENCES books(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT,
    summary TEXT,
    chapter_number INTEGER NOT NULL,
    status TEXT DEFAULT 'pending_generation', -- 'pending_generation', 'review_required', 'approved'
    editor_notes TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- MIRRALISM V5 データベース初期化スクリプト
-- 設計書v3.0に基づくテーブル定義

-- ファイル処理状態管理テーブル
CREATE TABLE IF NOT EXISTS file_processing_status (
    id SERIAL PRIMARY KEY,
    file_path VARCHAR(500) NOT NULL UNIQUE,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) CHECK(file_type IN ('meeting', 'email', 'memo', 'document', 'unknown')),
    status VARCHAR(50) CHECK(status IN ('pending', 'processing', 'completed', 'error', 'archived')),
    file_size INTEGER,
    file_hash VARCHAR(64),  -- SHA256ハッシュで重複検出
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    error_message TEXT,
    extracted_summary TEXT,
    output_paths TEXT[],  -- 生成された成果物のパス
    related_profile_ids INTEGER[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_processing_status ON file_processing_status(status);
CREATE INDEX IF NOT EXISTS idx_file_type ON file_processing_status(file_type);
CREATE INDEX IF NOT EXISTS idx_detected_at ON file_processing_status(detected_at DESC);

-- 人物プロファイルテーブル
CREATE TABLE IF NOT EXISTS profiles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    type VARCHAR(50) CHECK(type IN ('self', 'client', 'family', 'friend', 'colleague')),
    organization VARCHAR(255),
    tags TEXT[],
    characteristics JSONB,
    interaction_count INTEGER DEFAULT 0,
    last_interaction DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 知識エントリーテーブル
CREATE TABLE IF NOT EXISTS knowledge_entries (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    summary TEXT,
    source_type VARCHAR(50) CHECK(source_type IN ('meeting', 'memo', 'email', 'thought', 'transcription')),
    source_file_id INTEGER REFERENCES file_processing_status(id),
    related_profile_ids INTEGER[],
    extracted_info JSONB,
    tags TEXT[],
    file_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 学習パターンテーブル
CREATE TABLE IF NOT EXISTS learning_patterns (
    id SERIAL PRIMARY KEY,
    pattern_type VARCHAR(100) NOT NULL,
    original_text TEXT NOT NULL,
    corrected_text TEXT NOT NULL,
    context TEXT,
    abstraction_rule TEXT,
    confidence FLOAT DEFAULT 0.5,
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 生成履歴テーブル
CREATE TABLE IF NOT EXISTS generation_history (
    id SERIAL PRIMARY KEY,
    output_type VARCHAR(50),
    target_profile_id INTEGER REFERENCES profiles(id),
    file_path TEXT,
    prompt_used TEXT,
    quality_score FLOAT,
    user_feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 初期データの挿入
INSERT INTO profiles (name, type, organization, characteristics) 
VALUES ('末武修平', 'self', '株式会社末武コンサルティング', 
        '{"approach": "段階的導入", "expertise": ["システム導入", "業務改善"], "style": "丁寧で分かりやすい説明"}')
ON CONFLICT (name) DO NOTHING;

-- テーブル作成完了メッセージ
SELECT 'MIRRALISM V5 データベース初期化完了' AS message;
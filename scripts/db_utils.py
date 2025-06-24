#!/usr/bin/env python3
"""
データベース操作ユーティリティ
Claude Codeが必要に応じて使うDB操作ツール
"""

import psycopg2
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

class MirralismDB:
    """MIRRALISM V5 データベース操作クラス"""
    
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                "dbname=mirralism user=postgres password=mirralism host=localhost"
            )
        except psycopg2.OperationalError as e:
            print(f"警告: PostgreSQLに接続できません: {e}")
            self.conn = None
    
    def create_tables(self):
        """テーブルを作成"""
        if not self.conn:
            return False
            
        create_sql = """
        -- ファイル処理状態管理
        CREATE TABLE IF NOT EXISTS file_processing_status (
            id SERIAL PRIMARY KEY,
            file_path VARCHAR(500) NOT NULL UNIQUE,
            file_name VARCHAR(255) NOT NULL,
            file_type VARCHAR(50) CHECK(file_type IN ('meeting', 'email', 'memo', 'document', 'unknown')),
            status VARCHAR(50) CHECK(status IN ('pending', 'processing', 'completed', 'error', 'archived')),
            file_size INTEGER,
            file_hash VARCHAR(64),
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processing_started_at TIMESTAMP,
            processing_completed_at TIMESTAMP,
            error_message TEXT,
            extracted_summary TEXT,
            output_paths TEXT[],
            related_profile_ids INTEGER[],
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- インデックス
        CREATE INDEX IF NOT EXISTS idx_processing_status ON file_processing_status(status);
        CREATE INDEX IF NOT EXISTS idx_file_type ON file_processing_status(file_type);
        CREATE INDEX IF NOT EXISTS idx_detected_at ON file_processing_status(detected_at DESC);

        -- 人物プロファイル
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

        -- 知識エントリー
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

        -- 学習パターン
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

        -- 生成履歴
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
        """
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(create_sql)
                self.conn.commit()
                return True
        except Exception as e:
            print(f"テーブル作成エラー: {e}")
            return False
    
    def add_profile(self, name: str, profile_type: str, organization: str = None, 
                   characteristics: Dict = None) -> Optional[int]:
        """プロファイルを追加"""
        if not self.conn:
            return None
            
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO profiles (name, type, organization, characteristics)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (name) 
                    DO UPDATE SET 
                        type = EXCLUDED.type,
                        organization = EXCLUDED.organization,
                        characteristics = EXCLUDED.characteristics,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id
                """, (name, profile_type, organization, json.dumps(characteristics) if characteristics else None))
                
                profile_id = cur.fetchone()[0]
                self.conn.commit()
                return profile_id
        except Exception as e:
            print(f"プロファイル追加エラー: {e}")
            return None
    
    def add_knowledge_entry(self, content: str, summary: str = None, source_type: str = None,
                           source_file_id: int = None, related_profile_ids: List[int] = None,
                           extracted_info: Dict = None, tags: List[str] = None,
                           file_path: str = None) -> Optional[int]:
        """知識エントリーを追加"""
        if not self.conn:
            return None
            
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO knowledge_entries 
                    (content, summary, source_type, source_file_id, related_profile_ids, 
                     extracted_info, tags, file_path)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (content, summary, source_type, source_file_id, 
                      related_profile_ids, json.dumps(extracted_info) if extracted_info else None,
                      tags, file_path))
                
                entry_id = cur.fetchone()[0]
                self.conn.commit()
                return entry_id
        except Exception as e:
            print(f"知識エントリー追加エラー: {e}")
            return None
    
    def get_profiles(self, profile_type: str = None) -> List[Dict]:
        """プロファイル一覧を取得"""
        if not self.conn:
            return []
            
        try:
            with self.conn.cursor() as cur:
                if profile_type:
                    cur.execute("SELECT * FROM profiles WHERE type = %s ORDER BY name", (profile_type,))
                else:
                    cur.execute("SELECT * FROM profiles ORDER BY name")
                
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            print(f"プロファイル取得エラー: {e}")
            return []
    
    def get_knowledge_entries(self, profile_id: int = None, limit: int = 50) -> List[Dict]:
        """知識エントリーを取得"""
        if not self.conn:
            return []
            
        try:
            with self.conn.cursor() as cur:
                if profile_id:
                    cur.execute("""
                        SELECT * FROM knowledge_entries 
                        WHERE %s = ANY(related_profile_ids)
                        ORDER BY created_at DESC LIMIT %s
                    """, (profile_id, limit))
                else:
                    cur.execute("""
                        SELECT * FROM knowledge_entries 
                        ORDER BY created_at DESC LIMIT %s
                    """, (limit,))
                
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            print(f"知識エントリー取得エラー: {e}")
            return []

# スタンドアロン関数
def setup_database():
    """データベースをセットアップ"""
    db = MirralismDB()
    return db.create_tables()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_database()
    else:
        print("使い方: python db_utils.py setup")
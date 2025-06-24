#!/usr/bin/env python3
"""
Claude Codeが使うファイル操作ユーティリティ
これは自動処理スクリプトではなく、Claude Codeが必要に応じて呼び出すツール
"""

import os
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import psycopg2

class FileUtils:
    """Claude Codeが使うファイル操作補助ツール"""
    
    def __init__(self):
        self.input_dir = Path("input")
        self.archive_dir = Path("archive")
        
    def get_available_files(self) -> List[Dict]:
        """Claude Codeが処理対象を選択するための情報を提供"""
        files = []
        
        # これは自動処理ではない
        # Claude Codeが「どのファイルがあるか」を知るためのツール
        # 実際の処理はClaude Codeが個別に判断して実行する
        if self.input_dir.exists():
            for root, dirs, filenames in os.walk(self.input_dir):
                for filename in filenames:
                    if filename.startswith('.'):
                        continue
                        
                    file_path = Path(root) / filename
                    files.append({
                        'path': str(file_path),
                        'name': filename,
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime),
                        'parent_dir': file_path.parent.name
                    })
                    
        return sorted(files, key=lambda x: x['modified'], reverse=True)
    
    def read_file_content(self, file_path: str) -> str:
        """ファイル内容を読み込み"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def save_to_output(self, content: str, output_path: str) -> bool:
        """outputディレクトリに保存"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return True
    
    def get_file_hash(self, file_path: str) -> str:
        """ファイルのハッシュ値を計算"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

class DBUtils:
    """Claude Codeが使うDB操作補助ツール"""
    
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                "dbname=mirralism user=postgres password=mirralism host=localhost"
            )
        except psycopg2.OperationalError:
            print("警告: PostgreSQLに接続できません。データベース機能は無効です。")
            self.conn = None
        
    def record_file_processing(self, file_info: Dict) -> Optional[int]:
        """ファイル処理を記録"""
        if not self.conn:
            return None
            
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO file_processing_status 
                (file_path, file_name, file_type, status, file_size, file_hash)
                VALUES (%s, %s, %s, 'completed', %s, %s)
                ON CONFLICT (file_path) 
                DO UPDATE SET 
                    status = 'completed',
                    processing_completed_at = NOW()
                RETURNING id
            """, (
                file_info['path'],
                file_info['name'],
                file_info.get('type', 'unknown'),
                file_info.get('size', 0),
                file_info.get('hash', '')
            ))
            file_id = cur.fetchone()[0]
            self.conn.commit()
            return file_id
    
    def is_file_processed(self, file_path: str) -> Optional[Dict]:
        """ファイルが処理済みか確認"""
        if not self.conn:
            return None
            
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, status, processing_completed_at
                FROM file_processing_status
                WHERE file_path = %s
            """, (file_path,))
            
            result = cur.fetchone()
            if result:
                return {
                    'id': result[0],
                    'status': result[1],
                    'completed_at': result[2]
                }
            return None

# Claude Codeが必要に応じて使う関数
def get_input_status():
    """Claude Codeが判断に使うinputディレクトリの状態を取得"""
    file_utils = FileUtils()
    db_utils = DBUtils()
    
    # Claude Codeが選択するためのファイル一覧を取得
    files = file_utils.get_available_files()
    status = {
        'total_files': len(files),
        'files': []
    }
    
    for file in files:
        processing_info = db_utils.is_file_processed(file['path'])
        file['processing_status'] = processing_info
        status['files'].append(file)
        
    return status

if __name__ == "__main__":
    # Claude Codeから呼び出される
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        status = get_input_status()
        print(json.dumps(status, ensure_ascii=False, indent=2, default=str))
    else:
        print("使い方: python file_utils.py status")
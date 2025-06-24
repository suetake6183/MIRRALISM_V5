# MIRRALISM V5 実装仕様書（Claude Code直接実行版）

**作成日**: 2025年6月24日  
**バージョン**: 3.0  
**対象**: Claude CodeまたはCursorを使用する実装者

---

## 📌 実装者向け要約

このシステムは、末武さんの知識とクライアント情報を蓄積し、末武さんらしい提案書等を自動生成する個人用ナレッジベースです。**Claude Codeが主体的にファイルを理解し処理**することで、見せかけではない本物の知的処理を実現します。

**v3.0の主要変更**: inputディレクトリを追加。ただし「自動処理」ではなく、Claude Codeが主体的に処理する設計を維持。

---

## 🎯 確定要件一覧

```yaml
基本要件:
  - プロジェクト名: MIRRALISM V5
  - 開発方針: 完全新規開発（V4のコード不使用）
  - 利用者: 末武さん個人のみ
  - 動作環境: M2 Mac (16GB RAM) ローカル環境
  - 処理方式: Claude Codeが直接実行（APIサーバー不要）
  - 月額予算: 1万円以内（Claude Code除く）

機能要件:
  - データ入力: inputディレクトリ経由での自動処理
  - データ規模: 50人以上のプロファイル、1日5-10件の入力
  - 出力形式: Markdownファイル（Obsidianで閲覧）
  - 生成頻度: 毎日コンテンツ生成
  - 処理速度: 品質優先（1分以上の処理も許容）

技術要件:
  - 言語: Python 3.11
  - DB: PostgreSQL + pgvector
  - ベクトル検索: ChromaDB（ローカル）
  - バックアップ: GitHub + 外付けSSD
  - セキュリティ: パスワード不要（ローカル環境）
```

---

## 🏗️ システムアーキテクチャ（入力処理フロー追加版）

```
┌─────────────────┐
│  末武さん       │
└────────┬────────┘
         │ ファイルを配置
    ┌────┴────┐
    │  input/  │ ← 解析対象ファイル
    └────┬────┘
         │
┌────────┴────────┐
│  Claude Code    │ ← 「inputディレクトリを見て処理して」
└────────┬────────┘
         │
    ┌────┴────────┐
    │ 主体的に処理 │
    └────┬────────┘
         │
┌────────┼────────┬──────────────┐
│        │        │              │
│  内容を理解     │  情報を抽出     │
│  文脈を判断     │  適切に保存     │
│  学習・記憶     │  成果物生成     │
└────────┴────────┴──────────────┘
         │
┌────────┴────────┐
│  archive/       │ ← 処理済みファイル（末武さんが手動移動）
└─────────────────┘
```

---

## 📁 ディレクトリ構造（更新版）

```
MIRRALISM_V5/
├── input/                       # 【新規】解析待ちファイル置き場
│   ├── meetings/               # 会議録音・文字起こし
│   ├── emails/                 # メール
│   ├── memos/                  # メモ・思考
│   └── documents/              # その他文書
│
├── archive/                     # 【新規】処理済みファイル保管
│   ├── 2025-06/               # 年月別に自動整理
│   │   ├── meetings/
│   │   ├── emails/
│   │   └── documents/
│   └── 2025-07/
│
├── .claude/                     # Claude Code専用ルール
│   ├── context.md              # 毎回読み込む基本ルール
│   ├── learning_rules.md       # 学習機能のルール
│   ├── generation_rules.md     # 生成機能のルール
│   └── input_processing.md     # 【新規】入力処理ルール
│
├── .notes/                     # プロジェクトの頭脳
│   ├── project_overview.md     # プロジェクト概要
│   ├── task_list.md           # タスクと進捗
│   ├── learning_log.md        # 学習の改善記録
│   └── processing_log.md      # 【新規】ファイル処理履歴
│
├── outputs/                    # 成果物（Obsidianで直接開く）
│   ├── clients/               # クライアント別
│   │   ├── クライアントA/
│   │   │   ├── proposals/     # 提案書
│   │   │   ├── meetings/      # 会議録
│   │   │   └── notes/         # メモ
│   │   └── クライアントB/
│   │
│   └── personal/              # 末武さん個人
│       ├── blog/              # ブログ記事
│       ├── youtube/           # YouTube台本
│       ├── thoughts/          # 思考・アイデア
│       └── learning/          # 学んだこと
│
├── scripts/                    # Claude Code実行用
│   ├── file_utils.py          # 【新規】ファイル操作補助ツール
│   ├── analyze.py             # データ分析補助
│   ├── generate.py            # コンテンツ生成補助
│   ├── learn.py               # 学習処理補助
│   └── db_utils.py            # DB操作ユーティリティ
│
├── data/
│   ├── profiles/              # 人物プロファイル
│   ├── embeddings/            # ChromaDBデータ
│   └── patterns/              # 学習パターン保存
│
├── requirements.txt           # 依存関係
└── README.md                 # セットアップ手順
```

---

## 🤖 Claude Code運用手順（入力処理フロー追加）

### 初回セットアップ
```bash
claude "プロジェクトルート: ~/MIRRALISM_V5
以下のファイルを読んでプロジェクトを理解してください:
1. .claude/context.md
2. .notes/project_overview.md
3. README.md"
```

### 日常的な使い方

#### 1. 【新規】入力ファイルの処理（Claude Code主体）
```bash
# 末武さんがファイルをinputディレクトリに配置後
claude "inputディレクトリを確認してください。
新しいファイルがあれば、内容を読んで理解し、適切に処理してください。

スクリプトは使わず、あなたが直接：
1. ファイルを読む
2. 内容を理解する
3. 必要な情報を抽出する
4. 適切な形式で保存する
5. 学習すべき点があれば記録する"
```

#### 2. 【新規】特定ファイルの処理例
```bash
claude "input/meetings/2025-06-24_クライアントA.txt を読んで処理してください。

以下の観点で内容を理解し、適切に処理してください：
- 参加者は誰か
- 何が決まったか
- 次のアクションは何か
- 提案書に含めるべき要素は何か

処理後は outputs/clients/クライアントA/meetings/ に保存してください。"
```

#### 3. 【新規】処理状態の確認
```bash
claude "inputディレクトリを見て、以下を教えてください：
- どんなファイルがあるか
- どれが重要そうか
- 最近処理したファイルとその概要
- 処理が必要なファイルの優先順位

あなたの判断で優先順位をつけて、理由も説明してください。"
```

#### 4. 会議録の分析と保存（従来通り、ただし入力元が変更）
```bash
claude "input/meetings/ にある未処理の会議録をすべて分析してください。
優先順位は日付が新しいものから。"
```

---

## 💾 データベース設計（ファイル処理管理テーブル追加）

```sql
-- 【新規】ファイル処理状態管理
CREATE TABLE file_processing_status (
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
CREATE INDEX idx_processing_status ON file_processing_status(status);
CREATE INDEX idx_file_type ON file_processing_status(file_type);
CREATE INDEX idx_detected_at ON file_processing_status(detected_at DESC);

-- 既存テーブルの修正
ALTER TABLE knowledge_entries ADD COLUMN source_file_id INTEGER REFERENCES file_processing_status(id);

-- 人物プロファイル（変更なし）
CREATE TABLE profiles (
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

-- 知識エントリー（source_file_id追加済み）
CREATE TABLE knowledge_entries (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    summary TEXT,
    source_type VARCHAR(50) CHECK(source_type IN ('meeting', 'memo', 'email', 'thought', 'transcription')),
    source_file_id INTEGER REFERENCES file_processing_status(id),  -- 追加
    related_profile_ids INTEGER[],
    extracted_info JSONB,
    tags TEXT[],
    file_path TEXT,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 学習パターン（変更なし）
CREATE TABLE learning_patterns (
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

-- 生成履歴（変更なし）
CREATE TABLE generation_history (
    id SERIAL PRIMARY KEY,
    output_type VARCHAR(50),
    target_profile_id INTEGER REFERENCES profiles(id),
    file_path TEXT,
    prompt_used TEXT,
    quality_score FLOAT,
    user_feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔧 Claude Code支援ツール

### scripts/file_utils.py
```python
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
        
    def list_input_files(self) -> List[Dict]:
        """inputディレクトリのファイル一覧を取得"""
        files = []
        
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
        self.conn = psycopg2.connect(
            "dbname=mirralism user=postgres password=mirralism"
        )
        
    def record_file_processing(self, file_info: Dict) -> int:
        """ファイル処理を記録"""
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
    """inputディレクトリの状態を取得"""
    file_utils = FileUtils()
    db_utils = DBUtils()
    
    files = file_utils.list_input_files()
    status = {
        'total_files': len(files),
        'files': []
    }
    
    for file in files:
        processed = db_utils.is_file_processed(file['path'])
        file['processed'] = processed is not None
        file['processed_info'] = processed
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
```

---

## 📝 必須ファイル内容（更新版）

### .claude/context.md（入力処理追加）
```markdown
# Claude Code 必須コンテキスト - MIRRALISM V5

## プロジェクトの目的
末武さんの知識とクライアント情報を蓄積し、末武さんらしい提案書等を自動生成する個人用ナレッジベース

## 絶対に守るルール
1. **見せかけの機能は作らない**（V4の失敗を繰り返さない）
2. **すべての機能は検証可能**でなければならない
3. **複雑さは価値に比例**させる
4. **Claude Codeが直接実行**（APIサーバーは使わない）
5. **入力ファイルは自動処理**（末武さんの手間を最小化）

## 本物の学習とは
- 固有名詞の間違いを記憶し、次回は間違えない
- 末武さんの文体を分析し、それを再現できる
- クライアントの特性を理解し、最適な提案ができる
- 使うたびに賢くなる

## 処理の基本フロー（v3.0）
1. 末武さんの指示を受ける
2. inputディレクトリを確認
3. ファイル内容を読んで理解
4. 文脈から適切な処理を判断
5. 必要に応じてスクリプトを活用
6. 成果物を適切な場所に保存
7. 学習すべき点を記録

## ディレクトリ構造
- input/: 解析待ちファイル
- archive/: 処理済みファイル（末武さんが手動移動）
- outputs/: 成果物（Obsidianで開く）
- data/profiles/: 人物情報
- scripts/: 実行スクリプト
- .notes/: プロジェクト情報

## 現在の実装状態
Phase: [1/2/3]
最新タスク: .notes/task_list.md 参照
```

### .claude/input_processing.md（新規）
```markdown
# 入力ファイル処理の指針

## Claude Codeとしての処理方針
inputディレクトリのファイルを処理する際は、以下の指針に従います：

### 1. 主体的な判断
- ファイルの内容を読んで理解する
- 文脈から最適な処理方法を判断
- 機械的な処理ではなく、知的な処理

### 2. 処理の優先順位
- 末武さんが明示的に指定したファイル
- 最近追加されたファイル
- 重要そうな内容のファイル

### 3. 情報抽出の観点
- 誰が関わっているか（人物・組織）
- 何が決まったか（決定事項）
- 何をすべきか（TODO・アクション）
- いつまでに（期限・スケジュール）
- なぜ重要か（背景・文脈）

### 4. 学習すべき点
- 新しい固有名詞
- 末武さんの表現パターン
- クライアントの特徴
- プロジェクトの文脈

### 5. 保存先の判断
- クライアント関連 → outputs/clients/[クライアント名]/
- 個人的な内容 → outputs/personal/
- 判断に迷う場合は末武さんに確認

## スクリプトの使い方
スクリプトは「自動処理」のためではなく、Claude Codeが必要に応じて使うツール：
- file_utils.py: ファイル操作の補助
- db_utils.py: データベース操作
- learn.py: 学習パターンの記録

主体はあくまでClaude Code自身です。
```

---

## 🚀 セットアップ手順（更新版）

```bash
# 1. プロジェクト作成
mkdir ~/MIRRALISM_V5
cd ~/MIRRALISM_V5

# 2. ディレクトリ構造作成（input/archive追加）
mkdir -p .claude .notes scripts data/{profiles,embeddings,patterns}
mkdir -p input/{meetings,emails,memos,documents} archive
mkdir -p outputs/{clients,personal}

# 3. Python環境
python3 -m venv venv
source venv/bin/activate

# 4. 必要なパッケージ
pip install psycopg2-binary chromadb sentence-transformers openai

# 5. PostgreSQL起動
docker run -d --name mirralism-db \
  -e POSTGRES_PASSWORD=mirralism \
  -p 5432:5432 \
  ankane/pgvector

# 6. データベース初期化（更新版）
psql -h localhost -U postgres -c "CREATE DATABASE mirralism;"
psql -h localhost -U postgres -d mirralism -f init.sql

# 7. 基本ファイル作成
echo "# MIRRALISM V5" > README.md
cp [この設計書の内容] .notes/project_overview.md

# 8. Claude Codeで動作確認
claude "プロジェクトを理解するため、以下を読んでください:
- .claude/context.md
- .claude/input_processing.md"

# 9. 初回スキャンテスト
claude "inputディレクトリをスキャンして、状態を教えてください"
```

---

## ✅ 実装チェックリスト（更新版）

### Phase 1: 基礎実装（2週間）
- [ ] ディレクトリ構造の作成（input/archive追加）
- [ ] PostgreSQLのセットアップ（file_processing_statusテーブル追加）
- [ ] file_utils.py の実装（Claude Code用補助ツール）
- [ ] 基本的なスクリプト作成（analyze.py, db_utils.py）
- [ ] プロファイル管理機能
- [ ] 知識エントリーの保存機能

### Phase 2: 学習機能（3週間）
- [ ] learn.py の完全実装
- [ ] パターン抽出ロジック
- [ ] 抽象化エンジン
- [ ] フィードバック処理
- [ ] 学習効果の測定
- [ ] 入力ファイルからの自動学習

### Phase 3: 生成機能（2週間）
- [ ] generate.py の実装
- [ ] 動的コンテンツ構成
- [ ] 文体分析・適用
- [ ] 品質評価機能
- [ ] 継続的改善の仕組み
- [ ] 入力ベースの自動生成提案

---

## 🎯 成功基準（更新版）

```yaml
定量的指標:
  処理品質:
    - 情報抽出の精度: 初月70% → 3ヶ月後90%
    - 文脈理解の深さ: 表面的 → 本質的理解へ
    - 処理時間: 1ファイル1-2分（品質優先）
    
  学習効果:
    - 固有名詞認識: 初回50% → 1ヶ月後90%
    - 文体再現度: 手直し箇所30% → 10%以下
    
  運用効率:
    - 末武さんの作業時間: 50%削減
    - 成果物の品質: 手直し不要率80%以上
    - 月額コスト: 1万円以内

検証方法:
  - 毎週の精度測定
  - 生成物の品質チェック
  - 作業時間の記録
  - フィードバックの分析
```

---

## 📌 重要な設計思想（v3.0）

1. **Claude Codeが主役**
   - スクリプトはツールに過ぎない
   - 判断と処理の主体はClaude Code
   - 機械的な自動化ではない

2. **知的な処理**
   - ファイルの内容を理解
   - 文脈に応じた適切な対応
   - 学習と改善の継続

3. **トレーサビリティ**
   - すべての処理を追跡可能
   - 入力と出力の関連が明確
   - 問題の原因を特定しやすく

4. **シンプルな運用**
   - ファイルを置く
   - Claude Codeに処理を依頼
   - 結果を確認
   - 満足したらアーカイブ

---

**この設計書は、V4の失敗から学び、真に価値のあるシステムを構築するための指針です。**
**v3.0では、inputディレクトリによる運用の簡素化と、Claude Codeの主体的な処理を両立させています。**

## 本設計の核心

**機械的な自動処理ではなく、Claude Codeが主体的に判断し処理することで、真の知的処理を実現します。**

スクリプトはあくまで「Claude Codeが使うツール」であり、処理の主体ではありません。これにより：
- 文脈に応じた柔軟な対応が可能
- 継続的な学習と改善が実現
- 見せかけではない本物の価値を提供
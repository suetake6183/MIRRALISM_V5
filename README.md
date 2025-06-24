# MIRRALISM V5

末武さんの個人用ナレッジベースシステム

## 概要
- 末武さんの知識とクライアント情報を蓄積
- Claude Codeが主体的にファイルを処理
- 末武さんらしい提案書等を生成

## ディレクトリ構造
```
MIRRALISM_V5/
├── input/          # 処理待ちファイル
├── outputs/        # 成果物（Obsidian用）
├── archive/        # 処理済みファイル
├── data/           # プロファイル等
├── scripts/        # 補助スクリプト
├── .claude/        # Claude設定
└── .notes/         # プロジェクト情報
```

## セットアップ状況
- [x] ディレクトリ構造作成
- [x] 基本設定ファイル作成
- [ ] PostgreSQL環境構築
- [ ] Python環境構築
- [ ] 基本スクリプト実装

## 使用方法
```bash
# ファイル処理
claude "inputディレクトリを確認し、新しいファイルを処理してください"

# 特定ファイル処理
claude "input/meetings/ファイル名 を処理してください"

# 提案書生成
claude "クライアントAへの提案書を作成してください"
```

## 技術スタック
- Python 3.11
- PostgreSQL + pgvector
- ChromaDB
- Claude Code

## 重要な原則
1. 見せかけの機能は作らない
2. Claude Codeが主体的に処理
3. 本物の学習機能を実装
4. 価値ある成果物を生成

実装開始: 2025年6月24日
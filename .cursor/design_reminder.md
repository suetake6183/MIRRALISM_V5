# MIRRALISM V5 設計リマインダー

## 基本原則

**MIRRALISM V5 = 対話型の知的補助システム**

### ✅ 正しい姿勢
- Claude Codeが必要に応じてツールを使用
- 判断と実行の主体は常にClaude Code
- スクリプトは情報提供・補助のみ

### ❌ 禁止事項
- 自動処理・自動実行システム
- バックグラウンド処理
- 機械的な判断・承認

## 確認方法

Claude Codeが必要に応じて使用：
```bash
python .cursor/simple_check.py scripts/ファイル名.py
```

## 設計思想確認

新しい機能を実装する前に自問：
1. これは私（Claude Code）が主体的に使うツールか？
2. 自動的に動作していないか？
3. 機械的に判断していないか？

**答えがすべて適切な場合のみ実装する** 
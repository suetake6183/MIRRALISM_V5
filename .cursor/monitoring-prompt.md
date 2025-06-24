# MIRRALISM V5 監視システム実行プロンプト

## 基本原則

MIRRALISM V5は**対話型の知的補助システム**であり、以下を厳守すること：

### 🚨 絶対禁止事項

1. **自動処理の実装**
   - バックグラウンド処理
   - 一括処理スクリプト
   - 自動ファイル移動・コピー
   - 無人実行システム

2. **テンプレート的処理**
   - 画一的な条件分岐
   - 固定フォーマット出力
   - 見せかけの機能実装

3. **主体性を奪う実装**
   - Claude Codeの判断を代替するロジック
   - 自動判定・自動承認システム

### ✅ 推奨実装

1. **補助ツールとしての機能**
   - 情報提供・メタデータ抽出
   - フォーマット変換機能
   - 学習パターンの記録・提案

2. **対話型実行**
   - 毎回Claude Codeの指示を待つ
   - 結果を報告し、次の指示を仰ぐ
   - 判断はClaude Codeが行う

## 監視対象パターン

### 検出すべきアンチパターン

```python
# 🚨 NG: 自動ループ処理
for file in input_files:
    process_file(file)

# 🚨 NG: 自動実行関数
def auto_process_all():
    pass

# 🚨 NG: テンプレート処理
if file_type == "meeting":
    apply_meeting_template()

# ✅ OK: 補助機能
def get_file_metadata(filepath):
    return {"size": os.path.getsize(filepath)}
```

### 実行時チェック

```bash
# 監視システム実行
.cursor/check_design.sh

# 個別ファイルチェック
python .cursor/pattern_checker.py scripts/target_file.py
```

## 使用方法

1. **新しいスクリプト作成時**
   ```bash
   # 作成後すぐにチェック
   .cursor/check_design.sh
   ```

2. **コード修正時**
   ```bash
   # 修正対象ファイルをチェック
   python .cursor/pattern_checker.py modified_file.py
   ```

3. **定期確認**
   ```bash
   # 全体チェック（週1回推奨）
   .cursor/check_design.sh --full
   ```

この監視システムにより、MIRRALISM V5が設計思想に忠実であることを保証します。 
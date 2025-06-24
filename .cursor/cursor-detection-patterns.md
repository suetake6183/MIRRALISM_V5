# Cursor用 設計違反検出パターン集

## 検出すべきアンチパターン

### 1. 自動処理パターン

```python
# 🚨 検出パターン 1: 自動ループ処理
pattern_auto_loop = r"for\s+.*\s+in\s+.*input.*:[\s\S]*?process|analyze|handle"

# 検出例：
for file in input_files:
    process_file(file)  # ❌ 自動処理

# 🚨 検出パターン 2: 自動実行関数
pattern_auto_func = r"def\s+(auto_|automatic|batch_|bulk_).*\(.*\):"

# 検出例：
def auto_process_all():  # ❌ 名前から自動処理が明らか
```

### 2. テンプレート処理パターン

```python
# 🚨 検出パターン 3: 画一的な条件分岐
pattern_template = r"if.*file_type.*==.*:[\s\S]*?template|fixed|standard"

# 検出例：
if file_type == "meeting":
    apply_meeting_template()  # ❌ テンプレート的

# 🚨 検出パターン 4: 固定フォーマット
pattern_fixed = r"format\s*=\s*['\"].*template.*['\"]"

# 検出例：
output_format = "standard_template_v1"  # ❌ 固定的
```

### 3. 見せかけ機能パターン

```python
# 🚨 検出パターン 5: 中身のない関数
pattern_fake = r"def\s+.*\(.*\):[\s]*?(pass|return\s+['\"].*['\"]|print)"

# 検出例：
def advanced_analysis():
    return "分析完了"  # ❌ 実際には何もしていない

# 🚨 検出パターン 6: ハードコードされた結果
pattern_hardcoded = r"return\s+['\"].*完了|成功|analyzed|processed.*['\"]"
```

### 4. Claude Code の主体性を奪うパターン

```python
# 🚨 検出パターン 7: 判断の自動化
pattern_decision = r"if.*:[\s\S]*?automatically|without.*confirmation"

# 検出例：
if score > 0.8:
    automatically_approve()  # ❌ Claude Codeの判断を奪う

# 🚨 検出パターン 8: 直接的なファイル処理
pattern_direct = r"(shutil|os)\.(copy|move|remove).*input.*outputs"

# 検出例：
shutil.copy(input_file, output_dir)  # ❌ 理解せずにコピー
```

## 推奨パターン（これらは問題なし）

### 1. ツールとしての実装

```python
# ✅ 良いパターン 1: 情報取得ツール
def get_file_metadata(filepath):
    """Claude Codeが判断に使う情報を提供"""
    return {
        'size': os.path.getsize(filepath),
        'modified': os.path.getmtime(filepath)
    }

# ✅ 良いパターン 2: 補助関数
def format_as_markdown(content, metadata):
    """Claude Codeの指示で使うフォーマッタ"""
    # Claude Codeが内容を理解した上で使う
```

### 2. 学習機能の実装

```python
# ✅ 良いパターン 3: 実際の学習
def record_correction(original, corrected, context):
    """間違いを記録し、次回適用"""
    db.save_pattern(original, corrected, context)
    return f"学習しました: {original} → {corrected}"

# ✅ 良いパターン 4: パターンの適用
def apply_learned_patterns(text):
    """学習済みパターンを適用（Claude Code経由）"""
    patterns = db.get_patterns()
    suggestions = []
    # 提案を返すだけで、自動適用はしない
```

## Cursor での実装例

### .cursor/pattern_checker.py

```python
import re
import ast

class DesignViolationDetector:
    """設計違反を検出するクラス"""
    
    def __init__(self):
        self.violations = []
        self.anti_patterns = {
            'auto_loop': r"for\s+.*\s+in\s+.*input.*:[\s\S]*?process",
            'auto_function': r"def\s+(auto_|automatic).*\(.*\):",
            'template': r"template|fixed_format|standard_output",
            'fake_function': r"def\s+.*\(.*\):[\s]*?(pass|return\s+['\"])",
            'direct_process': r"shutil\.(copy|move).*input.*output"
        }
    
    def check_file(self, filepath):
        """ファイルをチェック"""
        with open(filepath, 'r') as f:
            content = f.read()
        
        # アンチパターンを検出
        for name, pattern in self.anti_patterns.items():
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                self.violations.append({
                    'file': filepath,
                    'pattern': name,
                    'line': content[:match.start()].count('\n') + 1,
                    'code': match.group(0)
                })
        
        return self.violations
    
    def generate_report(self):
        """違反レポートを生成"""
        if not self.violations:
            return "✅ 設計違反は検出されませんでした"
        
        report = "🚨 設計違反を検出しました:\n\n"
        for v in self.violations:
            report += f"ファイル: {v['file']}:{v['line']}\n"
            report += f"パターン: {v['pattern']}\n"
            report += f"該当コード: {v['code']}\n"
            report += "推奨: Claude Codeが主体的に判断する実装に変更\n\n"
        
        return report
```

### 使用方法

```python
# Cursorのターミナルで実行
detector = DesignViolationDetector()
detector.check_file('scripts/new_script.py')
print(detector.generate_report())
```

## 定期実行スクリプト

```bash
#!/bin/bash
# .cursor/check_design.sh

echo "🔍 MIRRALISM V5 設計適合性チェック"
echo "================================"

# Pythonスクリプトをチェック
for file in scripts/*.py; do
    echo "Checking: $file"
    python .cursor/pattern_checker.py "$file"
done

# 結果をレポート
if [ -f violations.log ]; then
    echo "⚠️ 設計違反が見つかりました。violations.log を確認してください。"
else
    echo "✅ すべてのファイルが設計に準拠しています。"
fi
```

これらのパターンを使用することで、Cursorは設計違反を自動的に検出し、
MIRRALISM V5が常に設計思想に忠実であることを保証できます。
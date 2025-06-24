# Cursor実装指示書 - MIRRALISM V5監視システム構築

## Cursorへの指示

以下の手順で、MIRRALISM V5の設計監視システムを構築してください。

### ステップ1: ディレクトリとファイルの作成

```bash
# プロジェクトルートで実行
cd ~/MIRRALISM_V5

# .cursorディレクトリを作成
mkdir -p .cursor

# 監視システムの基本ファイルを作成してください
```

### ステップ2: monitoring-prompt.md の作成

`.cursor/monitoring-prompt.md` を以下の内容で作成：

```markdown
# MIRRALISM V5 実装監視ガイド for Cursor

## あなたの役割

あなたはMIRRALISM V5プロジェクトの「設計監視者」として、Claude Codeの実装が設計書v3.0の思想に忠実であることを確認します。

## 監視対象ディレクトリ

- input/        # ファイル処理の起点
- scripts/      # ツールスクリプト（自動処理ではない）
- outputs/      # 成果物
- .claude/      # 運用ルール
- .notes/       # プロジェクト情報

## 設計書の核心（必ず理解すること）

### 最重要原則
- 見せかけの機能は作らない
- Claude Codeが内容を理解して処理
- 機械的な自動処理ではない
- スクリプトは単なるツール

### V4の失敗から学ぶ
- 失敗: 複雑な自動処理システムを作ったが、実際には機能しなかった
- 教訓: シンプルに、Claude Codeが主体となる設計

## RED FLAGS（即座に指摘すべき）

1. 自動処理スクリプトの作成
   - for file in input_files: process_automatically(file)
   - 指摘: 「機械的な自動処理です。Claude Codeが主体的に判断すべきです」

2. テンプレート的な処理
   - if file_type == "meeting": apply_meeting_template()
   - 指摘: 「内容を理解してから処理してください」

3. 見せかけの機能
   - def advanced_ai_analysis(): return "AIが分析しました"
   - 指摘: 「実際に動作する機能を実装してください」

## GOOD PATTERNS（推奨すべき）

1. Claude Codeが判断する実装
   - 情報取得ツールの提供
   - Claude Codeが判断に使う

2. 学習機能の実装
   - 間違いを記録し、次回から正しく処理
   - 実際にDBに保存

3. 柔軟な処理
   - 文脈から適切な処理を判断

## 指摘の仕方

設計違反を見つけたとき：
⚠️ 設計違反の可能性
該当箇所: [ファイル名:行番号]
問題: [具体的な問題]
理由: 設計書v3.0では「[該当する原則]」とされています
修正案: [具体的な改善案]

良い実装を見つけたとき：
✅ 設計に忠実な実装
該当箇所: [ファイル名:行番号]
良い点: [具体的な良い点]
```

### ステップ3: pattern_checker.py の作成

`.cursor/pattern_checker.py` を以下の内容で作成：

```python
#!/usr/bin/env python3
"""
MIRRALISM V5 設計違反検出ツール
"""

import re
import os
import sys
from pathlib import Path
from datetime import datetime

class DesignViolationDetector:
    """設計違反を検出するクラス"""
    
    def __init__(self):
        self.violations = []
        self.warnings = []
        
        # アンチパターンの定義
        self.anti_patterns = {
            'auto_loop': {
                'pattern': r'for\s+\w+\s+in\s+.*input.*:[\s\S]*?(process|analyze|handle)',
                'message': '自動ループ処理を検出。Claude Codeが主体的に処理すべきです。'
            },
            'auto_function': {
                'pattern': r'def\s+(auto_|automatic|batch_|bulk_)\w*\s*\(.*\):',
                'message': '自動処理関数を検出。関数名から自動処理が示唆されます。'
            },
            'template_processing': {
                'pattern': r'if.*file_type.*==.*:[\s\S]*?(template|fixed|standard)',
                'message': 'テンプレート的な処理を検出。画一的な処理は避けてください。'
            },
            'fake_function': {
                'pattern': r'def\s+\w+\s*\(.*\):\s*\n\s*(pass|return\s+["\'].*["\'])',
                'message': '中身のない関数を検出。実際に動作する機能を実装してください。'
            },
            'direct_file_operation': {
                'pattern': r'(shutil|os)\.(copy|move|remove).*input.*output',
                'message': '直接的なファイル操作を検出。内容を理解してから処理してください。'
            },
            'hardcoded_result': {
                'pattern': r'return\s+["\'].*(?:完了|成功|analyzed|processed).*["\']',
                'message': 'ハードコードされた結果を検出。実際の処理結果を返してください。'
            }
        }
        
        # 推奨パターンの定義
        self.good_patterns = {
            'tool_function': {
                'pattern': r'def\s+get_\w+|def\s+\w+_utils?|""".*Claude Code.*"""',
                'message': 'ツール関数として適切に実装されています。'
            },
            'learning_function': {
                'pattern': r'def\s+\w*learn\w*|record.*correction|save.*pattern',
                'message': '学習機能が実装されています。'
            }
        }
    
    def check_file(self, filepath):
        """ファイルをチェック"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return
        
        lines = content.split('\n')
        
        # アンチパターンを検出
        for name, config in self.anti_patterns.items():
            matches = re.finditer(config['pattern'], content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                self.violations.append({
                    'file': filepath,
                    'pattern': name,
                    'line': line_num,
                    'code': match.group(0)[:100],  # 最初の100文字
                    'message': config['message']
                })
        
        # 推奨パターンを検出
        for name, config in self.good_patterns.items():
            if re.search(config['pattern'], content, re.MULTILINE | re.IGNORECASE):
                self.warnings.append({
                    'file': filepath,
                    'pattern': name,
                    'message': config['message']
                })
    
    def check_directory(self, directory='.'):
        """ディレクトリ内のPythonファイルをチェック"""
        for root, dirs, files in os.walk(directory):
            # .cursorディレクトリ自身はスキップ
            if '.cursor' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    self.check_file(filepath)
    
    def generate_report(self):
        """違反レポートを生成"""
        report = f"\n{'='*60}\n"
        report += f"MIRRALISM V5 設計適合性チェックレポート\n"
        report += f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"{'='*60}\n\n"
        
        if not self.violations:
            report += "✅ 設計違反は検出されませんでした。\n\n"
        else:
            report += f"🚨 {len(self.violations)}件の設計違反を検出しました:\n\n"
            for i, v in enumerate(self.violations, 1):
                report += f"{i}. {v['file']}:{v['line']}\n"
                report += f"   パターン: {v['pattern']}\n"
                report += f"   該当コード: {v['code']}\n"
                report += f"   問題: {v['message']}\n\n"
        
        if self.warnings:
            report += "💡 推奨パターンの使用:\n\n"
            for w in self.warnings:
                report += f"✅ {w['file']}: {w['message']}\n"
        
        report += f"\n{'='*60}\n"
        return report
    
    def save_report(self, filename='design_check_report.txt'):
        """レポートをファイルに保存"""
        report = self.generate_report()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        return filename

def main():
    """メイン処理"""
    detector = DesignViolationDetector()
    
    # 引数でディレクトリを指定可能
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    print(f"Checking directory: {directory}")
    detector.check_directory(directory)
    
    # レポートを表示
    print(detector.generate_report())
    
    # レポートを保存
    if detector.violations:
        filename = detector.save_report()
        print(f"レポートを {filename} に保存しました。")

if __name__ == "__main__":
    main()
```

### ステップ4: monitoring_rules.md の作成

`.cursor/monitoring_rules.md` を以下の内容で作成：

```markdown
# MIRRALISM V5 監視ルール

## 自動チェック項目
1. scripts/内の新規ファイル → 自動処理でないか確認
2. "auto_"で始まる関数名 → 要注意
3. "template"を含む処理 → 画一的でないか確認
4. inputディレクトリの直接操作 → Claude Code経由か確認

## 監視スケジュール
- ファイル保存時: 即時チェック
- 日次: 全体スキャン
- 週次: 詳細レポート生成

## 設計書の場所
- .notes/mirralism-v5-design-doc.md（必読）
- 特に「本設計の核心」セクション

## 違反レベル
- 🚨 Critical: 自動処理、見せかけ機能
- ⚠️ Warning: テンプレート的処理
- 💡 Info: 改善可能な箇所
```

### ステップ5: check_design.sh の作成

`.cursor/check_design.sh` を以下の内容で作成し、実行権限を付与：

```bash
#!/bin/bash

echo "🔍 MIRRALISM V5 設計適合性チェック"
echo "================================"
echo ""

# Python環境をアクティベート（必要な場合）
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# pattern_checker.pyを実行
python .cursor/pattern_checker.py

# 結果に応じてアクション
if [ -f "design_check_report.txt" ]; then
    echo ""
    echo "詳細なレポートは design_check_report.txt を確認してください。"
fi
```

実行権限を付与：
```bash
chmod +x .cursor/check_design.sh
```

### ステップ6: Cursorへの初期設定

Cursorを開いて、以下を実行してください：

1. プロジェクトを開く
```bash
cd ~/MIRRALISM_V5
cursor .
```

2. 以下のメッセージをCursorに送る：
```
MIRRALISM V5の設計監視者として設定します。

1. まず .notes/mirralism-v5-design-doc.md を読んで、設計思想を理解してください
2. 次に .cursor/monitoring-prompt.md を読んで、監視ルールを理解してください
3. .cursor/pattern_checker.py を使って定期的に設計チェックを行ってください

あなたの役割：
- Claude Codeの実装を監視
- 設計違反を検出したら指摘
- 良い実装パターンを推奨
- V4の失敗を繰り返させない

ファイルが変更されたら、設計に準拠しているか確認してください。
```

### ステップ7: 動作確認

```bash
# 監視システムのテスト
cd ~/MIRRALISM_V5
./.cursor/check_design.sh

# 結果を確認
cat design_check_report.txt
```

## 使用方法

1. **定期チェック**
   ```bash
   ./.cursor/check_design.sh
   ```

2. **特定ディレクトリのチェック**
   ```bash
   python .cursor/pattern_checker.py scripts/
   ```

3. **Cursorでの常時監視**
   - ファイル保存時に自動実行される
   - 設計違反があれば即座に警告

これで監視システムの構築が完了します。
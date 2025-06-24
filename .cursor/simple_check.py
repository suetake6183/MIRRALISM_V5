#!/usr/bin/env python3
"""
MIRRALISM V5 設計確認ツール
Claude Codeが必要に応じて使用する補助ツール
"""

import sys
import re
from pathlib import Path

def check_file_compliance(filepath):
    """Claude Codeが指定したファイルの設計適合性を確認"""
    if not Path(filepath).exists():
        return {"error": f"ファイルが見つかりません: {filepath}"}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 最小限の重要パターンのみチェック
    critical_patterns = {
        'auto_processing': r'for\s+.*\s+in\s+.*input.*:\s*\n.*process',
        'background_thread': r'threading\.|multiprocessing\.',
        'automatic_execution': r'def\s+auto_.*\(',
    }
    
    violations = []
    for name, pattern in critical_patterns.items():
        if re.search(pattern, content, re.MULTILINE):
            violations.append(name)
    
    return {
        'file': filepath,
        'violations': violations,
        'compliant': len(violations) == 0
    }

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python simple_check.py ファイルパス")
        sys.exit(1)
    
    result = check_file_compliance(sys.argv[1])
    
    if result.get('compliant', False):
        print("✅ 設計適合")
    else:
        print("⚠️ 確認が必要な箇所があります")
        for violation in result.get('violations', []):
            print(f"  - {violation}") 
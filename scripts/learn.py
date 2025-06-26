#!/usr/bin/env python3
"""
学習機能スクリプト
Claude Codeが使う学習パターン記録・適用ツール
"""

import sys
import json
from datetime import datetime
from typing import Dict, List, Optional
from db_utils import MirralismDB

class LearningEngine:
    """学習エンジン"""
    
    def __init__(self):
        self.db = MirralismDB()
    
    def record_correction(self, original: str, corrected: str, context: str = None, 
                         pattern_type: str = "correction") -> bool:
        """修正パターンを記録"""
        if not self.db.conn:
            print("データベースに接続できません。学習機能は無効です。")
            return False
        
        try:
            with self.db.conn.cursor() as cur:
                # 既存のパターンを確認
                cur.execute("""
                    SELECT id, usage_count, success_count FROM learning_patterns
                    WHERE pattern_type = %s AND original_text = %s AND corrected_text = %s
                """, (pattern_type, original, corrected))
                
                existing = cur.fetchone()
                
                if existing:
                    # 既存パターンの使用回数を更新
                    cur.execute("""
                        UPDATE learning_patterns 
                        SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (existing[0],))
                else:
                    # 新しいパターンを追加
                    cur.execute("""
                        INSERT INTO learning_patterns 
                        (pattern_type, original_text, corrected_text, context, usage_count)
                        VALUES (%s, %s, %s, %s, 1)
                    """, (pattern_type, original, corrected, context))
                
                self.db.conn.commit()
                return True
                
        except Exception as e:
            print(f"学習記録エラー: {e}")
            return False
    
    def get_correction_suggestions(self, text: str, pattern_type: str = None) -> List[Dict]:
        """修正提案を取得"""
        if not self.db.conn:
            return []
        
        try:
            with self.db.conn.cursor() as cur:
                if pattern_type:
                    cur.execute("""
                        SELECT original_text, corrected_text, confidence, usage_count, context
                        FROM learning_patterns
                        WHERE pattern_type = %s AND %s LIKE CONCAT('%%', original_text, '%%')
                        ORDER BY confidence DESC, usage_count DESC
                    """, (pattern_type, text))
                else:
                    cur.execute("""
                        SELECT original_text, corrected_text, confidence, usage_count, context
                        FROM learning_patterns
                        WHERE %s LIKE CONCAT('%%', original_text, '%%')
                        ORDER BY confidence DESC, usage_count DESC
                    """, (text,))
                
                columns = ['original', 'corrected', 'confidence', 'usage_count', 'context']
                return [dict(zip(columns, row)) for row in cur.fetchall()]
                
        except Exception as e:
            print(f"修正提案取得エラー: {e}")
            return []
    
    def record_successful_application(self, original: str, corrected: str):
        """パターン適用成功を記録"""
        if not self.db.conn:
            return
        
        try:
            with self.db.conn.cursor() as cur:
                cur.execute("""
                    UPDATE learning_patterns 
                    SET success_count = success_count + 1,
                        confidence = LEAST(1.0, confidence + 0.1),
                        last_used = CURRENT_TIMESTAMP
                    WHERE original_text = %s AND corrected_text = %s
                """, (original, corrected))
                self.db.conn.commit()
                
        except Exception as e:
            print(f"成功記録エラー: {e}")
    
    def get_learning_stats(self) -> Dict:
        """学習統計を取得"""
        if not self.db.conn:
            return {}
        
        try:
            with self.db.conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        pattern_type,
                        COUNT(*) as pattern_count,
                        SUM(usage_count) as total_usage,
                        AVG(confidence) as avg_confidence
                    FROM learning_patterns
                    GROUP BY pattern_type
                    ORDER BY pattern_count DESC
                """)
                
                stats = {}
                for row in cur.fetchall():
                    stats[row[0]] = {
                        'pattern_count': row[1],
                        'total_usage': row[2],
                        'avg_confidence': float(row[3]) if row[3] else 0.0
                    }
                
                return stats
                
        except Exception as e:
            print(f"統計取得エラー: {e}")
            return {}
    
    def apply_learned_corrections(self, text: str) -> str:
        """学習した修正パターンを適用"""
        suggestions = self.get_correction_suggestions(text)
        
        corrected_text = text
        applied_corrections = []
        
        for suggestion in suggestions:
            if suggestion['confidence'] > 0.7:  # 高信頼度のパターンのみ適用
                if suggestion['original'] in corrected_text:
                    corrected_text = corrected_text.replace(
                        suggestion['original'], 
                        suggestion['corrected']
                    )
                    applied_corrections.append(suggestion)
        
        return corrected_text, applied_corrections

def main():
    """コマンドライン実行用メイン関数"""
    if len(sys.argv) < 2:
        print("使い方:")
        print("  python learn.py record <original> <corrected> [context]")
        print("  python learn.py suggest <text>")
        print("  python learn.py stats")
        print("  python learn.py apply <text>")
        return
    
    command = sys.argv[1]
    engine = LearningEngine()
    
    if command == "record":
        if len(sys.argv) < 4:
            print("エラー: original と corrected が必要です")
            return
        
        original = sys.argv[2]
        corrected = sys.argv[3]
        context = sys.argv[4] if len(sys.argv) > 4 else None
        
        result = engine.record_correction(original, corrected, context)
        if result:
            print(f"学習記録: '{original}' → '{corrected}'")
    
    elif command == "suggest":
        if len(sys.argv) < 3:
            print("エラー: text が必要です")
            return
        
        text = sys.argv[2]
        suggestions = engine.get_correction_suggestions(text)
        
        if suggestions:
            print("修正提案:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"{i}. '{suggestion['original']}' → '{suggestion['corrected']}' "
                      f"(信頼度: {suggestion['confidence']:.2f})")
        else:
            print("修正提案はありません")
    
    elif command == "stats":
        stats = engine.get_learning_stats()
        
        if stats:
            print("学習統計:")
            for pattern_type, data in stats.items():
                print(f"  {pattern_type}: {data['pattern_count']}パターン, "
                      f"使用回数: {data['total_usage']}, "
                      f"平均信頼度: {data['avg_confidence']:.2f}")
        else:
            print("学習データがありません")
    
    elif command == "apply":
        if len(sys.argv) < 3:
            print("エラー: text が必要です")
            return
        
        text = sys.argv[2]
        corrected_text, applied = engine.apply_learned_corrections(text)
        
        print(f"元のテキスト: {text}")
        print(f"修正後: {corrected_text}")
        
        if applied:
            print("適用した修正:")
            for correction in applied:
                print(f"  '{correction['original']}' → '{correction['corrected']}'")
    
    else:
        print(f"不明なコマンド: {command}")

if __name__ == "__main__":
    main()
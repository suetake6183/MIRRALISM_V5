#!/usr/bin/env python3
"""
データ分析補助スクリプト
Claude Codeが使うデータ分析・文脈理解ツール
"""

import json
import re
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import hashlib

class ContentAnalyzer:
    """コンテンツ分析クラス"""
    
    def __init__(self):
        self.patterns = {
            'date': [
                r'(\d{4})年(\d{1,2})月(\d{1,2})日',
                r'(\d{4})-(\d{1,2})-(\d{1,2})',
                r'(\d{1,2})/(\d{1,2})/(\d{4})'
            ],
            'time': [
                r'(\d{1,2}):(\d{2})',
                r'(\d{1,2})時(\d{1,2})分'
            ],
            'person': [
                r'([一-龯]{2,4})さん',
                r'([一-龯]{2,4})部長',
                r'([一-龯]{2,4})課長',
                r'([一-龯]{2,4})主任'
            ],
            'company': [
                r'([一-龯A-Za-z0-9]{2,20})(株式会社|有限会社|合同会社)',
                r'(株式会社|有限会社|合同会社)([一-龯A-Za-z0-9]{2,20})'
            ],
            'money': [
                r'(\d{1,4})万円',
                r'(\d{1,4})億円',
                r'¥([\d,]+)',
                r'(\d{1,4})千円'
            ],
            'deadline': [
                r'(\d{1,2})月末まで',
                r'来週末',
                r'今月中',
                r'(\d{1,2})日まで'
            ]
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """エンティティを抽出"""
        entities = {}
        
        for entity_type, patterns in self.patterns.items():
            entities[entity_type] = []
            
            for pattern in patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    if isinstance(match, tuple):
                        # 複数グループのマッチ
                        if entity_type == 'date':
                            entities[entity_type].append(f"{match[0]}/{match[1]}/{match[2]}")
                        elif entity_type == 'time':
                            entities[entity_type].append(f"{match[0]}:{match[1]}")
                        else:
                            entities[entity_type].append(' '.join(match))
                    else:
                        entities[entity_type].append(match)
        
        # 重複を除去
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    def analyze_meeting_content(self, content: str) -> Dict:
        """会議録を分析"""
        analysis = {
            'type': 'meeting',
            'entities': self.extract_entities(content),
            'key_points': [],
            'decisions': [],
            'action_items': [],
            'participants': [],
            'topics': []
        }
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 決定事項を検出
            if any(keyword in line for keyword in ['決定', '決まった', '合意', '承認']):
                analysis['decisions'].append(line)
            
            # アクションアイテムを検出
            if any(keyword in line for keyword in ['TODO', 'アクション', '宿題', '〜する', '〜します']):
                analysis['action_items'].append(line)
            
            # 重要なポイントを検出
            if any(keyword in line for keyword in ['重要', '課題', '問題', 'リスク', '提案']):
                analysis['key_points'].append(line)
        
        # 参加者を抽出（人名パターンから）
        analysis['participants'] = analysis['entities'].get('person', [])
        
        return analysis
    
    def analyze_email_content(self, content: str) -> Dict:
        """メール内容を分析"""
        analysis = {
            'type': 'email',
            'entities': self.extract_entities(content),
            'sender': None,
            'recipients': [],
            'subject': None,
            'key_points': [],
            'urgency': 'normal'
        }
        
        lines = content.split('\n')
        
        # メールヘッダーを解析
        for line in lines[:10]:  # 最初の10行でヘッダーを探す
            if line.startswith('From:') or line.startswith('送信者:'):
                analysis['sender'] = line.split(':', 1)[1].strip()
            elif line.startswith('Subject:') or line.startswith('件名:'):
                analysis['subject'] = line.split(':', 1)[1].strip()
            elif line.startswith('To:') or line.startswith('宛先:'):
                analysis['recipients'] = [r.strip() for r in line.split(':', 1)[1].split(',')]
        
        # 緊急度を判定
        urgent_keywords = ['至急', '緊急', '急ぎ', 'URGENT', '今日中', '明日まで']
        if any(keyword in content for keyword in urgent_keywords):
            analysis['urgency'] = 'high'
        
        return analysis
    
    def analyze_memo_content(self, content: str) -> Dict:
        """メモ内容を分析"""
        analysis = {
            'type': 'memo',
            'entities': self.extract_entities(content),
            'topics': [],
            'ideas': [],
            'references': []
        }
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # アイデアを検出
            if any(keyword in line for keyword in ['アイデア', '案', '提案', '考え', '思いつき']):
                analysis['ideas'].append(line)
            
            # 参考情報を検出
            if any(keyword in line for keyword in ['参考', '引用', '出典', 'URL', 'http']):
                analysis['references'].append(line)
        
        return analysis
    
    def detect_file_type(self, filename: str, content: str) -> str:
        """ファイルタイプを検出"""
        filename_lower = filename.lower()
        
        # ファイル名から判定
        if any(keyword in filename_lower for keyword in ['meeting', '会議', 'mtg']):
            return 'meeting'
        elif any(keyword in filename_lower for keyword in ['email', 'mail', 'メール']):
            return 'email'
        elif any(keyword in filename_lower for keyword in ['memo', 'メモ', 'note']):
            return 'memo'
        elif any(keyword in filename_lower for keyword in ['doc', '文書', 'document']):
            return 'document'
        
        # 内容から判定
        if any(keyword in content for keyword in ['議事録', '会議録', '打ち合わせ', 'ミーティング']):
            return 'meeting'
        elif any(keyword in content for keyword in ['From:', 'Subject:', '送信者:', '件名:']):
            return 'email'
        elif len(content.split('\n')) < 10 and not any(keyword in content for keyword in ['です', 'である']):
            return 'memo'
        
        return 'document'
    
    def generate_summary(self, analysis: Dict) -> str:
        """分析結果からサマリーを生成"""
        content_type = analysis.get('type', 'unknown')
        
        if content_type == 'meeting':
            summary_parts = []
            
            if analysis.get('participants'):
                summary_parts.append(f"参加者: {', '.join(analysis['participants'])}")
            
            if analysis.get('decisions'):
                summary_parts.append(f"決定事項: {len(analysis['decisions'])}件")
            
            if analysis.get('action_items'):
                summary_parts.append(f"アクション項目: {len(analysis['action_items'])}件")
            
            dates = analysis.get('entities', {}).get('date', [])
            if dates:
                summary_parts.append(f"開催日: {dates[0]}")
            
            return " | ".join(summary_parts)
        
        elif content_type == 'email':
            summary_parts = []
            
            if analysis.get('sender'):
                summary_parts.append(f"送信者: {analysis['sender']}")
            
            if analysis.get('subject'):
                summary_parts.append(f"件名: {analysis['subject']}")
            
            if analysis.get('urgency') == 'high':
                summary_parts.append("【緊急】")
            
            return " | ".join(summary_parts)
        
        else:
            # 汎用サマリー
            entities = analysis.get('entities', {})
            summary_parts = []
            
            for entity_type, values in entities.items():
                if values:
                    summary_parts.append(f"{entity_type}: {len(values)}件")
            
            return " | ".join(summary_parts) or "分析データなし"

def analyze_file(file_path: str) -> Dict:
    """ファイルを分析"""
    analyzer = ContentAnalyzer()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'error': f"ファイル読み込みエラー: {e}"}
    
    filename = Path(file_path).name
    file_type = analyzer.detect_file_type(filename, content)
    
    if file_type == 'meeting':
        analysis = analyzer.analyze_meeting_content(content)
    elif file_type == 'email':
        analysis = analyzer.analyze_email_content(content)
    elif file_type == 'memo':
        analysis = analyzer.analyze_memo_content(content)
    else:
        # 汎用分析
        analysis = {
            'type': file_type,
            'entities': analyzer.extract_entities(content)
        }
    
    analysis['filename'] = filename
    analysis['file_size'] = len(content)
    analysis['summary'] = analyzer.generate_summary(analysis)
    
    return analysis

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使い方: python analyze.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    result = analyze_file(file_path)
    
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
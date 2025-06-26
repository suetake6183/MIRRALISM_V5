#!/usr/bin/env python3
"""
コンテンツ生成補助スクリプト
Claude Codeが使う提案書・記事生成ツール
"""

import json
import sys
from datetime import datetime, date
from typing import Dict, List, Optional
from pathlib import Path
from db_utils import MirralismDB

class ContentGenerator:
    """コンテンツ生成クラス"""
    
    def __init__(self):
        self.db = MirralismDB()
        self.templates = {
            'proposal': self._load_proposal_template(),
            'meeting_summary': self._load_meeting_template(),
            'blog_post': self._load_blog_template()
        }
    
    def _load_proposal_template(self) -> str:
        """提案書テンプレート"""
        return """# {title}

## 1. はじめに
{introduction}

## 2. 現状の課題
{current_issues}

## 3. ご提案内容
{proposal_content}

### 3.1 アプローチ
{approach}

### 3.2 期待効果
{expected_results}

## 4. 投資対効果
{roi_analysis}

## 5. スケジュール
{schedule}

## 6. 実績
{track_record}

## 7. おわりに
{conclusion}

---
{date}
{author_info}
"""
    
    def _load_meeting_template(self) -> str:
        """会議録テンプレート"""
        return """# {title}

## 概要
- **日時**: {datetime}
- **場所**: {location}
- **議題**: {agenda}

## 参加者
{participants}

## 議論内容
{discussion}

## 決定事項
{decisions}

## アクション項目
{action_items}

## 次回予定
{next_meeting}

---
*作成日: {created_date}*
"""
    
    def _load_blog_template(self) -> str:
        """ブログ記事テンプレート"""
        return """# {title}

{introduction}

## {section1_title}
{section1_content}

## {section2_title}
{section2_content}

## {section3_title}
{section3_content}

## まとめ
{conclusion}

---
*投稿日: {publish_date}*
"""
    
    def get_client_context(self, client_name: str) -> Dict:
        """クライアント文脈を取得"""
        profiles = self.db.get_profiles('client')
        client_profile = None
        
        for profile in profiles:
            if client_name.lower() in profile['name'].lower():
                client_profile = profile
                break
        
        if not client_profile:
            return {}
        
        # 関連する知識エントリーを取得
        knowledge_entries = self.db.get_knowledge_entries(client_profile['id'])
        
        return {
            'profile': client_profile,
            'recent_interactions': knowledge_entries[:5],
            'characteristics': client_profile.get('characteristics', {}),
            'organization': client_profile.get('organization', '')
        }
    
    def generate_proposal(self, client_name: str, topic: str, 
                         meeting_insights: List[Dict] = None) -> str:
        """提案書を生成"""
        client_context = self.get_client_context(client_name)
        
        # 基本情報
        variables = {
            'title': f'{topic}のご提案',
            'date': datetime.now().strftime('%Y年%m月%d日'),  # システム日付を自動取得
            'author_info': '株式会社末武コンサルティング\n末武修平'
        }
        
        # クライアント固有の内容を生成
        if client_context:
            profile = client_context['profile']
            characteristics = client_context.get('characteristics', {})
            
            # 導入部
            variables['introduction'] = f"""この度は、{profile['organization']}様の{topic}についてご相談いただき、誠にありがとうございます。

先日のお打ち合わせでお伺いした内容を踏まえ、{profile['organization']}様に最適なソリューションをご提案させていただきます。"""
            
            # 現状課題（会議録から抽出）
            if meeting_insights:
                issues = []
                for insight in meeting_insights:
                    if 'key_points' in insight:
                        issues.extend(insight['key_points'])
                variables['current_issues'] = '\n'.join([f"- {issue}" for issue in issues[:5]])
            else:
                variables['current_issues'] = "（具体的な課題をここに記載）"
            
            # アプローチ（末武さんの特徴的なアプローチを反映）
            variables['approach'] = """リスクを最小化しながら、確実に効果を実感いただけるよう、段階的な導入をご提案いたします。

これにより：
- 初期投資を抑制できます
- 効果を確認しながら進められます
- リスクを最小化できます"""
            
        else:
            # デフォルトの内容
            variables.update({
                'introduction': 'この度は貴重なお時間をいただき、誠にありがとうございます。',
                'current_issues': '（現状の課題を記載）',
                'approach': '（アプローチを記載）'
            })
        
        # その他のデフォルト値
        variables.update({
            'proposal_content': '（提案内容の詳細）',
            'expected_results': '（期待される効果）',
            'roi_analysis': '（投資対効果の分析）',
            'schedule': '（実施スケジュール）',
            'track_record': '（関連する実績）',
            'conclusion': '（結びの言葉）'
        })
        
        return self.templates['proposal'].format(**variables)
    
    def generate_meeting_summary(self, meeting_data: Dict) -> str:
        """会議サマリーを生成"""
        # 会議データから情報を抽出
        variables = {
            'title': meeting_data.get('title', '会議録'),
            'datetime': meeting_data.get('datetime', '[会議開催日時を確認してください]'),
            'location': meeting_data.get('location', '未記載'),
            'agenda': meeting_data.get('agenda', '未記載'),
            'created_date': datetime.now().strftime('%Y年%m月%d日')  # システム日付を自動取得
        }
        
        # 参加者
        participants = meeting_data.get('participants', [])
        if participants:
            variables['participants'] = '\n'.join([f"- {p}" for p in participants])
        else:
            variables['participants'] = '（参加者情報なし）'
        
        # 議論内容
        discussion = meeting_data.get('discussion', [])
        if discussion:
            variables['discussion'] = '\n'.join(discussion)
        else:
            variables['discussion'] = '（議論内容なし）'
        
        # 決定事項
        decisions = meeting_data.get('decisions', [])
        if decisions:
            variables['decisions'] = '\n'.join([f"- {d}" for d in decisions])
        else:
            variables['decisions'] = '（決定事項なし）'
        
        # アクション項目
        action_items = meeting_data.get('action_items', [])
        if action_items:
            variables['action_items'] = '\n'.join([f"- {a}" for a in action_items])
        else:
            variables['action_items'] = '（アクション項目なし）'
        
        variables['next_meeting'] = meeting_data.get('next_meeting', '未定')
        
        return self.templates['meeting_summary'].format(**variables)
    
    def generate_blog_post(self, title: str, topic: str, insights: List[str] = None) -> str:
        """ブログ記事を生成"""
        variables = {
            'title': title,
            'publish_date': datetime.now().strftime('%Y年%m月%d日'),  # システム日付を自動取得
            'introduction': f'{topic}について考察します。',
            'section1_title': '背景',
            'section1_content': '（背景の説明）',
            'section2_title': '現状分析',
            'section2_content': '（現状の分析）',
            'section3_title': '今後の展望',
            'section3_content': '（将来的な展望）',
            'conclusion': '（まとめの内容）'
        }
        
        return self.templates['blog_post'].format(**variables)
    
    def get_suetake_style_patterns(self) -> Dict:
        """末武さんの文体パターンを取得"""
        if not self.db.conn:
            return {}
        
        try:
            with self.db.conn.cursor() as cur:
                cur.execute("""
                    SELECT corrected_text, context, confidence 
                    FROM learning_patterns 
                    WHERE pattern_type = 'writing_style'
                    ORDER BY confidence DESC, usage_count DESC
                """)
                
                patterns = []
                for row in cur.fetchall():
                    patterns.append({
                        'text': row[0],
                        'context': row[1],
                        'confidence': row[2]
                    })
                
                return {'patterns': patterns}
                
        except Exception as e:
            print(f"文体パターン取得エラー: {e}")
            return {}

def main():
    """コマンドライン実行用メイン関数"""
    if len(sys.argv) < 3:
        print("使い方:")
        print("  python generate.py proposal <client_name> <topic>")
        print("  python generate.py meeting <meeting_data_json>")
        print("  python generate.py blog <title> <topic>")
        return
    
    content_type = sys.argv[1]
    generator = ContentGenerator()
    
    if content_type == "proposal":
        if len(sys.argv) < 4:
            print("エラー: client_name と topic が必要です")
            return
        
        client_name = sys.argv[2]
        topic = sys.argv[3]
        
        proposal = generator.generate_proposal(client_name, topic)
        print(proposal)
    
    elif content_type == "meeting":
        if len(sys.argv) < 3:
            print("エラー: meeting_data_json が必要です")
            return
        
        try:
            meeting_data = json.loads(sys.argv[2])
        except json.JSONDecodeError:
            print("エラー: 無効なJSON形式です")
            return
        
        summary = generator.generate_meeting_summary(meeting_data)
        print(summary)
    
    elif content_type == "blog":
        if len(sys.argv) < 4:
            print("エラー: title と topic が必要です")
            return
        
        title = sys.argv[2]
        topic = sys.argv[3]
        
        blog_post = generator.generate_blog_post(title, topic)
        print(blog_post)
    
    else:
        print(f"不明なコンテンツタイプ: {content_type}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Gemini AIを使用して動画の字幕とコメントから質的分析を行うクラス。
"""

import google.generativeai as genai
from typing import Dict, List, Optional, Any
import os
import json
import re
import logging

logger = logging.getLogger(__name__)

class GeminiAnalyzer:
    """
    Gemini AIを使用して動画の字幕とコメントから質的分析を行うクラス。
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        GeminiAnalyzerを初期化します。
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API Key is not provided in args or environment variable 'GEMINI_API_KEY'.")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_video_fully(self, transcript: str, comments: List[Dict], video_duration: int) -> Dict:
        """
        Geminiを使用して動画の包括的な質的分析を実行します。
        """
        transcript_snippet = transcript[:8000] if transcript else "字幕なし"
        
        # コメントをテキストに変換
        comments_text_list = [f"'{c.get('text', '')}' (at {c.get('formatted_time', 'N/A')}, likes: {c.get('like_count', 0)})" for c in comments[:50]]
        comments_snippet = "\n".join(comments_text_list)[:8000]

        prompt = f"""
        あなたは、YouTube動画のパフォーマンスを分析し、コンテンツ戦略を提案するプロのデータアナリストです。
        以下の動画データに基づき、指定されたすべての項目を分析し、厳格なJSON形式で出力してください。

        # 入力データ
        - 動画の長さ: {video_duration}秒
        - 字幕(トランスクリプト):
        {transcript_snippet}
        - 視聴者コメント(タイムスタンプといいね数付き):
        {comments_snippet}

        # 分析タスクと出力形式
        以下のJSONオブジェクトを完成させてください。時間は「MM:SS」形式で記述してください。
        YouTube APIの仕様上、視聴維持率データは直接取得できません。そのため、字幕の文脈とコメントの分布から**論理的に推定**してください。

        {{
          "vvp_scores": {{
            "narrative_structure": {{ "score": <number_0_to_10>, "reason": "物語構造(導入-展開-結論)の有効性を評価してください。" }},
            "hook_effectiveness": {{ "score": <number_0_to_10>, "reason": "動画冒頭30秒のフックの強さと視聴者を引き込む力を評価してください。" }},
            "emotional_engagement": {{ "score": <number_0_to_10>, "reason": "コメントから読み取れる視聴者の感情的な熱量(感動、驚き、共感など)を評価してください。" }}
          }},
          "retention_analysis": {{
            "peak_viewership_segment": {{
              "time_range": "<MM:SS> - <MM:SS>",
              "reason": "視聴者の関心が最も高まったと**推定**される区間とその論理的根拠を述べてください。"
            }},
            "highest_dropoff_point": {{
              "time_range": "<MM:SS> - <MM:SS>",
              "reason": "視聴者が最も離脱したと**推定**される区間とその論理的根拠(例:話が難しい、間延びしている等)を述べてください。"
            }},
            "second_highest_dropoff_point": {{
              "time_range": "<MM:SS> - <MM:SS>",
              "reason": "2番目に離脱が多かったと**推定**される区間とその論理的根拠を述べてください。"
            }}
          }},
          "engagement_hotspots": {{
            "most_liked_segment": {{
              "time_range": "<MM:SS> - <MM:SS>",
              "reason": "いいね数が最も多かったコメントのタイムスタンプ周辺で、何が評価されたかを分析してください。"
            }},
            "most_commented_segment": {{
              "time_range": "<MM:SS> - <MM:SS>",
              "reason": "コメントが最も集中した区間で、どのような議論や反応があったかを分析してください。"
            }}
          }},
          "top_clips_semantic_analysis": [
            {{
              "time": "<MM:SS>",
              "reason": "タイムスタンプ付きコメントが最も集中した箇所について、なぜそこが注目されたのか(例:感動のクライマックス、面白い発言、有益な情報)を分析してください。"
            }},
            {{
              "time": "<MM:SS>",
              "reason": "2番目にコメントが集中した箇所について、なぜそこが注目されたのかを分析してください。"
            }},
            {{
              "time": "<MM:SS>",
              "reason": "3番目にコメントが集中した箇所について、なぜそこが注目されたのかを分析してください。"
            }}
          ],
          "golden_clip_suggestion": {{
            "time_range": "<MM:SS> - <MM:SS>",
            "duration": <number_in_seconds>,
            "reason": "すべての分析を統合し、最もバイラルポテンシャルが高いと判断した「ゴールデンクリップ」を1つ提案し、その選定理由を戦略的に説明してください。"
          }}
        }}
        """

        try:
            logger.info("Gemini分析開始")
            response = self.model.generate_content(prompt)
            cleaned_text = re.sub(r'^```json\s*|\s*```$', '', response.text, flags=re.MULTILINE | re.DOTALL).strip()
            analysis_result = json.loads(cleaned_text)
            logger.info("Gemini分析完了")
            return analysis_result
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            if 'response' in locals():
                logger.error(f"Original Gemini response text: {response.text}")
            return {"error": f"Gemini analysis failed: {str(e)}", "raw_response": response.text if 'response' in locals() else "No response"}

    def analyze_emotions(self, comments: List[Dict]) -> Dict[str, Any]:
        """
        コメントの感情分析を実行
        
        Args:
            comments (List[Dict]): コメントリスト
            
        Returns:
            Dict[str, Any]: 感情分析結果
        """
        try:
            logger.info("感情分析開始")
            
            # コメントテキストを準備
            comment_texts = [comment['text'] for comment in comments[:50]]
            comments_text = '\n'.join([f"コメント{i+1}: {text}" for i, text in enumerate(comment_texts)])
            
            prompt = f"""
            以下のYouTube動画のコメントを感情分析してください。
            
            【コメント】
            {comments_text}
            
            【分析項目】
            1. 全体的な感情傾向（ポジティブ/ネガティブ/ニュートラル）
            2. 感情分布（ポジティブ、ネガティブ、ニュートラルの割合）
            3. 主要な感情キーワード
            4. 視聴者の満足度評価
            
            【出力形式】
            {{
                "overall_sentiment": "ポジティブ/ネガティブ/ニュートラル",
                "sentiment_distribution": {{
                    "positive": 割合,
                    "negative": 割合,
                    "neutral": 割合
                }},
                "key_emotions": ["感情1", "感情2", "感情3"],
                "satisfaction_score": 数値,
                "analysis_summary": "分析要約"
            }}
            """
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # JSONブロックの抽出
            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_text = response_text.split("```")[1]
            else:
                json_text = response_text
            
            json_text = json_text.strip()
            
            try:
                result = json.loads(json_text)
                logger.info("感情分析完了")
                return result
            except json.JSONDecodeError as e:
                logger.error(f"感情分析JSON解析失敗: {e}")
                return self._create_fallback_emotion_result()
                
        except Exception as e:
            logger.error(f"感情分析失敗: {e}")
            return self._create_fallback_emotion_result()

    def analyze_clip_points(self, comments: List[Dict], video_duration: int) -> Dict[str, Any]:
        """
        切り抜きポイント分析を実行
        
        Args:
            comments (List[Dict]): コメントリスト
            video_duration (int): 動画の長さ（秒）
            
        Returns:
            Dict[str, Any]: 切り抜きポイント分析結果
        """
        try:
            logger.info("切り抜きポイント分析開始")
            
            # タイムスタンプ付きコメントを抽出
            timestamp_comments = []
            for comment in comments:
                if comment.get('timestamps'):
                    for timestamp in comment['timestamps']:
                        timestamp_comments.append({
                            'time': timestamp['formatted'],
                            'seconds': timestamp['seconds'],
                            'text': comment['text'],
                            'author': comment['author'],
                            'like_count': comment['like_count']
                        })
            
            if not timestamp_comments:
                logger.warning("タイムスタンプ付きコメントが見つかりません")
                return self._create_fallback_clip_result()
            
            # 時間帯別にコメントをグループ化
            time_groups = {}
            for comment in timestamp_comments:
                time_key = f"{comment['seconds'] // 30 * 30:04d}"  # 30秒単位でグループ化
                if time_key not in time_groups:
                    time_groups[time_key] = []
                time_groups[time_key].append(comment)
            
            # 最も人気のある時間帯を特定
            popular_times = sorted(time_groups.items(), key=lambda x: len(x[1]), reverse=True)[:5]
            
            # Gemini APIで詳細分析
            popular_times_text = "\n".join([
                f"{time}: {len(comments)}件のコメント" for time, comments in popular_times
            ])
            
            prompt = f"""
            以下のYouTube動画の切り抜きポイント分析を行ってください。
            
            【動画の長さ】: {video_duration}秒
            
            【人気のある時間帯】
            {popular_times_text}
            
            【タイムスタンプ付きコメント例】
            {json.dumps(timestamp_comments[:10], indent=2, ensure_ascii=False)}
            
            【分析項目】
            1. 最も注目すべき切り抜きポイント（上位3つ）
            2. 各ポイントの人気理由
            3. 切り抜き動画としての適性評価
            4. 視聴者の反応パターン
            
            【出力形式】
            {{
                "top_clip_points": [
                    {{
                        "time": "時間",
                        "seconds": 秒数,
                        "reason": "人気理由",
                        "comment_count": コメント数,
                        "clip_suitability": "適性評価"
                    }}
                ],
                "clip_analysis": {{
                    "total_timestamp_comments": 総数,
                    "most_popular_time_range": "最も人気の時間帯",
                    "viewer_engagement_pattern": "視聴者反応パターン",
                    "recommendations": ["推奨事項1", "推奨事項2"]
                }}
            }}
            """
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # JSONブロックの抽出
            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_text = response_text.split("```")[1]
            else:
                json_text = response_text
            
            json_text = json_text.strip()
            
            try:
                result = json.loads(json_text)
                logger.info("切り抜きポイント分析完了")
                return result
            except json.JSONDecodeError as e:
                logger.error(f"切り抜きポイント分析JSON解析失敗: {e}")
                return self._create_fallback_clip_result()
                
        except Exception as e:
            logger.error(f"切り抜きポイント分析失敗: {e}")
            return self._create_fallback_clip_result()

    def _create_fallback_emotion_result(self) -> Dict[str, Any]:
        """
        フォールバック用の感情分析結果を作成
        
        Returns:
            Dict[str, Any]: フォールバック結果
        """
        return {
            "overall_sentiment": "ニュートラル",
            "sentiment_distribution": {
                "positive": 0.33,
                "negative": 0.33,
                "neutral": 0.34
            },
            "key_emotions": ["一般的", "標準的", "平均的"],
            "satisfaction_score": 5.0,
            "analysis_summary": "感情分析に問題がありました。"
        }

    def _create_fallback_clip_result(self) -> Dict[str, Any]:
        """
        フォールバック用の切り抜きポイント分析結果を作成
        
        Returns:
            Dict[str, Any]: フォールバック結果
        """
        return {
            "top_clip_points": [
                {
                    "time": "00:00",
                    "seconds": 0,
                    "reason": "自動解析",
                    "comment_count": 0,
                    "clip_suitability": "要確認"
                }
            ],
            "clip_analysis": {
                "total_timestamp_comments": 0,
                "most_popular_time_range": "N/A",
                "viewer_engagement_pattern": "要確認",
                "recommendations": ["より詳細な分析が必要です"]
            }
        } 
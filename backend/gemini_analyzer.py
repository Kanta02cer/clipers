# backend/gemini_analyzer.py

import google.generativeai as genai
from typing import Dict, List, Optional
import os
import json
import re

class GeminiAnalyzer:
    """
    Gemini AIを使用して動画の字幕とコメントから質的分析を行うクラス。
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        GeminiAnalyzerを初期化します。

        Args:
            api_key (Optional[str]): Gemini APIキー。提供されない場合は環境変数 'GEMINI_API_KEY' を使用します。
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API Key is not provided in args or environment variable 'GEMINI_API_KEY'.")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_content_with_gemini_realtime(self, transcript: str, comments: List[str], 
                                           engagement_data: Dict = None) -> Dict:
        """
        Geminiを使用して動画の質的分析を実行（リアルタイム版）
        """
        analysis_steps = []
        
        # ステップ1: データ準備
        analysis_steps.append({
            "step": 1,
            "title": "データ準備",
            "description": "字幕とコメントデータを分析用に準備中...",
            "status": "processing"
        })
        
        transcript_snippet = transcript[:8000] if transcript else "字幕なし"
        comments_snippet = "\n".join(comments[:50])[:8000] if comments else "コメントなし"
        
        # ステップ2: エンゲージメントデータの統合
        analysis_steps.append({
            "step": 2,
            "title": "エンゲージメント分析",
            "description": "コメントの感情分析とキーワード抽出を実行中...",
            "status": "processing"
        })
        
        # ステップ3: AI分析の実行
        analysis_steps.append({
            "step": 3,
            "title": "AI分析実行",
            "description": "Gemini AIが動画の質的分析を実行中...",
            "status": "processing"
        })
        
        # エンゲージメントデータをプロンプトに統合
        engagement_info = ""
        if engagement_data and 'engagement_analysis' in engagement_data:
            engagement = engagement_data['engagement_analysis']
            engagement_info = f"""
            # エンゲージメント分析結果:
            - エンゲージメント率: {engagement.get('engagement_rate', 0)}%
            - コメント数: {engagement.get('comments', {}).get('total_comments', 0)}
            - 感情分析: ポジティブ {engagement.get('comment_sentiment', {}).get('positive_rate', 0)}%
            - 人気キーワード: {', '.join([kw['word'] for kw in engagement.get('popular_keywords', [])[:5]])}
            """
        
        prompt = f"""
        あなたはプロのYouTube動画アナリストです。
        以下の動画の字幕、視聴者コメント、エンゲージメントデータを総合的に分析し、4つの観点から評価してください。

        # 動画の字幕 (トランスクリプト):
        {transcript_snippet}

        # 視聴者コメント (上位50件):
        {comments_snippet}

        {engagement_info}

        # 分析と評価:
        以下のJSON形式で、厳密に出力してください。各スコアは10段階評価とします。

        {{
          "narrative_structure": {{
            "score": <number>,
            "reason": "動画の物語構造（導入→展開→クライマックス→結論）を評価し、その理由を簡潔に述べてください。"
          }},
          "emotional_engagement": {{
            "score": <number>,
            "dominant_emotion": "コメント全体の感情的共感を評価し、最も多かった感情（例：感動、面白い、驚き、共感）を挙げてください。"
          }},
          "semantic_hotspots": [
              {{ "time": "XX:XX", "reason": "コメントから判断できる、視聴者が最も価値を感じたポイントを具体的な内容と共に挙げてください。" }}
          ],
          "virality_prediction": {{
            "score": <number>,
            "reason": "コメント内のキーワードや文脈から、この動画の拡散可能性（バイラリティ）を評価し、その根拠を述べてください。"
          }},
          "engagement_insights": {{
            "strengths": ["動画の強みを3つ挙げてください"],
            "improvements": ["改善点を3つ挙げてください"],
            "target_audience": "主なターゲット層を分析してください"
          }}
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            
            # ステップ4: 結果の解析
            analysis_steps.append({
                "step": 4,
                "title": "結果解析",
                "description": "AI分析結果を解析中...",
                "status": "processing"
            })
            
            cleaned_text = re.sub(r'^```json\s*|\s*```$', '', response.text, flags=re.MULTILINE | re.DOTALL).strip()
            analysis_result = json.loads(cleaned_text)
            
            # 全ステップを完了に更新
            for step in analysis_steps:
                step["status"] = "completed"
            
            return {
                "analysis_result": analysis_result,
                "analysis_steps": analysis_steps,
                "raw_prompt": prompt,
                "raw_response": response.text
            }
            
        except Exception as e:
            # エラー時のステップ更新
            for step in analysis_steps:
                if step["status"] == "processing":
                    step["status"] = "error"
                    step["description"] = f"エラー: {str(e)}"
            
            return {
                "error": f"Gemini analysis failed: {str(e)}",
                "analysis_steps": analysis_steps,
                "raw_response": response.text if 'response' in locals() else "No response"
            }

    def analyze_content_with_gemini(self, transcript: str, comments: List[str]) -> Dict:
        """
        Geminiを使用して動画の質的分析を実行します（後方互換性のため）
        """
        result = self.analyze_content_with_gemini_realtime(transcript, comments)
        return result.get("analysis_result", result) 
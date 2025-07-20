#!/usr/bin/env python3
"""
Gemini-Enhanced VVP ScoreとClip Scoreを計算するためのロジックを格納するクラス。
"""

from typing import Dict, List, Any
import re

class VVPScoreCalculator:
    """
    Gemini-Enhanced VVP ScoreとClip Scoreを計算するためのロジックを格納するクラス。
    """
    VVP_WEIGHTS = {
        "narrative_retention": 0.40,
        "hook_effectiveness": 0.30,
        "engagement_signals": 0.25,
        "technical_quality": 0.05,
    }

    CLIP_SCORE_WEIGHTS = {
        "quantitative_engagement": 0.6,
        "qualitative_insight": 0.4,
    }

    def _normalize_score(self, score: float, max_score: float) -> float:
        """スコアを0-100の範囲に正規化する"""
        return min(100.0, max(0.0, (score / max_score) * 100))

    def calculate_vvp_score(self, gemini_kpis: Dict, tech_quality_score: float) -> Dict:
        """
        Geminiの質的分析と技術品質から総合VVPスコアを算出する。

        Args:
            gemini_kpis (Dict): GeminiによるKPI評価 (各10点満点)。
            tech_quality_score (float): 技術品質スコア (100点満点)。

        Returns:
            Dict: 各柱のスコアと総合スコアを含む辞書。
        """
        scores = {
            "narrative_retention": self._normalize_score(gemini_kpis.get("narrative_structure", {}).get("score", 0), 10),
            "hook_effectiveness": self._normalize_score(gemini_kpis.get("hook_effectiveness", {}).get("score", 0), 10),
            "engagement_signals": self._normalize_score(gemini_kpis.get("emotional_engagement", {}).get("score", 0), 10),
            "technical_quality": tech_quality_score,
        }

        total_score = (
            scores["narrative_retention"] * self.VVP_WEIGHTS["narrative_retention"] +
            scores["hook_effectiveness"] * self.VVP_WEIGHTS["hook_effectiveness"] +
            scores["engagement_signals"] * self.VVP_WEIGHTS["engagement_signals"] +
            scores["technical_quality"] * self.VVP_WEIGHTS["technical_quality"]
        )

        scores["total_vvp_score"] = round(total_score, 2)
        return scores

    def calculate_clip_scores(self, engagement_hotspots: List[Dict], gemini_hotspots: List[Dict]) -> List[Dict]:
        """
        各切り抜き候補のClip Scoreを算出する。

        Args:
            engagement_hotspots (List[Dict]): コメント数やいいねに基づく量的ホットスポット。
            gemini_hotspots (List[Dict]): Geminiによる質的ホットスポット。

        Returns:
            List[Dict]: 各ホットスポットにClip Scoreが追加されたリスト。
        """
        if not engagement_hotspots:
            return []

        max_mention_count = max(h.get("mention_count", 1) for h in engagement_hotspots)

        scored_clips = []
        for eng_spot in engagement_hotspots:
            # 1. 定量エンゲージメントスコア (Quantitative Engagement Score)
            # 正規化した言及回数をスコアとする (0-100)
            quant_score = self._normalize_score(eng_spot.get("mention_count", 0), max_mention_count)

            # 2. 定性インサイトスコア (Qualitative Insight Score)
            qual_score = 0
            reason = "視聴者の注目"
            # Geminiの分析と時間帯が近いものを探す
            for gem_spot in gemini_hotspots:
                # 簡単な時間比較（±15秒以内など）
                try:
                    gem_time_sec = self._time_str_to_seconds(gem_spot.get("time", "0:0"))
                    if abs(eng_spot.get("time", 0) - gem_time_sec) <= 15:
                        # Geminiが特定した理由に応じてスコアを加算
                        if "感動" in gem_spot.get("reason", "") or "クライマックス" in gem_spot.get("reason", ""):
                            qual_score = 100
                        elif "面白い" in gem_spot.get("reason", "") or "ユーモア" in gem_spot.get("reason", ""):
                            qual_score = 90
                        elif "学び" in gem_spot.get("reason", "") or "有益" in gem_spot.get("reason", ""):
                            qual_score = 80
                        else:
                            qual_score = 70
                        reason = gem_spot.get("reason", reason)
                        break # 最初に見つかったものを採用
                except:
                    pass
            
            if qual_score == 0:
                qual_score = 50 # Geminiの特定がなくても基本スコア

            # 3. 最終クリップスコアの計算
            clip_score = (
                quant_score * self.CLIP_SCORE_WEIGHTS["quantitative_engagement"] +
                qual_score * self.CLIP_SCORE_WEIGHTS["qualitative_insight"]
            )
            
            eng_spot["clip_score"] = round(clip_score)
            eng_spot["reason"] = reason
            scored_clips.append(eng_spot)

        # スコアの高い順にソート
        return sorted(scored_clips, key=lambda x: x["clip_score"], reverse=True)

    def _time_str_to_seconds(self, time_str: str) -> int:
        """時間文字列 (M:SS or H:MM:SS) を秒に変換"""
        parts = list(map(int, time_str.split(':')))
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
        return 0

    def extract_timestamps_from_comments(self, comments: List[Dict]) -> List[Dict]:
        """
        コメントからタイムスタンプを抽出し、ホットスポットを特定する
        
        Args:
            comments (List[Dict]): コメントリスト
            
        Returns:
            List[Dict]: タイムスタンプ付きホットスポット
        """
        timestamp_patterns = [
            r'(\d{1,2}):(\d{2})(?::(\d{2}))?',  # MM:SS または HH:MM:SS
            r'(\d{1,2})分(\d{1,2})秒',  # 日本語形式
            r'(\d{1,2})m(\d{1,2})s',  # 英語形式
        ]
        
        hotspots = {}
        
        for comment in comments:
            comment_text = comment.get('text', '')
            
            for pattern in timestamp_patterns:
                matches = re.finditer(pattern, comment_text)
                for match in matches:
                    if len(match.groups()) == 3 and match.group(3):  # HH:MM:SS
                        hours = int(match.group(1))
                        minutes = int(match.group(2))
                        seconds = int(match.group(3))
                        total_seconds = hours * 3600 + minutes * 60 + seconds
                    elif len(match.groups()) == 2:  # MM:SS
                        minutes = int(match.group(1))
                        seconds = int(match.group(2))
                        total_seconds = minutes * 60 + seconds
                    else:
                        continue
                    
                    # 30秒単位でグループ化
                    time_key = f"{total_seconds // 30 * 30:04d}"
                    
                    if time_key not in hotspots:
                        hotspots[time_key] = {
                            'time': total_seconds,
                            'formatted_time': f"{minutes:02d}:{seconds:02d}" if len(match.groups()) == 2 else f"{hours:02d}:{minutes:02d}:{seconds:02d}",
                            'mention_count': 0,
                            'comments': [],
                            'total_likes': 0
                        }
                    
                    hotspots[time_key]['mention_count'] += 1
                    hotspots[time_key]['comments'].append({
                        'text': comment_text,
                        'author': comment.get('author', 'Unknown'),
                        'likes': comment.get('like_count', 0)
                    })
                    hotspots[time_key]['total_likes'] += comment.get('like_count', 0)
        
        # リストに変換してソート
        hotspot_list = list(hotspots.values())
        return sorted(hotspot_list, key=lambda x: x['mention_count'], reverse=True)

    def calculate_engagement_metrics(self, comments: List[Dict]) -> Dict[str, Any]:
        """
        エンゲージメント指標を計算する
        
        Args:
            comments (List[Dict]): コメントリスト
            
        Returns:
            Dict[str, Any]: エンゲージメント指標
        """
        if not comments:
            return {
                'total_comments': 0,
                'total_likes': 0,
                'avg_likes_per_comment': 0,
                'engagement_rate': 0,
                'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0}
            }
        
        total_comments = len(comments)
        total_likes = sum(comment.get('like_count', 0) for comment in comments)
        avg_likes_per_comment = total_likes / total_comments if total_comments > 0 else 0
        
        # 簡単な感情分析（キーワードベース）
        positive_keywords = ['素晴らしい', '最高', '感動', '面白い', '良い', 'love', 'amazing', 'great', 'awesome']
        negative_keywords = ['つまらない', '悪い', '最悪', '退屈', 'hate', 'terrible', 'boring', 'bad']
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for comment in comments:
            text = comment.get('text', '').lower()
            if any(keyword in text for keyword in positive_keywords):
                positive_count += 1
            elif any(keyword in text for keyword in negative_keywords):
                negative_count += 1
            else:
                neutral_count += 1
        
        sentiment_distribution = {
            'positive': positive_count / total_comments if total_comments > 0 else 0,
            'negative': negative_count / total_comments if total_comments > 0 else 0,
            'neutral': neutral_count / total_comments if total_comments > 0 else 0
        }
        
        return {
            'total_comments': total_comments,
            'total_likes': total_likes,
            'avg_likes_per_comment': round(avg_likes_per_comment, 2),
            'engagement_rate': round((total_likes + total_comments) / 1000, 2),  # 仮の計算式
            'sentiment_distribution': sentiment_distribution
        } 
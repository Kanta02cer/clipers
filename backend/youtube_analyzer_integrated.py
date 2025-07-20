#!/usr/bin/env python3
"""
統合YouTube動画分析システム
YouTube Data API v3、yt-dlp、Gemini AI、コンテンツ分析を統合
"""

import os
import sys
import json
import logging
import tempfile
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# YouTube API関連
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 動画ダウンロード関連
import yt_dlp

# AI分析関連
from gemini_analyzer import GeminiAnalyzer
from analysis_logic import VVPScoreCalculator
from content_analyzer import ContentAnalyzer

# 設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegratedYouTubeAnalyzer:
    """統合YouTube動画分析器"""
    
    def __init__(self, youtube_api_key: str, gemini_api_key: str):
        """
        初期化
        
        Args:
            youtube_api_key: YouTube Data API v3キー
            gemini_api_key: Google Gemini APIキー
        """
        self.youtube_api_key = youtube_api_key
        self.gemini_api_key = gemini_api_key
        
        # YouTube APIクライアント初期化
        try:
            self.youtube_client = build('youtube', 'v3', developerKey=youtube_api_key)
            logger.info("YouTube APIクライアント初期化成功")
        except Exception as e:
            logger.error(f"YouTube APIクライアント初期化エラー: {e}")
            self.youtube_client = None
        
        # Gemini分析器初期化
        try:
            self.gemini_analyzer = GeminiAnalyzer(gemini_api_key)
            logger.info("Gemini分析器初期化成功")
        except Exception as e:
            logger.error(f"Gemini分析器初期化エラー: {e}")
            self.gemini_analyzer = None
        
        # VVPスコア計算器初期化
        try:
            self.vvp_calculator = VVPScoreCalculator()
            logger.info("VVPスコア計算器初期化成功")
        except Exception as e:
            logger.error(f"VVPスコア計算器初期化エラー: {e}")
            self.vvp_calculator = None
        
        # コンテンツ分析器初期化
        try:
            self.content_analyzer = ContentAnalyzer()
            logger.info("コンテンツ分析器初期化成功")
        except Exception as e:
            logger.error(f"コンテンツ分析器初期化エラー: {e}")
            self.content_analyzer = None
        
        # 一時ディレクトリ作成
        self.temp_dir = tempfile.mkdtemp(prefix='youtube_analyzer_')
        logger.info(f"一時ディレクトリ作成: {self.temp_dir}")
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        YouTube URLから動画IDを抽出
        
        Args:
            url: YouTube動画URL
            
        Returns:
            動画ID
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        YouTube動画の詳細情報を取得
        
        Args:
            video_id: 動画ID
            
        Returns:
            動画情報
        """
        try:
            if not self.youtube_client:
                raise Exception("YouTube APIクライアントが初期化されていません")
            
            # 動画情報取得
            video_response = self.youtube_client.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            ).execute()
            
            if not video_response['items']:
                raise Exception(f"動画が見つかりません: {video_id}")
            
            video_data = video_response['items'][0]
            snippet = video_data['snippet']
            statistics = video_data['statistics']
            content_details = video_data['contentDetails']
            
            # チャンネル情報取得
            channel_id = snippet['channelId']
            channel_response = self.youtube_client.channels().list(
                part='snippet,statistics',
                id=channel_id
            ).execute()
            
            channel_data = channel_response['items'][0] if channel_response['items'] else {}
            channel_snippet = channel_data.get('snippet', {})
            channel_statistics = channel_data.get('statistics', {})
            
            # コメント取得（最新100件）
            comments = []
            try:
                comment_response = self.youtube_client.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=100,
                    order='relevance'
                ).execute()
                
                for item in comment_response['items']:
                    comment = item['snippet']['topLevelComment']['snippet']
                    comments.append({
                        'author': comment['authorDisplayName'],
                        'text': comment['textDisplay'],
                        'like_count': comment['likeCount'],
                        'published_at': comment['publishedAt']
                    })
            except HttpError as e:
                logger.warning(f"コメント取得エラー: {e}")
            
            return {
                'video_id': video_id,
                'title': snippet['title'],
                'description': snippet['description'],
                'channel_title': snippet['channelTitle'],
                'channel_id': channel_id,
                'published_at': snippet['publishedAt'],
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'duration': content_details.get('duration', 'PT0S'),
                'tags': snippet.get('tags', []),
                'category_id': snippet.get('categoryId', ''),
                'comments': comments,
                'channel_info': {
                    'title': channel_snippet.get('title', ''),
                    'description': channel_snippet.get('description', ''),
                    'subscriber_count': int(channel_statistics.get('subscriberCount', 0)),
                    'video_count': int(channel_statistics.get('videoCount', 0)),
                    'view_count': int(channel_statistics.get('viewCount', 0))
                }
            }
            
        except Exception as e:
            logger.error(f"動画情報取得エラー: {e}")
            raise
    
    def download_video(self, url: str, output_format: str = 'mp4') -> Dict[str, Any]:
        """
        動画をダウンロード
        
        Args:
            url: YouTube動画URL
            output_format: 出力形式
            
        Returns:
            ダウンロード結果
        """
        try:
            video_id = self.extract_video_id(url)
            if not video_id:
                raise Exception("有効なYouTube URLではありません")
            
            # 出力ファイル名
            output_filename = f"{video_id}.{output_format}"
            output_path = os.path.join(self.temp_dir, output_filename)
            
            # 字幕ファイル名
            subtitle_filename = f"{video_id}_subtitle.vtt"
            subtitle_path = os.path.join(self.temp_dir, subtitle_filename)
            
            # yt-dlp設定
            ydl_opts = {
                'format': f'best[ext={output_format}]/best',
                'outtmpl': output_path,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['ja', 'en'],
                'subtitlesformat': 'vtt',
                'writesubtitles': True,
                'writeautomaticsub': True,
                'writethumbnail': True,
                'writeinfojson': True,
                'quiet': True,
                'no_warnings': True
            }
            
            logger.info(f"動画ダウンロード開始: {url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # 動画ファイルの存在確認
                if not os.path.exists(output_path):
                    # 実際のファイル名を取得
                    for file in os.listdir(self.temp_dir):
                        if file.startswith(video_id) and file.endswith(f'.{output_format}'):
                            output_path = os.path.join(self.temp_dir, file)
                            break
                
                # 字幕ファイルの存在確認
                subtitle_path = None
                for file in os.listdir(self.temp_dir):
                    if file.startswith(video_id) and file.endswith('.vtt'):
                        subtitle_path = os.path.join(self.temp_dir, file)
                        break
                
                # 情報JSONファイルの存在確認
                info_json_path = None
                for file in os.listdir(self.temp_dir):
                    if file.startswith(video_id) and file.endswith('.info.json'):
                        info_json_path = os.path.join(self.temp_dir, file)
                        break
                
                # サムネイルファイルの存在確認
                thumbnail_path = None
                for file in os.listdir(self.temp_dir):
                    if file.startswith(video_id) and (file.endswith('.jpg') or file.endswith('.png')):
                        thumbnail_path = os.path.join(self.temp_dir, file)
                        break
                
                return {
                    'success': True,
                    'video_path': output_path if os.path.exists(output_path) else None,
                    'subtitle_path': subtitle_path,
                    'info_json_path': info_json_path,
                    'thumbnail_path': thumbnail_path,
                    'duration': info.get('duration', 0),
                    'title': info.get('title', ''),
                    'uploader': info.get('uploader', ''),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'description': info.get('description', '')
                }
                
        except Exception as e:
            logger.error(f"動画ダウンロードエラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def parse_subtitle(self, subtitle_path: str) -> str:
        """
        字幕ファイルを解析してテキストを抽出
        
        Args:
            subtitle_path: 字幕ファイルのパス
            
        Returns:
            字幕テキスト
        """
        try:
            if not subtitle_path or not os.path.exists(subtitle_path):
                return ""
            
            with open(subtitle_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # VTTファイルからテキストを抽出
            lines = content.split('\n')
            text_lines = []
            in_text_block = False
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('WEBVTT') or '-->' in line:
                    continue
                
                if line and not line[0].isdigit():
                    text_lines.append(line)
            
            return ' '.join(text_lines)
            
        except Exception as e:
            logger.error(f"字幕解析エラー: {e}")
            return ""
    
    def analyze_with_gemini(self, video_info: Dict[str, Any], subtitle_text: str = "") -> Dict[str, Any]:
        """
        Gemini AIを使用して動画を分析
        
        Args:
            video_info: 動画情報
            subtitle_text: 字幕テキスト
            
        Returns:
            Gemini分析結果
        """
        try:
            if not self.gemini_analyzer:
                raise Exception("Gemini分析器が初期化されていません")
            
            logger.info("Gemini分析開始")
            
            # 包括的分析実行
            result = self.gemini_analyzer.analyze_video_comprehensive(
                video_info=video_info,
                subtitle_text=subtitle_text
            )
            
            logger.info("Gemini分析完了")
            return result
            
        except Exception as e:
            logger.error(f"Gemini分析エラー: {e}")
            return {
                'narrative_score': 0,
                'narrative_reason': f'分析エラー: {str(e)}',
                'hook_score': 0,
                'hook_reason': f'分析エラー: {str(e)}',
                'engagement_score': 0,
                'engagement_reason': f'分析エラー: {str(e)}',
                'tech_score': 0,
                'tech_reason': f'分析エラー: {str(e)}',
                'vvp_score': 0,
                'golden_clip': {
                    'time_range': 'N/A',
                    'duration': 0,
                    'reason': f'分析エラー: {str(e)}'
                },
                'summary': f'分析エラー: {str(e)}',
                'target_audience': 'N/A',
                'improvement_suggestions': ['分析エラーが発生しました']
            }
    
    def analyze_emotions(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        コメントの感情分析
        
        Args:
            comments: コメントリスト
            
        Returns:
            感情分析結果
        """
        try:
            if not comments:
                return {
                    'overall_sentiment': 'neutral',
                    'satisfaction_distribution': {
                        'positive': 0.0,
                        'neutral': 1.0,
                        'negative': 0.0
                    },
                    'key_emotions': [],
                    'analysis': 'コメントがありません'
                }
            
            # 感情分析実行
            if self.gemini_analyzer:
                return self.gemini_analyzer.analyze_emotions(comments)
            else:
                # フォールバック: 簡単な感情分析
                positive_words = ['すごい', '素晴らしい', '感動', '面白い', '楽しい', '最高', '完璧']
                negative_words = ['つまらない', '退屈', '悪い', '最悪', '嫌い', '失敗']
                
                positive_count = 0
                negative_count = 0
                total_comments = len(comments)
                
                for comment in comments:
                    text = comment.get('text', '').lower()
                    positive_count += sum(1 for word in positive_words if word in text)
                    negative_count += sum(1 for word in negative_words if word in text)
                
                positive_ratio = positive_count / total_comments if total_comments > 0 else 0
                negative_ratio = negative_count / total_comments if total_comments > 0 else 0
                neutral_ratio = 1 - positive_ratio - negative_ratio
                
                return {
                    'overall_sentiment': 'positive' if positive_ratio > negative_ratio else 'negative' if negative_ratio > positive_ratio else 'neutral',
                    'satisfaction_distribution': {
                        'positive': positive_ratio,
                        'neutral': neutral_ratio,
                        'negative': negative_ratio
                    },
                    'key_emotions': [],
                    'analysis': f'ポジティブ: {positive_ratio:.2f}, ネガティブ: {negative_ratio:.2f}, ニュートラル: {neutral_ratio:.2f}'
                }
                
        except Exception as e:
            logger.error(f"感情分析エラー: {e}")
            return {
                'overall_sentiment': 'neutral',
                'satisfaction_distribution': {
                    'positive': 0.0,
                    'neutral': 1.0,
                    'negative': 0.0
                },
                'key_emotions': [],
                'analysis': f'感情分析エラー: {str(e)}'
            }
    
    def analyze_clip_points(self, comments: List[Dict[str, Any]], video_duration: int = 0) -> Dict[str, Any]:
        """
        切り抜きポイント分析
        
        Args:
            comments: コメントリスト
            video_duration: 動画の長さ（秒）
            
        Returns:
            切り抜きポイント分析結果
        """
        try:
            if not comments:
                return {
                    'top_clip_points': [],
                    'analysis': 'コメントがありません'
                }
            
            # タイムスタンプ付きコメントを抽出
            timestamp_comments = []
            for comment in comments:
                text = comment.get('text', '')
                # タイムスタンプパターンを検出
                timestamp_patterns = [
                    r'(\d{1,2}):(\d{2})',  # MM:SS
                    r'(\d{1,2}):(\d{2}):(\d{2})',  # HH:MM:SS
                ]
                
                for pattern in timestamp_patterns:
                    matches = re.findall(pattern, text)
                    for match in matches:
                        if len(match) == 2:  # MM:SS
                            minutes, seconds = int(match[0]), int(match[1])
                            timestamp_seconds = minutes * 60 + seconds
                        elif len(match) == 3:  # HH:MM:SS
                            hours, minutes, seconds = int(match[0]), int(match[1]), int(match[2])
                            timestamp_seconds = hours * 3600 + minutes * 60 + seconds
                        else:
                            continue
                        
                        timestamp_comments.append({
                            'timestamp': timestamp_seconds,
                            'time_str': f"{match[0]}:{match[1]}" if len(match) == 2 else f"{match[0]}:{match[1]}:{match[2]}",
                            'comment': text,
                            'like_count': comment.get('like_count', 0)
                        })
            
            if not timestamp_comments:
                return {
                    'top_clip_points': [],
                    'analysis': 'タイムスタンプ付きコメントが見つかりませんでした'
                }
            
            # タイムスタンプでグループ化
            timestamp_groups = {}
            for comment in timestamp_comments:
                timestamp = comment['timestamp']
                if timestamp not in timestamp_groups:
                    timestamp_groups[timestamp] = []
                timestamp_groups[timestamp].append(comment)
            
            # 各タイムスタンプのスコアを計算
            clip_points = []
            for timestamp, group in timestamp_groups.items():
                total_likes = sum(c['like_count'] for c in group)
                comment_count = len(group)
                
                # スコア計算（いいね数 + コメント数）
                score = total_likes + comment_count * 2
                
                clip_points.append({
                    'timestamp': timestamp,
                    'time_str': group[0]['time_str'],
                    'score': score,
                    'comment_count': comment_count,
                    'total_likes': total_likes,
                    'comments': group
                })
            
            # スコアでソート
            clip_points.sort(key=lambda x: x['score'], reverse=True)
            
            # 上位5つの切り抜きポイントを返す
            top_clip_points = []
            for point in clip_points[:5]:
                # 切り抜き適性を評価
                clip_suitability = self._evaluate_clip_suitability(point, video_duration)
                
                top_clip_points.append({
                    'time': point['time_str'],
                    'timestamp': point['timestamp'],
                    'score': point['score'],
                    'comment_count': point['comment_count'],
                    'total_likes': point['total_likes'],
                    'clip_suitability': clip_suitability,
                    'reason': self._generate_clip_reason(point),
                    'comments': point['comments'][:3]  # 上位3つのコメントのみ
                })
            
            return {
                'top_clip_points': top_clip_points,
                'analysis': f'{len(timestamp_comments)}件のタイムスタンプ付きコメントから{len(top_clip_points)}個の切り抜きポイントを特定しました'
            }
            
        except Exception as e:
            logger.error(f"切り抜きポイント分析エラー: {e}")
            return {
                'top_clip_points': [],
                'analysis': f'切り抜きポイント分析エラー: {str(e)}'
            }
    
    def analyze_content_quality(self, video_path: str, subtitle_text: str = "") -> Dict[str, Any]:
        """
        動画コンテンツの質を分析
        
        Args:
            video_path: 動画ファイルのパス
            subtitle_text: 字幕テキスト
            
        Returns:
            コンテンツ分析結果
        """
        try:
            if not self.content_analyzer:
                raise Exception("コンテンツ分析器が初期化されていません")
            
            if not video_path or not os.path.exists(video_path):
                raise Exception("動画ファイルが見つかりません")
            
            logger.info("コンテンツ分析開始")
            
            # 包括的コンテンツ分析実行
            result = self.content_analyzer.analyze_video_content(video_path, subtitle_text)
            
            logger.info("コンテンツ分析完了")
            return result
            
        except Exception as e:
            logger.error(f"コンテンツ分析エラー: {e}")
            return {
                'success': False,
                'error': str(e),
                'audio_transcription': None,
                'content_quality': None,
                'speech_patterns': None,
                'subtitle_analysis': None,
                'overall_assessment': None
            }
    
    def _evaluate_clip_suitability(self, clip_point: Dict[str, Any], video_duration: int) -> str:
        """切り抜き適性を評価"""
        try:
            score = clip_point['score']
            comment_count = clip_point['comment_count']
            
            if score >= 20 and comment_count >= 3:
                return "非常に高い"
            elif score >= 10 and comment_count >= 2:
                return "高い"
            elif score >= 5:
                return "中程度"
            else:
                return "低い"
                
        except Exception as e:
            logger.error(f"切り抜き適性評価エラー: {e}")
            return "評価不可"
    
    def _generate_clip_reason(self, clip_point: Dict[str, Any]) -> str:
        """切り抜き理由を生成"""
        try:
            comments = clip_point['comments']
            if not comments:
                return "コメント情報が不足しています"
            
            # コメントの内容から理由を推測
            text = ' '.join([c['comment'] for c in comments])
            
            if any(word in text.lower() for word in ['すごい', '素晴らしい', '感動']):
                return "視聴者が感動している場面"
            elif any(word in text.lower() for word in ['面白い', '笑った', '楽しい']):
                return "視聴者が楽しんでいる場面"
            elif any(word in text.lower() for word in ['重要', 'ポイント', '要点']):
                return "重要なポイントが含まれる場面"
            elif any(word in text.lower() for word in ['驚き', '意外', '予想外']):
                return "視聴者が驚いている場面"
            else:
                return "視聴者の関心が高い場面"
                
        except Exception as e:
            logger.error(f"切り抜き理由生成エラー: {e}")
            return "理由を特定できませんでした"
    
    def analyze_video_comprehensive(self, url: str, download_video: bool = True) -> Dict[str, Any]:
        """
        動画の包括的分析
        
        Args:
            url: YouTube動画URL
            download_video: 動画をダウンロードするかどうか
            
        Returns:
            包括的分析結果
        """
        try:
            logger.info(f"包括的分析開始: {url}")
            
            # 1. 動画情報取得
            video_id = self.extract_video_id(url)
            if not video_id:
                raise Exception("有効なYouTube URLではありません")
            
            video_info = self.get_video_info(video_id)
            
            # 2. 動画ダウンロード（オプション）
            download_result = None
            subtitle_text = ""
            video_path = None
            
            if download_video:
                download_result = self.download_video(url)
                if download_result.get('success'):
                    video_path = download_result.get('video_path')
                    subtitle_text = self.parse_subtitle(download_result.get('subtitle_path', ''))
            
            # 3. Gemini AI分析
            gemini_result = self.analyze_with_gemini(video_info, subtitle_text)
            
            # 4. 感情分析
            emotion_result = self.analyze_emotions(video_info.get('comments', []))
            
            # 5. 切り抜きポイント分析
            video_duration = download_result.get('duration', 0) if download_result else 0
            clip_result = self.analyze_clip_points(video_info.get('comments', []), video_duration)
            
            # 6. コンテンツ品質分析（動画がダウンロードされている場合）
            content_result = None
            if video_path and os.path.exists(video_path):
                content_result = self.analyze_content_quality(video_path, subtitle_text)
            
            # 7. 結果の統合
            analysis_result = {
                'video_info': video_info,
                'download_result': download_result,
                'gemini_analysis': gemini_result,
                'emotion_analysis': emotion_result,
                'clip_analysis': clip_result,
                'content_analysis': content_result,
                'analysis_timestamp': datetime.now().isoformat(),
                'processing_time': 0  # 後で計算
            }
            
            logger.info("包括的分析完了")
            return analysis_result
            
        except Exception as e:
            logger.error(f"包括的分析エラー: {e}")
            raise

# グローバルインスタンス管理
_analyzer_instance = None

def get_analyzer_instance(youtube_api_key: str, gemini_api_key: str) -> IntegratedYouTubeAnalyzer:
    """
    分析器インスタンスを取得（シングルトンパターン）
    
    Args:
        youtube_api_key: YouTube Data API v3キー
        gemini_api_key: Google Gemini APIキー
        
    Returns:
        統合分析器インスタンス
    """
    global _analyzer_instance
    
    if _analyzer_instance is None:
        _analyzer_instance = IntegratedYouTubeAnalyzer(youtube_api_key, gemini_api_key)
    
    return _analyzer_instance

if __name__ == "__main__":
    # テスト実行
    import sys
    
    if len(sys.argv) < 4:
        print("使用方法: python youtube_analyzer_integrated.py <YouTube_URL> <YouTube_API_Key> <Gemini_API_Key>")
        sys.exit(1)
    
    url = sys.argv[1]
    youtube_api_key = sys.argv[2]
    gemini_api_key = sys.argv[3]
    
    print("統合YouTube動画分析システム - テスト実行")
    print("=" * 50)
    
    try:
        analyzer = get_analyzer_instance(youtube_api_key, gemini_api_key)
        result = analyzer.analyze_video_comprehensive(url, download_video=True)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"エラー: {e}")
    finally:
        if _analyzer_instance:
            # 一時ディレクトリのクリーンアップは、システムに任せるか、必要に応じて追加
            # ここでは、システムのtempfileモジュールが自動的に管理するため、明示的に削除はしない
            # もし、システムのtempfileが使い果たされた場合は、ここでエラーが発生する可能性がある
            # ただし、このスクリプトでは、tempfile.mkdtemp()を使用しているため、
            # スクリプト終了時に自動的に削除される。
            pass 
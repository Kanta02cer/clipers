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

# AI分析・ロジック関連
from gemini_analyzer import GeminiAnalyzer
from analysis_logic import VVPScoreCalculator
from content_analyzer import ContentAnalyzer

# 設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
        
        # 各コンポーネントを初期化
        self.youtube_client = self._init_youtube_client(youtube_api_key)
        self.gemini_analyzer = GeminiAnalyzer(gemini_api_key)
        self.vvp_calculator = VVPScoreCalculator()
        self.content_analyzer = ContentAnalyzer()
        
        self.temp_dir = tempfile.mkdtemp(prefix='youtube_analyzer_')
        logger.info(f"一時ディレクトリ作成: {self.temp_dir}")

    def _init_youtube_client(self, api_key: str):
        try:
            client = build('youtube', 'v3', developerKey=api_key)
            logger.info("YouTube APIクライアント初期化成功")
            return client
        except Exception as e:
            logger.error(f"YouTube APIクライアント初期化エラー: {e}")
            raise

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        YouTube URLから動画IDを抽出
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
        """
        if not self.youtube_client:
            raise Exception("YouTube APIクライアントが初期化されていません")
        
        try:
            # 動画情報
            video_response = self.youtube_client.videos().list(
                part='snippet,statistics,contentDetails', id=video_id
            ).execute()
            if not video_response.get('items'):
                raise Exception(f"動画が見つかりません: {video_id}")
            video_data = video_response['items'][0]

            # チャンネル情報
            channel_id = video_data['snippet']['channelId']
            channel_response = self.youtube_client.channels().list(
                part='snippet,statistics', id=channel_id
            ).execute()
            channel_data = channel_response['items'][0] if channel_response.get('items') else {}

            # コメント取得
            comments = []
            try:
                comment_response = self.youtube_client.commentThreads().list(
                    part='snippet', videoId=video_id, maxResults=100, order='relevance'
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
                logger.warning(f"コメント取得エラー: {e} (コメントが無効になっている可能性があります)")

            return self._format_video_info(video_data, channel_data, comments)
        except Exception as e:
            logger.error(f"動画情報取得中にエラーが発生しました: {e}")
            raise

    def _format_video_info(self, video_data, channel_data, comments):
        snippet = video_data.get('snippet', {})
        stats = video_data.get('statistics', {})
        details = video_data.get('contentDetails', {})
        ch_snippet = channel_data.get('snippet', {})
        ch_stats = channel_data.get('statistics', {})

        return {
            'video_id': video_data.get('id'),
            'title': snippet.get('title'),
            'description': snippet.get('description'),
            'published_at': snippet.get('publishedAt'),
            'channel_id': snippet.get('channelId'),
            'channel_title': snippet.get('channelTitle'),
            'tags': snippet.get('tags', []),
            'view_count': int(stats.get('viewCount', 0)),
            'like_count': int(stats.get('likeCount', 0)),
            'comment_count': int(stats.get('commentCount', 0)),
            'duration_iso': details.get('duration', 'PT0S'),
            'duration_sec': self._convert_iso8601_duration(details.get('duration', 'PT0S')),
            'comments': comments,
            'channel_info': {
                'title': ch_snippet.get('title'),
                'subscriber_count': int(ch_stats.get('subscriberCount', 0)),
                'video_count': int(ch_stats.get('videoCount', 0)),
                'view_count': int(ch_stats.get('viewCount', 0)),
            }
        }

    def _convert_iso8601_duration(self, duration_str: str) -> int:
        """ISO 8601形式の時間を秒に変換"""
        if not duration_str.startswith('PT'):
            return 0
        
        duration_str = duration_str[2:]
        total_seconds = 0
        
        time_matches = re.match(r'(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
        if time_matches:
            hours = int(time_matches.group(1) or 0)
            minutes = int(time_matches.group(2) or 0)
            seconds = int(time_matches.group(3) or 0)
            total_seconds = hours * 3600 + minutes * 60 + seconds
            
        return total_seconds

    def download_video(self, url: str, output_format: str = 'mp4') -> Dict[str, Any]:
        """
        yt-dlpを使用して動画と関連情報をダウンロード
        """
        video_id = self.extract_video_id(url)
        if not video_id:
            raise ValueError("無効なYouTube URLです")

        output_path = os.path.join(self.temp_dir, f"{video_id}.{output_format}")
        
        ydl_opts = {
            'format': f'bestvideo[ext={output_format}]+bestaudio/best[ext={output_format}]/best',
            'outtmpl': os.path.join(self.temp_dir, f'{video_id}.%(ext)s'),
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['ja', 'en'],
            'subtitlesformat': 'vtt',
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': output_format,
        }
        
        logger.info(f"動画ダウンロード開始: {url}")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # 実際のファイルパスを特定
                actual_video_path = ydl.prepare_filename(info)
                subtitle_path = self._find_file_by_extension(video_id, '.vtt')

                logger.info(f"動画ダウンロード完了: {actual_video_path}")
                return {
                    'success': True,
                    'video_path': actual_video_path,
                    'subtitle_path': subtitle_path,
                    'duration': info.get('duration', 0),
                    'title': info.get('title', ''),
                }
        except Exception as e:
            logger.error(f"動画ダウンロードエラー: {e}")
            return {'success': False, 'error': str(e)}

    def _find_file_by_extension(self, video_id: str, extension: str) -> Optional[str]:
        """指定された拡張子のファイルを一時ディレクトリから探す"""
        for lang in ['ja', 'en']:
            expected_path = os.path.join(self.temp_dir, f"{video_id}.{lang}{extension}")
            if os.path.exists(expected_path):
                return expected_path
        # 言語指定なしのパスも確認
        expected_path = os.path.join(self.temp_dir, f"{video_id}{extension}")
        if os.path.exists(expected_path):
            return expected_path
        return None

    def parse_subtitle(self, subtitle_path: str) -> str:
        """
        字幕ファイル(VTT)を解析してテキストを抽出
        """
        if not subtitle_path or not os.path.exists(subtitle_path):
            return ""
        try:
            with open(subtitle_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # タイムスタンプ行と空行を除外
            text_lines = [line.strip() for line in lines if line.strip() and '-->' not in line and not line.strip().isdigit() and 'WEBVTT' not in line]
            
            # 重複するテキスト行を削除
            unique_lines = []
            for line in text_lines:
                if not unique_lines or unique_lines[-1] != line:
                    unique_lines.append(line)

            return ' '.join(unique_lines)
        except Exception as e:
            logger.error(f"字幕解析エラー: {e}")
            return ""

    def analyze_video_comprehensive(self, url: str, download_video: bool = True) -> Dict[str, Any]:
        """
        動画の包括的分析を実行し、指定された形式で結果を返す
        """
        start_time = datetime.now()
        logger.info(f"包括的分析開始: {url}")
        
        video_id = self.extract_video_id(url)
        if not video_id:
            raise ValueError("無効なYouTube URLです")

        # 1. 動画情報取得
        video_info = self.get_video_info(video_id)
        
        # 2. 動画ダウンロードと字幕取得
        subtitle_text = ""
        technical_quality_score = 50.0 # デフォルト値
        if download_video:
            download_result = self.download_video(url)
            if download_result.get('success'):
                subtitle_text = self.parse_subtitle(download_result.get('subtitle_path'))
                # ここで技術品質を評価するロジックを追加可能 (今回はダミー)
                technical_quality_score = 85.0 # ダウンロード成功時の仮スコア
            else:
                logger.warning("動画のダウンロードに失敗したため、字幕なしで分析を続行します。")

        # 3. Geminiによる包括的分析
        gemini_full_analysis = self.gemini_analyzer.analyze_video_fully(
            transcript=subtitle_text,
            comments=video_info.get('comments', []),
            video_duration=video_info.get('duration_sec', 0)
        )
        if "error" in gemini_full_analysis:
            logger.error(f"Gemini分析でエラー: {gemini_full_analysis['error']}")
            # エラー時でも処理を続けるためにデフォルト構造を返す
            raise Exception(f"Gemini analysis failed: {gemini_full_analysis['error']}")

        # 4. VVPスコア計算
        vvp_score_result = self.vvp_calculator.calculate_vvp_score(
            gemini_kpis=gemini_full_analysis.get('vvp_scores', {}),
            tech_quality_score=technical_quality_score
        )

        # 5. 切り抜き候補ランキング生成
        engagement_hotspots = self.vvp_calculator.extract_timestamps_from_comments(video_info.get('comments', []))
        gemini_hotspots = gemini_full_analysis.get('top_clips_semantic_analysis', [])
        clip_ranking = self.vvp_calculator.calculate_clip_scores(engagement_hotspots, gemini_hotspots)

        # 6. エンゲージメント指標と感情分析
        engagement_metrics = self.vvp_calculator.calculate_engagement_metrics(video_info.get('comments', []))
        
        # 7. 最終出力の整形
        final_report = {
            "vvp_score": vvp_score_result.get('total_vvp_score'),
            "vvp_score_details": vvp_score_result,
            "golden_clip_suggestion": gemini_full_analysis.get('golden_clip_suggestion'),
            "clip_candidates_ranking": clip_ranking[:10], # 上位10件
            "sentiment_analysis": {
                "sentiment_distribution": engagement_metrics.get('sentiment_distribution'),
                "summary": f"コメント総数{engagement_metrics.get('total_comments')}件に基づく感情分析結果です。"
            },
            "engagement_metrics": engagement_metrics,
            "technical_quality_assessment": {
                "score": technical_quality_score,
                "summary": "動画ファイルに基づく技術評価です。" + ("(ダウンロード未実施のためダミー値)" if not download_video else "")
            },
            "full_gemini_analysis": gemini_full_analysis, # 詳細なGemini分析結果も格納
            "source_video_info": video_info,
        }
        
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"包括的分析完了。処理時間: {processing_time:.2f}秒")
        
        return final_report

# グローバルインスタンス管理
_analyzer_instance = None

def get_analyzer_instance(youtube_api_key: str, gemini_api_key: str) -> "IntegratedYouTubeAnalyzer":
    """
    分析器インスタンスを取得（シングルトンパターン）
    """
    global _analyzer_instance
    if _analyzer_instance is None or _analyzer_instance.youtube_api_key != youtube_api_key:
        logger.info("新しい統合分析器インスタンスを作成します。")
        _analyzer_instance = IntegratedYouTubeAnalyzer(youtube_api_key, gemini_api_key)
    return _analyzer_instance

if __name__ == '__main__':
    # テスト実行用のコード
    if len(sys.argv) < 4:
        print("使用方法: python youtube_analyzer_integrated.py <YouTube_URL> <YouTube_API_Key> <Gemini_API_Key>")
        sys.exit(1)
    
    test_url = sys.argv[1]
    test_yt_key = sys.argv[2]
    test_gemini_key = sys.argv[3]
    
    print("統合YouTube動画分析システム - テスト実行")
    print("=" * 60)
    
    try:
        analyzer = get_analyzer_instance(test_yt_key, test_gemini_key)
        final_result = analyzer.analyze_video_comprehensive(test_url, download_video=True)
        
        # 結果を読みやすい形式で出力
        print("\n--- 最終分析レポート ---")
        print(f"📈 総合VVPスコア: {final_result['vvp_score']}/100")
        
        print("\n💎 ゴールデンクリップ提案:")
        golden_clip = final_result['golden_clip_suggestion']
        print(f"   - 時間: {golden_clip.get('time_range', 'N/A')}")
        print(f"   - 理由: {golden_clip.get('reason', 'N/A')}")

        print("\n🎬 切り抜き候補トップ5:")
        for i, clip in enumerate(final_result['clip_candidates_ranking'][:5]):
            print(f"   {i+1}. [{clip.get('clip_score')}点] {clip.get('formatted_time', 'N/A')} - {clip.get('reason', 'N/A')} ({clip.get('mention_count')}回言及)")

        print("\n❤️ 感情分析:")
        sentiment = final_result['sentiment_analysis']['sentiment_distribution']
        print(f"   - ポジティブ: {sentiment.get('positive', 0):.1%}")
        print(f"   - ネガティブ: {sentiment.get('negative', 0):.1%}")
        print(f"   - ニュートラル: {sentiment.get('neutral', 0):.1%}")

        print("\n📊 エンゲージメント指標:")
        engagement = final_result['engagement_metrics']
        print(f"   - 総コメント数: {engagement.get('total_comments')}")
        print(f"   - 総いいね数（コメント）: {engagement.get('total_likes')}")
        print("-" * 25)

    except Exception as e:
        logger.error(f"テスト実行中にエラーが発生しました: {e}", exc_info=True)
    finally:
        # 一時ファイルのクリーンアップ
        if _analyzer_instance and os.path.exists(_analyzer_instance.temp_dir):
            import shutil
            shutil.rmtree(_analyzer_instance.temp_dir)
            logger.info(f"一時ディレクトリをクリーンアップしました: {_analyzer_instance.temp_dir}") 
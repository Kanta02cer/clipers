#!/usr/bin/env python3
"""
YouTube動画コンテンツ分析器
音声内容、発言、字幕の詳細分析を行う
"""

import os
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import re
from datetime import datetime

# 音声処理関連
import speech_recognition as sr
from pydub import AudioSegment
import whisper

# 自然言語処理
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer

# 設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentAnalyzer:
    """YouTube動画のコンテンツ分析器"""
    
    def __init__(self):
        """初期化"""
        self.recognizer = sr.Recognizer()
        self.whisper_model = None
        self.nltk_downloaded = False
        
        # NLTKデータのダウンロード
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('vader_lexicon')
            self.nltk_downloaded = True
        except LookupError:
            logger.info("NLTKデータをダウンロード中...")
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('vader_lexicon', quiet=True)
                self.nltk_downloaded = True
                logger.info("NLTKデータのダウンロード完了")
            except Exception as e:
                logger.warning(f"NLTKデータのダウンロードに失敗: {e}")
    
    def extract_audio_from_video(self, video_path: str, output_path: str = None) -> str:
        """
        動画から音声を抽出
        
        Args:
            video_path: 動画ファイルのパス
            output_path: 出力音声ファイルのパス（オプション）
            
        Returns:
            音声ファイルのパス
        """
        try:
            if not output_path:
                output_path = video_path.replace('.mp4', '_audio.wav')
            
            logger.info(f"音声抽出開始: {video_path}")
            
            # ffmpegを使用して音声を抽出
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vn',  # ビデオストリームを無効化
                '-acodec', 'pcm_s16le',  # PCM 16bit
                '-ar', '16000',  # サンプリングレート 16kHz
                '-ac', '1',  # モノラル
                '-y',  # 上書き
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"音声抽出完了: {output_path}")
                return output_path
            else:
                logger.error(f"音声抽出エラー: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"音声抽出エラー: {e}")
            return None
    
    def transcribe_audio_whisper(self, audio_path: str, language: str = 'ja') -> Dict[str, Any]:
        """
        Whisperを使用して音声を文字起こし
        
        Args:
            audio_path: 音声ファイルのパス
            language: 言語コード
            
        Returns:
            文字起こし結果
        """
        try:
            logger.info(f"Whisper文字起こし開始: {audio_path}")
            
            # Whisperモデルの読み込み
            if not self.whisper_model:
                self.whisper_model = whisper.load_model("base")
            
            # 文字起こし実行
            result = self.whisper_model.transcribe(
                audio_path,
                language=language,
                verbose=False
            )
            
            logger.info("Whisper文字起こし完了")
            
            return {
                'text': result['text'],
                'segments': result['segments'],
                'language': result['language'],
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Whisper文字起こしエラー: {e}")
            return {
                'text': '',
                'segments': [],
                'language': language,
                'success': False,
                'error': str(e)
            }
    
    def transcribe_audio_speech_recognition(self, audio_path: str, language: str = 'ja-JP') -> Dict[str, Any]:
        """
        Speech Recognitionを使用して音声を文字起こし
        
        Args:
            audio_path: 音声ファイルのパス
            language: 言語コード
            
        Returns:
            文字起こし結果
        """
        try:
            logger.info(f"Speech Recognition文字起こし開始: {audio_path}")
            
            with sr.AudioFile(audio_path) as source:
                audio = self.recognizer.record(source)
                
                # Google Speech Recognitionを使用
                text = self.recognizer.recognize_google(
                    audio,
                    language=language
                )
                
                logger.info("Speech Recognition文字起こし完了")
                
                return {
                    'text': text,
                    'segments': [],
                    'language': language,
                    'success': True
                }
                
        except sr.UnknownValueError:
            logger.warning("音声が認識できませんでした")
            return {
                'text': '',
                'segments': [],
                'language': language,
                'success': False,
                'error': '音声が認識できませんでした'
            }
        except sr.RequestError as e:
            logger.error(f"Speech Recognition APIエラー: {e}")
            return {
                'text': '',
                'segments': [],
                'language': language,
                'success': False,
                'error': f'APIエラー: {e}'
            }
        except Exception as e:
            logger.error(f"Speech Recognition文字起こしエラー: {e}")
            return {
                'text': '',
                'segments': [],
                'language': language,
                'success': False,
                'error': str(e)
            }
    
    def analyze_content_quality(self, text: str, segments: List[Dict] = None) -> Dict[str, Any]:
        """
        コンテンツの質を分析
        
        Args:
            text: 文字起こしテキスト
            segments: セグメント情報
            
        Returns:
            分析結果
        """
        try:
            if not text.strip():
                return {
                    'content_score': 0,
                    'speech_clarity': 0,
                    'content_structure': 0,
                    'engagement_factors': 0,
                    'overall_quality': 0,
                    'analysis': 'テキストが空のため分析できません'
                }
            
            # 基本統計
            sentences = sent_tokenize(text) if self.nltk_downloaded else text.split('。')
            words = word_tokenize(text) if self.nltk_downloaded else text.split()
            
            # コンテンツスコア計算
            content_score = self._calculate_content_score(text, sentences, words)
            speech_clarity = self._calculate_speech_clarity(text, segments)
            content_structure = self._calculate_content_structure(sentences)
            engagement_factors = self._calculate_engagement_factors(text)
            
            # 総合品質スコア
            overall_quality = (content_score + speech_clarity + content_structure + engagement_factors) / 4
            
            return {
                'content_score': round(content_score, 2),
                'speech_clarity': round(speech_clarity, 2),
                'content_structure': round(content_structure, 2),
                'engagement_factors': round(engagement_factors, 2),
                'overall_quality': round(overall_quality, 2),
                'statistics': {
                    'total_words': len(words),
                    'total_sentences': len(sentences),
                    'average_sentence_length': len(words) / len(sentences) if sentences else 0,
                    'speech_duration': self._calculate_speech_duration(segments)
                },
                'analysis': self._generate_content_analysis(text, sentences, words)
            }
            
        except Exception as e:
            logger.error(f"コンテンツ分析エラー: {e}")
            return {
                'content_score': 0,
                'speech_clarity': 0,
                'content_structure': 0,
                'engagement_factors': 0,
                'overall_quality': 0,
                'analysis': f'分析エラー: {str(e)}'
            }
    
    def analyze_speech_patterns(self, text: str, segments: List[Dict] = None) -> Dict[str, Any]:
        """
        発言パターンを分析
        
        Args:
            text: 文字起こしテキスト
            segments: セグメント情報
            
        Returns:
            発言パターン分析結果
        """
        try:
            if not text.strip():
                return {
                    'speech_patterns': [],
                    'key_phrases': [],
                    'speech_rhythm': 0,
                    'analysis': 'テキストが空のため分析できません'
                }
            
            # キーフレーズ抽出
            key_phrases = self._extract_key_phrases(text)
            
            # 発言リズム分析
            speech_rhythm = self._analyze_speech_rhythm(segments)
            
            # 発言パターン識別
            speech_patterns = self._identify_speech_patterns(text)
            
            return {
                'speech_patterns': speech_patterns,
                'key_phrases': key_phrases,
                'speech_rhythm': round(speech_rhythm, 2),
                'analysis': self._generate_speech_analysis(text, key_phrases, speech_patterns)
            }
            
        except Exception as e:
            logger.error(f"発言パターン分析エラー: {e}")
            return {
                'speech_patterns': [],
                'key_phrases': [],
                'speech_rhythm': 0,
                'analysis': f'分析エラー: {str(e)}'
            }
    
    def _calculate_content_score(self, text: str, sentences: List[str], words: List[str]) -> float:
        """コンテンツスコアを計算"""
        try:
            # 基本的な品質指標
            word_count = len(words)
            sentence_count = len(sentences)
            
            if word_count == 0 or sentence_count == 0:
                return 0
            
            # 平均文長（適切な範囲: 10-30語）
            avg_sentence_length = word_count / sentence_count
            length_score = max(0, 10 - abs(avg_sentence_length - 20) / 2)
            
            # 語彙の多様性
            unique_words = len(set(words))
            vocabulary_diversity = unique_words / word_count if word_count > 0 else 0
            diversity_score = min(10, vocabulary_diversity * 20)
            
            # 文の構造の複雑さ
            complex_sentences = sum(1 for s in sentences if len(s.split()) > 15)
            complexity_score = min(10, (complex_sentences / sentence_count) * 20)
            
            return (length_score + diversity_score + complexity_score) / 3
            
        except Exception as e:
            logger.error(f"コンテンツスコア計算エラー: {e}")
            return 0
    
    def _calculate_speech_clarity(self, text: str, segments: List[Dict] = None) -> float:
        """発言の明確性を計算"""
        try:
            if not text.strip():
                return 0
            
            # 基本的な明確性指標
            clarity_score = 0
            
            # 句読点の使用
            punctuation_count = len(re.findall(r'[。、！？]', text))
            word_count = len(text.split())
            punctuation_ratio = punctuation_count / word_count if word_count > 0 else 0
            clarity_score += min(5, punctuation_ratio * 50)
            
            # 繰り返し表現の検出
            words = text.split()
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            repetition_penalty = 0
            for word, freq in word_freq.items():
                if freq > 3 and len(word) > 2:  # 3回以上出現する2文字以上の単語
                    repetition_penalty += (freq - 3) * 0.5
            
            clarity_score = max(0, clarity_score - repetition_penalty)
            
            return min(10, clarity_score)
            
        except Exception as e:
            logger.error(f"発言明確性計算エラー: {e}")
            return 0
    
    def _calculate_content_structure(self, sentences: List[str]) -> float:
        """コンテンツ構造を評価"""
        try:
            if not sentences:
                return 0
            
            structure_score = 0
            
            # 文の長さの多様性
            sentence_lengths = [len(s.split()) for s in sentences]
            length_variance = sum((l - sum(sentence_lengths)/len(sentence_lengths))**2 for l in sentence_lengths) / len(sentence_lengths)
            structure_score += min(5, length_variance / 10)
            
            # 文の開始パターン
            start_patterns = {}
            for sentence in sentences:
                if sentence.strip():
                    first_word = sentence.strip().split()[0] if sentence.strip().split() else ''
                    start_patterns[first_word] = start_patterns.get(first_word, 0) + 1
            
            pattern_diversity = len(start_patterns) / len(sentences) if sentences else 0
            structure_score += min(5, pattern_diversity * 10)
            
            return min(10, structure_score)
            
        except Exception as e:
            logger.error(f"コンテンツ構造計算エラー: {e}")
            return 0
    
    def _calculate_engagement_factors(self, text: str) -> float:
        """エンゲージメント要因を計算"""
        try:
            if not text.strip():
                return 0
            
            engagement_score = 0
            
            # 質問文の検出
            question_count = len(re.findall(r'[？?]', text))
            engagement_score += min(3, question_count * 0.5)
            
            # 感嘆文の検出
            exclamation_count = len(re.findall(r'[！!]', text))
            engagement_score += min(3, exclamation_count * 0.3)
            
            # 感情表現の検出
            emotion_words = ['すごい', '素晴らしい', '感動', '面白い', '楽しい', '驚き', '感動的']
            emotion_count = sum(1 for word in emotion_words if word in text)
            engagement_score += min(4, emotion_count * 0.5)
            
            return min(10, engagement_score)
            
        except Exception as e:
            logger.error(f"エンゲージメント要因計算エラー: {e}")
            return 0
    
    def _calculate_speech_duration(self, segments: List[Dict] = None) -> float:
        """発言時間を計算"""
        try:
            if not segments:
                return 0
            
            total_duration = 0
            for segment in segments:
                if 'end' in segment and 'start' in segment:
                    total_duration += segment['end'] - segment['start']
            
            return total_duration
            
        except Exception as e:
            logger.error(f"発言時間計算エラー: {e}")
            return 0
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """キーフレーズを抽出"""
        try:
            # 基本的なキーフレーズ抽出
            sentences = sent_tokenize(text) if self.nltk_downloaded else text.split('。')
            
            key_phrases = []
            for sentence in sentences:
                if len(sentence.strip()) > 10:  # 10文字以上の文のみ
                    # 重要な表現を検出
                    if any(word in sentence for word in ['重要', 'ポイント', '要点', '結論', 'まとめ']):
                        key_phrases.append(sentence.strip())
            
            return key_phrases[:5]  # 上位5つまで
            
        except Exception as e:
            logger.error(f"キーフレーズ抽出エラー: {e}")
            return []
    
    def _analyze_speech_rhythm(self, segments: List[Dict] = None) -> float:
        """発言リズムを分析"""
        try:
            if not segments:
                return 0
            
            # 発言の間隔を分析
            intervals = []
            for i in range(1, len(segments)):
                if 'start' in segments[i] and 'end' in segments[i-1]:
                    interval = segments[i]['start'] - segments[i-1]['end']
                    intervals.append(interval)
            
            if not intervals:
                return 0
            
            # 平均間隔の逆数（リズムスコア）
            avg_interval = sum(intervals) / len(intervals)
            rhythm_score = 10 / (1 + avg_interval) if avg_interval > 0 else 10
            
            return min(10, rhythm_score)
            
        except Exception as e:
            logger.error(f"発言リズム分析エラー: {e}")
            return 0
    
    def _identify_speech_patterns(self, text: str) -> List[str]:
        """発言パターンを識別"""
        try:
            patterns = []
            
            # 繰り返しパターン
            words = text.split()
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            repeated_words = [word for word, freq in word_freq.items() if freq > 2 and len(word) > 1]
            if repeated_words:
                patterns.append(f"繰り返し表現: {', '.join(repeated_words[:3])}")
            
            # 質問パターン
            question_count = len(re.findall(r'[？?]', text))
            if question_count > 0:
                patterns.append(f"質問形式: {question_count}回")
            
            # 感嘆パターン
            exclamation_count = len(re.findall(r'[！!]', text))
            if exclamation_count > 0:
                patterns.append(f"感嘆表現: {exclamation_count}回")
            
            return patterns
            
        except Exception as e:
            logger.error(f"発言パターン識別エラー: {e}")
            return []
    
    def _generate_content_analysis(self, text: str, sentences: List[str], words: List[str]) -> str:
        """コンテンツ分析レポートを生成"""
        try:
            analysis = []
            
            # 基本統計
            analysis.append(f"総文字数: {len(text)}文字")
            analysis.append(f"総単語数: {len(words)}語")
            analysis.append(f"総文数: {len(sentences)}文")
            
            if sentences:
                avg_sentence_length = len(words) / len(sentences)
                analysis.append(f"平均文長: {avg_sentence_length:.1f}語")
            
            # 語彙の多様性
            unique_words = len(set(words))
            vocabulary_diversity = unique_words / len(words) if words else 0
            analysis.append(f"語彙多様性: {vocabulary_diversity:.2f}")
            
            # 文の構造
            long_sentences = sum(1 for s in sentences if len(s.split()) > 20)
            short_sentences = sum(1 for s in sentences if len(s.split()) < 10)
            analysis.append(f"長文: {long_sentences}文, 短文: {short_sentences}文")
            
            return " | ".join(analysis)
            
        except Exception as e:
            logger.error(f"コンテンツ分析レポート生成エラー: {e}")
            return "分析レポート生成エラー"
    
    def _generate_speech_analysis(self, text: str, key_phrases: List[str], speech_patterns: List[str]) -> str:
        """発言分析レポートを生成"""
        try:
            analysis = []
            
            # キーフレーズ
            if key_phrases:
                analysis.append(f"キーフレーズ: {len(key_phrases)}個")
            
            # 発言パターン
            if speech_patterns:
                analysis.append(f"発言パターン: {len(speech_patterns)}種類")
            
            # 感情表現
            emotion_words = ['すごい', '素晴らしい', '感動', '面白い', '楽しい', '驚き', '感動的']
            emotion_count = sum(1 for word in emotion_words if word in text)
            analysis.append(f"感情表現: {emotion_count}回")
            
            return " | ".join(analysis)
            
        except Exception as e:
            logger.error(f"発言分析レポート生成エラー: {e}")
            return "発言分析レポート生成エラー"
    
    def analyze_video_content(self, video_path: str, subtitle_text: str = "") -> Dict[str, Any]:
        """
        動画コンテンツの包括的分析
        
        Args:
            video_path: 動画ファイルのパス
            subtitle_text: 字幕テキスト（オプション）
            
        Returns:
            包括的分析結果
        """
        try:
            logger.info(f"動画コンテンツ分析開始: {video_path}")
            
            result = {
                'success': False,
                'audio_transcription': None,
                'content_quality': None,
                'speech_patterns': None,
                'subtitle_analysis': None,
                'overall_assessment': None
            }
            
            # 音声抽出
            audio_path = self.extract_audio_from_video(video_path)
            if not audio_path:
                result['error'] = '音声抽出に失敗しました'
                return result
            
            # 音声文字起こし（Whisper優先）
            transcription = self.transcribe_audio_whisper(audio_path)
            if not transcription['success']:
                # Whisperが失敗した場合、Speech Recognitionを試行
                transcription = self.transcribe_audio_speech_recognition(audio_path)
            
            result['audio_transcription'] = transcription
            
            # コンテンツ品質分析
            if transcription['success']:
                result['content_quality'] = self.analyze_content_quality(
                    transcription['text'], 
                    transcription.get('segments', [])
                )
                
                result['speech_patterns'] = self.analyze_speech_patterns(
                    transcription['text'], 
                    transcription.get('segments', [])
                )
            
            # 字幕分析（字幕がある場合）
            if subtitle_text:
                result['subtitle_analysis'] = self.analyze_content_quality(subtitle_text)
            
            # 総合評価
            result['overall_assessment'] = self._generate_overall_assessment(result)
            result['success'] = True
            
            # 一時ファイルの削除
            try:
                os.remove(audio_path)
            except:
                pass
            
            logger.info("動画コンテンツ分析完了")
            return result
            
        except Exception as e:
            logger.error(f"動画コンテンツ分析エラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_overall_assessment(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """総合評価を生成"""
        try:
            assessment = {
                'overall_score': 0,
                'strengths': [],
                'weaknesses': [],
                'recommendations': []
            }
            
            # スコア計算
            scores = []
            
            if analysis_result.get('content_quality'):
                scores.append(analysis_result['content_quality']['overall_quality'])
            
            if analysis_result.get('subtitle_analysis'):
                scores.append(analysis_result['subtitle_analysis']['overall_quality'])
            
            if scores:
                assessment['overall_score'] = sum(scores) / len(scores)
            
            # 強み・弱みの分析
            if analysis_result.get('content_quality'):
                quality = analysis_result['content_quality']
                
                if quality['content_score'] > 7:
                    assessment['strengths'].append('コンテンツの質が高い')
                elif quality['content_score'] < 4:
                    assessment['weaknesses'].append('コンテンツの質を改善する必要がある')
                
                if quality['speech_clarity'] > 7:
                    assessment['strengths'].append('発言が明確')
                elif quality['speech_clarity'] < 4:
                    assessment['weaknesses'].append('発言の明確性を向上させる必要がある')
                
                if quality['engagement_factors'] > 7:
                    assessment['strengths'].append('エンゲージメント要因が豊富')
                elif quality['engagement_factors'] < 4:
                    assessment['weaknesses'].append('エンゲージメント要因を増やす必要がある')
            
            # 推奨事項
            if not assessment['strengths']:
                assessment['recommendations'].append('全体的な品質向上が必要です')
            
            if assessment['weaknesses']:
                assessment['recommendations'].extend([
                    '発言の明確性を向上させる',
                    'エンゲージメント要因を増やす',
                    'コンテンツ構造を改善する'
                ])
            
            return assessment
            
        except Exception as e:
            logger.error(f"総合評価生成エラー: {e}")
            return {
                'overall_score': 0,
                'strengths': [],
                'weaknesses': [],
                'recommendations': ['評価生成エラー']
            } 
import librosa
import numpy as np
from typing import Dict, List, Tuple
import json

class AudioAnalyzer:
    def __init__(self):
        self.sample_rate = 22050  # 標準的なサンプルレート
        
    def analyze_audio(self, audio_file_path: str) -> Dict:
        """
        音声ファイルを分析して盛り上がりポイントを特定
        """
        try:
            # 音声ファイルを読み込み
            y, sr = librosa.load(audio_file_path, sr=self.sample_rate)
            
            # 基本情報
            duration = librosa.get_duration(y=y, sr=sr)
            
            # 音量分析
            rms = librosa.feature.rms(y=y)[0]
            db = librosa.amplitude_to_db(rms)
            
            # 音声の感情分析（音調）
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_mean = np.mean(pitches, axis=0)
            
            # 盛り上がりポイントの特定
            excitement_points = self._find_excitement_points(db, pitch_mean, duration)
            
            return {
                "duration": duration,
                "sample_rate": sr,
                "volume_analysis": {
                    "mean_volume": float(np.mean(db)),
                    "max_volume": float(np.max(db)),
                    "volume_variance": float(np.var(db))
                },
                "pitch_analysis": {
                    "mean_pitch": float(np.mean(pitch_mean)),
                    "pitch_variance": float(np.var(pitch_mean))
                },
                "excitement_points": excitement_points,
                "overall_excitement_score": self._calculate_excitement_score(db, pitch_mean)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _find_excitement_points(self, db: np.ndarray, pitch_mean: np.ndarray, duration: float) -> List[Dict]:
        """
        盛り上がりポイントを特定（改善版）
        """
        excitement_points = []
        
        # より緩い閾値で音量の変化を検出
        volume_threshold = np.mean(db) + 0.5 * np.std(db)  # 閾値を緩和
        high_volume_indices = np.where(db > volume_threshold)[0]
        
        # 時間軸に変換
        time_points = high_volume_indices / len(db) * duration
        
        # 連続したポイントをグループ化
        if len(time_points) > 0:
            groups = []
            current_group = [time_points[0]]
            
            for i in range(1, len(time_points)):
                if time_points[i] - time_points[i-1] < 3.0:  # 3秒以内に緩和
                    current_group.append(time_points[i])
                else:
                    if len(current_group) > 0:
                        groups.append(current_group)
                    current_group = [time_points[i]]
            
            if len(current_group) > 0:
                groups.append(current_group)
            
            # 各グループの中心点を盛り上がりポイントとして記録
            for group in groups:
                if len(group) > 3:  # 3ポイント以上連続に緩和
                    center_time = np.mean(group)
                    excitement_points.append({
                        "time": round(center_time, 2),
                        "duration": round(group[-1] - group[0], 2),
                        "intensity": min(1.0, len(group) / 5.0)  # 強度を調整
                    })
        
        # 音調の変化も考慮
        if len(pitch_mean) > 0:
            pitch_threshold = np.mean(pitch_mean) + 0.5 * np.std(pitch_mean)
            high_pitch_indices = np.where(pitch_mean > pitch_threshold)[0]
            
            if len(high_pitch_indices) > 0:
                pitch_time_points = high_pitch_indices / len(pitch_mean) * duration
                
                # 音調の盛り上がりポイントも追加
                for i in range(0, len(pitch_time_points), 50):  # 50フレームごとにサンプリング
                    if i < len(pitch_time_points):
                        excitement_points.append({
                            "time": round(pitch_time_points[i], 2),
                            "duration": 2.0,
                            "intensity": 0.5,
                            "type": "pitch"
                        })
        
        # 時間順にソートして上位10個を返す
        excitement_points.sort(key=lambda x: x["time"])
        return excitement_points[:10]
    
    def _calculate_excitement_score(self, db: np.ndarray, pitch_mean: np.ndarray) -> float:
        """
        全体的な盛り上がりスコアを計算
        """
        # 音量の変動
        volume_variance = np.var(db)
        
        # 音調の変動
        pitch_variance = np.var(pitch_mean)
        
        # スコアを正規化（0-100）
        score = (volume_variance * 0.7 + pitch_variance * 0.3) / 100
        return min(100.0, max(0.0, score)) 
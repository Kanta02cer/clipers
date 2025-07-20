from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import os
import tempfile
from typing import Optional, List
import json
from audio_analyzer import AudioAnalyzer
from visualization import AudioVisualizer

app = FastAPI(title="YouTube盛り上がり分析ツール (Simple)", version="1.0.0")

# CORS設定を追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切なオリジンを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

class VideoInfo(BaseModel):
    title: str
    duration: Optional[int]
    description: Optional[str]
    view_count: Optional[int]
    like_count: Optional[int]

class AudioAnalysisRequest(BaseModel):
    url: str
    download_audio: bool = True

class AudioAnalysisResponse(BaseModel):
    video_info: VideoInfo
    audio_file_path: Optional[str]
    audio_duration: Optional[float]
    sample_rate: Optional[int]
    debug_info: dict

@app.get("/")
async def root():
    return {"message": "YouTube盛り上がり分析ツール API (Simple)"}

@app.post("/download-audio-simple", response_model=AudioAnalysisResponse)
async def download_audio_simple(request: AudioAnalysisRequest):
    """
    シンプル版：YouTube動画から音声をダウンロードする
    """
    debug_info = {}
    
    try:
        # 一時ディレクトリを作成
        temp_dir = tempfile.mkdtemp()
        debug_info['temp_dir'] = temp_dir
        print(f"一時ディレクトリ作成: {temp_dir}")
        
        # シンプルなyt-dlpの設定
        ydl_opts = {
            'format': 'bestaudio/best',  # 最もシンプルな設定
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            'quiet': False,
            'no_warnings': False,
        }
        
        debug_info['ydl_opts'] = ydl_opts
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 動画情報を取得
            print("動画情報を取得中...")
            info = ydl.extract_info(request.url, download=False)
            
            debug_info['video_info'] = {
                'title': info.get('title'),
                'duration': info.get('duration'),
            }
            
            # 音声をダウンロード
            if request.download_audio:
                print("音声ダウンロード開始...")
                try:
                    ydl.download([request.url])
                    print("ダウンロード完了")
                except Exception as download_error:
                    debug_info['download_error'] = str(download_error)
                    print(f"ダウンロードエラー: {download_error}")
                
                # ダウンロードされたファイルを探す
                print(f"ダウンロード後のファイル一覧: {os.listdir(temp_dir)}")
                all_files = os.listdir(temp_dir)
                debug_info['all_files'] = all_files
                
                # 音声ファイルを探す
                audio_files = [f for f in all_files if f.endswith('.wav')]
                debug_info['audio_files_found'] = audio_files
                
                if audio_files:
                    audio_file_path = os.path.join(temp_dir, audio_files[0])
                    debug_info['audio_file_path'] = audio_file_path
                else:
                    audio_file_path = None
                    debug_info['error'] = "音声ファイルが見つかりません"
            else:
                audio_file_path = None
            
            return AudioAnalysisResponse(
                video_info=VideoInfo(
                    title=info.get('title', ''),
                    duration=info.get('duration'),
                    description=info.get('description', ''),
                    view_count=info.get('view_count'),
                    like_count=info.get('like_count')
                ),
                audio_file_path=audio_file_path,
                audio_duration=info.get('duration'),
                sample_rate=44100,
                debug_info=debug_info
            )
            
    except Exception as e:
        debug_info['error'] = str(e)
        raise HTTPException(status_code=400, detail=f"音声ダウンロードに失敗しました: {str(e)}")

# 音声分析器と視覚化器のインスタンスを作成
analyzer = AudioAnalyzer()
visualizer = AudioVisualizer()

@app.post("/analyze-audio")
async def analyze_audio(request: AudioAnalysisRequest):
    """
    音声ファイルを分析して盛り上がりポイントを特定
    """
    try:
        # まず音声をダウンロード
        audio_response = await download_audio_simple(request)
        
        if audio_response.audio_file_path:
            # 音声分析を実行
            analysis_result = analyzer.analyze_audio(audio_response.audio_file_path)
            
            return {
                "video_info": audio_response.video_info,
                "audio_analysis": analysis_result,
                "audio_file_path": audio_response.audio_file_path
            }
        else:
            raise HTTPException(status_code=400, detail="音声ファイルのダウンロードに失敗しました")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"音声分析に失敗しました: {str(e)}")

@app.post("/analyze-with-visualization")
async def analyze_with_visualization(request: AudioAnalysisRequest):
    """
    音声分析と視覚化を実行
    """
    try:
        # まず音声をダウンロード
        audio_response = await download_audio_simple(request)
        
        if audio_response.audio_file_path:
            # 音声分析を実行
            analysis_result = analyzer.analyze_audio(audio_response.audio_file_path)
            
            # 視覚化を生成
            excitement_points = analysis_result.get('excitement_points', [])
            timeline_image = visualizer.create_excitement_timeline(audio_response.audio_file_path, excitement_points)
            summary_image = visualizer.create_summary_chart(analysis_result)
            
            # レポートを生成
            report = visualizer.generate_analysis_report(analysis_result)
            
            return {
                "video_info": audio_response.video_info,
                "audio_analysis": analysis_result,
                "visualization": {
                    "timeline_image": timeline_image,
                    "summary_image": summary_image
                },
                "report": report,
                "audio_file_path": audio_response.audio_file_path
            }
        else:
            raise HTTPException(status_code=400, detail="音声ファイルのダウンロードに失敗しました")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"音声分析・視覚化に失敗しました: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 
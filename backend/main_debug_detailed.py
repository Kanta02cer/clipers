from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp
import os
import tempfile
from typing import Optional, List
import json
import subprocess

app = FastAPI(title="YouTube盛り上がり分析ツール (Detailed Debug)", version="1.0.0")

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
    return {"message": "YouTube盛り上がり分析ツール API (Detailed Debug)"}

@app.post("/download-audio-detailed", response_model=AudioAnalysisResponse)
async def download_audio_detailed(request: AudioAnalysisRequest):
    """
    詳細デバッグ版：YouTube動画から音声をダウンロードする
    """
    debug_info = {}
    
    try:
        # 一時ディレクトリを作成
        temp_dir = tempfile.mkdtemp()
        debug_info['temp_dir'] = temp_dir
        print(f"一時ディレクトリ作成: {temp_dir}")
        
        # yt-dlpのバージョンを確認
        try:
            result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
            debug_info['yt_dlp_version'] = result.stdout.strip()
        except Exception as e:
            debug_info['yt_dlp_version_error'] = str(e)
        
        # 手動でyt-dlpコマンドを実行
        try:
            cmd = [
                'yt-dlp',
                '-f', 'bestaudio',
                '--extract-audio',
                '--audio-format', 'wav',
                '-o', os.path.join(temp_dir, '%(title)s.%(ext)s'),
                request.url
            ]
            debug_info['command'] = ' '.join(cmd)
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=temp_dir)
            debug_info['command_stdout'] = result.stdout
            debug_info['command_stderr'] = result.stderr
            debug_info['command_returncode'] = result.returncode
            
            print(f"コマンド実行結果: {result.returncode}")
            print(f"標準出力: {result.stdout}")
            print(f"標準エラー: {result.stderr}")
            
        except Exception as cmd_error:
            debug_info['command_error'] = str(cmd_error)
            print(f"コマンド実行エラー: {cmd_error}")
        
        # ダウンロードされたファイルを確認
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
        
        # 動画情報を取得（別途）
        try:
            ydl_opts = {'quiet': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(request.url, download=False)
                debug_info['video_info'] = {
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                }
        except Exception as info_error:
            debug_info['info_error'] = str(info_error)
        
        return AudioAnalysisResponse(
            video_info=VideoInfo(
                title=debug_info.get('video_info', {}).get('title', ''),
                duration=debug_info.get('video_info', {}).get('duration'),
                description='',
                view_count=None,
                like_count=None
            ),
            audio_file_path=audio_file_path,
            audio_duration=debug_info.get('video_info', {}).get('duration'),
            sample_rate=44100,
            debug_info=debug_info
        )
            
    except Exception as e:
        debug_info['error'] = str(e)
        raise HTTPException(status_code=400, detail=f"音声ダウンロードに失敗しました: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

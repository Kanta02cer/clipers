#!/usr/bin/env python3
"""
統合YouTube動画分析システム - FastAPIサーバー
"""

import os
import sys
import json
import logging
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# FastAPI関連
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# 統合分析システム
from youtube_analyzer_integrated import IntegratedYouTubeAnalyzer, get_analyzer_instance

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPIアプリケーション
app = FastAPI(
    title="統合YouTube動画分析システム",
    description="YouTube動画の取得・ダウンロード・AI分析・切り抜きポイント分析・感情分析を統合したAPI",
    version="2.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# リクエストモデル
class VideoAnalysisRequest(BaseModel):
    url: str = Field(..., description="YouTube動画URL")
    youtube_api_key: str = Field(..., description="YouTube Data API v3キー")
    gemini_api_key: str = Field(..., description="Google Gemini APIキー")
    download_video: bool = Field(True, description="動画をダウンロードするかどうか")
    output_format: str = Field("mp4", description="出力形式 (mp4, mov, avi, mkv)")

# レスポンスモデル
class VideoAnalysisResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None

class AsyncAnalysisResponse(BaseModel):
    task_id: str
    status: str = "started"
    message: str = "分析を開始しました"

class AnalysisStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    gemini_thoughts: Optional[List[str]] = None
    current_step: Optional[str] = None

# 非同期タスク管理
background_tasks: Dict[str, Dict[str, Any]] = {}

@app.get("/")
async def root():
    """API情報"""
    return {
        "title": "統合YouTube動画分析システム",
        "version": "2.0.0",
        "description": "YouTube動画の取得・ダウンロード・AI分析・切り抜きポイント分析・感情分析を統合したAPI",
        "endpoints": {
            "POST /analyze-video": "統合動画分析（同期）",
            "POST /analyze-video-async": "統合動画分析（非同期）",
            "GET /analysis-status/{task_id}": "分析状態確認",
            "GET /health": "ヘルスチェック",
            "GET /api-info": "機能一覧"
        }
    }

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

@app.get("/api-info")
async def api_info():
    """機能一覧"""
    return {
        "features": [
            {
                "name": "YouTube動画情報取得",
                "description": "YouTube Data API v3による詳細情報取得",
                "capabilities": [
                    "動画タイトル、説明、統計情報",
                    "チャンネル情報（登録者数、動画数）",
                    "コメント分析（最新200件）",
                    "タイムスタンプ付きコメント抽出"
                ]
            },
            {
                "name": "動画ファイルダウンロード",
                "description": "yt-dlpによる高品質動画ファイル取得",
                "capabilities": [
                    "複数形式対応（mp4, mov, avi, mkv）",
                    "字幕自動取得（日本語・英語）",
                    "サムネイル取得",
                    "動画情報JSON取得"
                ]
            },
            {
                "name": "Gemini AI分析",
                "description": "Google Gemini AIによる質的分析",
                "capabilities": [
                    "ナラティブ維持率評価",
                    "フックの効力評価",
                    "エンゲージメント評価",
                    "技術品質評価",
                    "VVPスコア計算（100点満点）",
                    "Golden Clip抽出",
                    "Executive Summary生成",
                    "リアルタイム思考プロセス表示"
                ]
            },
            {
                "name": "切り抜きポイント分析",
                "description": "タイムスタンプ付きコメントによる切り抜きポイント特定",
                "capabilities": [
                    "タイムスタンプ抽出",
                    "人気時間帯特定",
                    "切り抜き適性評価",
                    "視聴者反応パターン分析"
                ]
            },
            {
                "name": "感情分析",
                "description": "コメントの感情傾向と満足度分析",
                "capabilities": [
                    "全体的な感情傾向判定",
                    "感情分布分析",
                    "主要な感情キーワード抽出",
                    "視聴者満足度評価"
                ]
            },
            {
                "name": "非同期処理対応",
                "description": "長時間動画の分析対応",
                "capabilities": [
                    "進捗管理機能",
                    "リアルタイム状態確認",
                    "バックグラウンド処理",
                    "Gemini思考プロセス可視化"
                ]
            }
        ]
    }

@app.post("/analyze-video", response_model=VideoAnalysisResponse)
async def analyze_video(request: VideoAnalysisRequest):
    """
    統合動画分析（同期）
    
    - YouTube動画情報取得
    - 動画ファイルダウンロード
    - Gemini AI分析
    - 切り抜きポイント分析
    - 感情分析
    """
    try:
        start_time = datetime.now()
        logger.info(f"同期分析開始: {request.url}")
        
        # 分析器インスタンス取得
        analyzer = get_analyzer_instance(request.youtube_api_key, request.gemini_api_key)
        
        # 統合分析実行
        result = analyzer.analyze_video_comprehensive(
            url=request.url,
            download_video=request.download_video
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"同期分析完了: {processing_time:.2f}秒")
        
        return VideoAnalysisResponse(
            success=True,
            data=result,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"同期分析エラー: {e}")
        return VideoAnalysisResponse(
            success=False,
            error=str(e)
        )

@app.post("/analyze-video-async", response_model=AsyncAnalysisResponse)
async def analyze_video_async(request: VideoAnalysisRequest, background_tasks: BackgroundTasks):
    """
    統合動画分析（非同期）
    
    長時間の動画分析をバックグラウンドで実行
    """
    try:
        task_id = str(uuid.uuid4())
        logger.info(f"非同期分析開始: {task_id}")
        
        # タスク情報を初期化
        background_tasks[task_id] = {
            "status": "started",
            "progress": 0.0,
            "result": None,
            "error": None,
            "start_time": datetime.now(),
            "gemini_thoughts": [],
            "current_step": "初期化中..."
        }
        
        # バックグラウンドタスクを開始
        background_tasks.add_task(
            run_async_analysis,
            task_id,
            request.url,
            request.youtube_api_key,
            request.gemini_api_key,
            request.download_video,
            request.output_format
        )
        
        return AsyncAnalysisResponse(
            task_id=task_id,
            status="started",
            message="非同期分析を開始しました"
        )
        
    except Exception as e:
        logger.error(f"非同期分析開始エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_async_analysis(
    task_id: str,
    url: str,
    youtube_api_key: str,
    gemini_api_key: str,
    download_video: bool,
    output_format: str
):
    """
    非同期分析の実行
    """
    try:
        logger.info(f"非同期分析実行開始: {task_id}")
        
        # 進捗更新
        background_tasks[task_id]["status"] = "processing"
        background_tasks[task_id]["progress"] = 10.0
        background_tasks[task_id]["current_step"] = "YouTube動画情報取得中..."
        background_tasks[task_id]["gemini_thoughts"].append("🔍 YouTube Data API v3を使用して動画の詳細情報を取得しています...")
        
        # 分析器インスタンス取得
        analyzer = get_analyzer_instance(youtube_api_key, gemini_api_key)
        
        # 1. YouTube動画情報取得
        background_tasks[task_id]["progress"] = 20.0
        video_id = analyzer.extract_video_id(url)
        if not video_id:
            raise ValueError("有効なYouTube URLではありません")
        
        video_info = analyzer.get_video_info(video_id)
        background_tasks[task_id]["progress"] = 40.0
        background_tasks[task_id]["current_step"] = "動画ダウンロード中..."
        background_tasks[task_id]["gemini_thoughts"].append("📥 動画ファイルと字幕をダウンロードしています...")
        
        # 2. 動画ダウンロード（オプション）
        download_result = None
        subtitle_text = ""
        if download_video:
            background_tasks[task_id]["progress"] = 50.0
            download_result = analyzer.download_video(url, output_format)
            if download_result.get('success'):
                subtitle_text = analyzer.parse_subtitle(download_result.get('subtitle_path', ''))
            background_tasks[task_id]["progress"] = 60.0
            background_tasks[task_id]["current_step"] = "Gemini AI分析中..."
            background_tasks[task_id]["gemini_thoughts"].append("🤖 Gemini AIが動画の質的分析を開始しています...")
        
        # 3. Gemini AI分析
        background_tasks[task_id]["progress"] = 70.0
        background_tasks[task_id]["gemini_thoughts"].append("🧠 ナラティブ構造、フック効果、感情エンゲージメントを分析中...")
        gemini_result = analyzer.analyze_with_gemini(video_info, subtitle_text)
        background_tasks[task_id]["progress"] = 80.0
        background_tasks[task_id]["current_step"] = "感情分析中..."
        background_tasks[task_id]["gemini_thoughts"].append("💭 視聴者コメントの感情傾向を分析しています...")
        
        # 4. 感情分析
        emotion_result = analyzer.analyze_emotions(video_info.get('comments', []))
        background_tasks[task_id]["progress"] = 85.0
        background_tasks[task_id]["current_step"] = "切り抜きポイント分析中..."
        background_tasks[task_id]["gemini_thoughts"].append("✂️ タイムスタンプ付きコメントから切り抜きポイントを特定中...")
        
        # 5. 切り抜きポイント分析
        video_duration = download_result.get('duration', 0) if download_result else 0
        clip_result = analyzer.analyze_clip_points(video_info.get('comments', []), video_duration)
        background_tasks[task_id]["progress"] = 90.0
        background_tasks[task_id]["current_step"] = "結果統合中..."
        background_tasks[task_id]["gemini_thoughts"].append("📊 すべての分析結果を統合し、最終レポートを作成中...")
        
        # 6. コンテンツ品質分析（動画がダウンロードされている場合）
        content_result = None
        if download_result and download_result.get('success') and download_result.get('video_path'):
            background_tasks[task_id]["progress"] = 92.0
            background_tasks[task_id]["current_step"] = "コンテンツ品質分析中..."
            background_tasks[task_id]["gemini_thoughts"].append("🎵 動画の音声内容と発言を分析中...")
            content_result = analyzer.analyze_content_quality(download_result['video_path'], subtitle_text)
            background_tasks[task_id]["progress"] = 95.0
            background_tasks[task_id]["current_step"] = "結果統合中..."
            background_tasks[task_id]["gemini_thoughts"].append("📊 すべての分析結果を統合し、最終レポートを作成中...")
        
        # 7. 結果の統合
        analysis_result = {
            'video_info': video_info,
            'download_result': download_result,
            'gemini_analysis': gemini_result,
            'emotion_analysis': emotion_result,
            'clip_analysis': clip_result,
            'content_analysis': content_result,
            'analysis_timestamp': datetime.now().isoformat(),
            'processing_time': (datetime.now() - background_tasks[task_id]["start_time"]).total_seconds()
        }
        
        # 完了
        background_tasks[task_id]["status"] = "completed"
        background_tasks[task_id]["progress"] = 100.0
        background_tasks[task_id]["result"] = analysis_result
        background_tasks[task_id]["current_step"] = "分析完了"
        background_tasks[task_id]["gemini_thoughts"].append("✅ 分析が完了しました！詳細な結果をご確認ください。")
        
        logger.info(f"非同期分析完了: {task_id}")
        
    except Exception as e:
        logger.error(f"非同期分析エラー: {task_id} - {e}")
        background_tasks[task_id]["status"] = "error"
        background_tasks[task_id]["error"] = str(e)
        background_tasks[task_id]["current_step"] = "エラーが発生しました"
        background_tasks[task_id]["gemini_thoughts"].append(f"❌ エラーが発生しました: {str(e)}")

@app.get("/analysis-status/{task_id}", response_model=AnalysisStatusResponse)
async def get_analysis_status(task_id: str):
    """
    分析状態確認
    """
    if task_id not in background_tasks:
        raise HTTPException(status_code=404, detail="タスクが見つかりません")
    
    task_info = background_tasks[task_id]
    
    return AnalysisStatusResponse(
        task_id=task_id,
        status=task_info["status"],
        progress=task_info["progress"],
        result=task_info.get("result"),
        error=task_info.get("error"),
        gemini_thoughts=task_info.get("gemini_thoughts", []),
        current_step=task_info.get("current_step")
    )

@app.get("/clip-points/{video_id}")
async def get_clip_points(video_id: str, youtube_api_key: str, gemini_api_key: str):
    """
    切り抜きポイント分析のみ実行
    """
    try:
        analyzer = get_analyzer_instance(youtube_api_key, gemini_api_key)
        
        # 動画情報取得
        video_info = analyzer.get_video_info(video_id)
        
        # 切り抜きポイント分析
        video_duration = 0  # 実際の動画長は取得できないため0
        clip_result = analyzer.analyze_clip_points(video_info.get('comments', []), video_duration)
        
        return {
            "success": True,
            "video_id": video_id,
            "clip_analysis": clip_result
        }
        
    except Exception as e:
        logger.error(f"切り抜きポイント分析エラー: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/emotion-analysis/{video_id}")
async def get_emotion_analysis(video_id: str, youtube_api_key: str, gemini_api_key: str):
    """
    感情分析のみ実行
    """
    try:
        analyzer = get_analyzer_instance(youtube_api_key, gemini_api_key)
        
        # 動画情報取得
        video_info = analyzer.get_video_info(video_id)
        
        # 感情分析
        emotion_result = analyzer.analyze_emotions(video_info.get('comments', []))
        
        return {
            "success": True,
            "video_id": video_id,
            "emotion_analysis": emotion_result
        }
        
    except Exception as e:
        logger.error(f"感情分析エラー: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/content-analysis")
async def analyze_content_only(request: VideoAnalysisRequest):
    """
    コンテンツ分析のみ実行（動画ファイルが必要）
    """
    try:
        analyzer = get_analyzer_instance(request.youtube_api_key, request.gemini_api_key)
        
        # 動画ダウンロード
        download_result = analyzer.download_video(request.url, request.output_format)
        
        if not download_result.get('success'):
            raise Exception("動画のダウンロードに失敗しました")
        
        video_path = download_result.get('video_path')
        subtitle_text = analyzer.parse_subtitle(download_result.get('subtitle_path', ''))
        
        # コンテンツ分析
        content_result = analyzer.analyze_content_quality(video_path, subtitle_text)
        
        return {
            "success": True,
            "content_analysis": content_result,
            "download_info": {
                "video_path": video_path,
                "subtitle_path": download_result.get('subtitle_path'),
                "duration": download_result.get('duration', 0)
            }
        }
        
    except Exception as e:
        logger.error(f"コンテンツ分析エラー: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/video-info/{video_id}")
async def get_video_info(video_id: str, youtube_api_key: str):
    """
    動画情報のみ取得
    """
    try:
        analyzer = get_analyzer_instance(youtube_api_key, "dummy")  # Gemini APIキーは不要
        
        # 動画情報取得
        video_info = analyzer.get_video_info(video_id)
        
        return {
            "success": True,
            "video_id": video_id,
            "video_info": video_info
        }
        
    except Exception as e:
        logger.error(f"動画情報取得エラー: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.delete("/cleanup/{task_id}")
async def cleanup_task(task_id: str):
    """
    タスクのクリーンアップ
    """
    if task_id in background_tasks:
        del background_tasks[task_id]
        return {"message": f"タスク {task_id} を削除しました"}
    else:
        raise HTTPException(status_code=404, detail="タスクが見つかりません")

@app.delete("/cleanup-all")
async def cleanup_all_tasks():
    """
    全タスクのクリーンアップ
    """
    count = len(background_tasks)
    background_tasks.clear()
    return {"message": f"{count}個のタスクを削除しました"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True) 
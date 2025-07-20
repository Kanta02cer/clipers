#!/usr/bin/env python3
"""
統合YouTube分析システムのテストスクリプト
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

# 現在のディレクトリをPythonパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_integrated_system():
    """統合システムのテスト"""
    print("=" * 60)
    print("🧪 統合YouTube分析システムテスト")
    print("=" * 60)
    
    # テスト用データ
    test_data = {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "youtube_api_key": "AIzaSyAs5sjHDdfbe8LZPUULNF2QrzAp-cD8lbg",
        "gemini_api_key": "AIzaSyDosn3ybHfEAV66TsG1fVlTfNQ-itHSFAI",
        "download_video": True,
        "output_format": "mp4"
    }
    
    print(f"📡 YouTube API Key: {test_data['youtube_api_key'][:10]}...")
    print(f"🤖 Gemini API Key: {test_data['gemini_api_key'][:10]}...")
    print(f"🎬 テスト動画: {test_data['url']}")
    
    # サーバーの起動確認
    print("\n🔍 サーバー状態確認...")
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ サーバーが起動しています")
        else:
            print("❌ サーバーが起動していません")
            return False
    except:
        print("❌ サーバーに接続できません")
        print("💡 サーバーを起動してください: python3 integrated_server.py")
        return False
    
    # 同期分析テスト
    print("\n🚀 同期分析テスト開始...")
    try:
        start_time = time.time()
        response = requests.post(
            "http://127.0.0.1:8000/analyze-video",
            json=test_data,
            timeout=180
        )
        end_time = time.time()
        
        print(f"⏱️  処理時間: {end_time - start_time:.2f}秒")
        print(f"📊 レスポンスステータス: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 同期分析テスト成功！")
                display_analysis_results(result['data'])
                return True
            else:
                print(f"❌ 同期分析テスト失敗: {result.get('error')}")
                return False
        else:
            print(f"❌ 同期分析テスト失敗: {response.status_code}")
            print(f"エラー内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 同期分析テストタイムアウト")
        return False
    except Exception as e:
        print(f"❌ 同期分析テストエラー: {e}")
        return False

def test_async_analysis():
    """非同期分析テスト"""
    print("\n" + "=" * 60)
    print("🔄 非同期分析テスト")
    print("=" * 60)
    
    test_data = {
        "url": "https://www.youtube.com/watch?v=9bZkp7q19f0",
        "youtube_api_key": "AIzaSyAs5sjHDdfbe8LZPUULNF2QrzAp-cD8lbg",
        "gemini_api_key": "AIzaSyDosn3ybHfEAV66TsG1fVlTfNQ-itHSFAI",
        "download_video": False,  # 高速化のためダウンロード無効
        "output_format": "mp4"
    }
    
    try:
        # 非同期分析開始
        print("📡 非同期分析開始...")
        response = requests.post(
            "http://127.0.0.1:8000/analyze-video-async",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get('task_id')
            print(f"✅ 非同期分析開始成功: {task_id}")
            
            # 状態確認
            max_checks = 30  # 最大30回チェック（60秒）
            for i in range(max_checks):
                time.sleep(2)
                
                status_response = requests.get(f"http://127.0.0.1:8000/analysis-status/{task_id}")
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"📊 進捗: {status['progress']}% - 状態: {status['status']}")
                    
                    if status['status'] == 'completed':
                        print("✅ 非同期分析完了！")
                        display_analysis_results(status['result'])
                        return True
                    elif status['status'] == 'error':
                        print(f"❌ 非同期分析エラー: {status['error']}")
                        return False
                else:
                    print(f"❌ 状態確認エラー: {status_response.status_code}")
                    return False
            
            print("❌ 非同期分析タイムアウト")
            return False
        else:
            print(f"❌ 非同期分析開始失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 非同期分析テストエラー: {e}")
        return False

def display_analysis_results(data):
    """分析結果の表示"""
    print("\n" + "=" * 60)
    print("📊 分析結果")
    print("=" * 60)
    
    if not data:
        print("❌ 分析データがありません")
        return
    
    # 動画情報
    video_info = data.get('video_info', {})
    if video_info:
        print(f"🎬 動画タイトル: {video_info.get('title', 'N/A')}")
        print(f"📺 チャンネル: {video_info.get('channel_title', 'N/A')}")
        print(f"👀 再生回数: {video_info.get('view_count', 0):,}")
        print(f"👍 高評価数: {video_info.get('like_count', 0):,}")
        print(f"💬 コメント数: {video_info.get('comment_count', 0):,}")
    
    # Gemini分析結果
    gemini_analysis = data.get('gemini_analysis', {})
    if gemini_analysis:
        print(f"\n🤖 AI分析結果:")
        print(f"   📊 ナラティブ維持率: {gemini_analysis.get('narrative_score', 'N/A')}/10")
        print(f"   🎣 フックの効力: {gemini_analysis.get('hook_score', 'N/A')}/10")
        print(f"   💬 エンゲージメント: {gemini_analysis.get('engagement_score', 'N/A')}/10")
        print(f"   🔧 技術品質: {gemini_analysis.get('tech_score', 'N/A')}/10")
        print(f"   🎯 VVPスコア: {gemini_analysis.get('vvp_score', 'N/A')}/100")
        
        # Golden Clip
        golden_clip = gemini_analysis.get('golden_clip', {})
        if golden_clip:
            print(f"   💎 Golden Clip: {golden_clip.get('time', 'N/A')}")
            print(f"      📝 理由: {golden_clip.get('reason', 'N/A')}")
        
        # Executive Summary
        summary = gemini_analysis.get('summary', '')
        if summary:
            print(f"   📋 Executive Summary: {summary[:100]}{'...' if len(summary) > 100 else ''}")
    
    # ダウンロード結果
    download_result = data.get('download_result', {})
    if download_result:
        if download_result.get('success'):
            print(f"\n⬇️ ダウンロード成功:")
            print(f"   📁 ファイル: {download_result.get('video_path', 'N/A')}")
            print(f"   📏 サイズ: {(download_result.get('file_size', 0) / 1024 / 1024):.2f} MB")
            print(f"   🎬 形式: {download_result.get('format', 'N/A')}")
            
            if download_result.get('subtitle_path'):
                print(f"   📝 字幕: {download_result.get('subtitle_path')}")
        else:
            print(f"\n❌ ダウンロード失敗: {download_result.get('error', 'N/A')}")
    
    # チャンネル情報
    channel_info = video_info.get('channel_info', {})
    if channel_info:
        print(f"\n📈 チャンネル情報:")
        print(f"   👤 チャンネル名: {channel_info.get('name', 'N/A')}")
        print(f"   👥 登録者数: {int(channel_info.get('subscriber_count', 0)):,}")
        print(f"   🎬 動画数: {int(channel_info.get('video_count', 0)):,}")
        print(f"   👀 総再生回数: {int(channel_info.get('view_count', 0)):,}")
    
    # コメント情報
    comments = video_info.get('comments', [])
    if comments:
        print(f"\n💬 コメント分析:")
        print(f"   📊 コメント数: {len(comments)}件")
        print(f"   🔝 最新コメント:")
        for i, comment in enumerate(comments[:3]):
            print(f"      {i+1}. {comment.get('author', 'N/A')}: {comment.get('text', 'N/A')[:50]}...")

def test_error_handling():
    """エラーハンドリングテスト"""
    print("\n" + "=" * 60)
    print("⚠️ エラーハンドリングテスト")
    print("=" * 60)
    
    # 無効なURL
    print("🔗 無効なURLでのテスト...")
    try:
        response = requests.post(
            "http://127.0.0.1:8000/analyze-video",
            json={
                "url": "https://www.youtube.com/watch?v=invalid",
                "youtube_api_key": "AIzaSyAs5sjHDdfbe8LZPUULNF2QrzAp-cD8lbg",
                "gemini_api_key": "AIzaSyDosn3ybHfEAV66TsG1fVlTfNQ-itHSFAI"
            },
            timeout=30
        )
        print(f"📊 レスポンス: {response.status_code}")
        if response.status_code != 200:
            print("✅ エラーハンドリング正常")
        else:
            print("⚠️ 予期しない成功")
    except Exception as e:
        print(f"❌ エラー: {e}")
    
    # 無効なAPIキー
    print("\n🔑 無効なAPIキーでのテスト...")
    try:
        response = requests.post(
            "http://127.0.0.1:8000/analyze-video",
            json={
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "youtube_api_key": "invalid_key",
                "gemini_api_key": "AIzaSyDosn3ybHfEAV66TsG1fVlTfNQ-itHSFAI"
            },
            timeout=30
        )
        print(f"📊 レスポンス: {response.status_code}")
        if response.status_code != 200:
            print("✅ エラーハンドリング正常")
        else:
            print("⚠️ 予期しない成功")
    except Exception as e:
        print(f"❌ エラー: {e}")

def main():
    """メイン関数"""
    print("🧪 統合YouTube分析システムの包括的テスト")
    print("=" * 60)
    
    # 1. 同期分析テスト
    sync_success = test_integrated_system()
    
    # 2. 非同期分析テスト
    async_success = test_async_analysis()
    
    # 3. エラーハンドリングテスト
    test_error_handling()
    
    # 結果のまとめ
    print("\n" + "=" * 60)
    print("📋 テスト結果まとめ")
    print("=" * 60)
    print(f"🔧 同期分析テスト: {'✅ 成功' if sync_success else '❌ 失敗'}")
    print(f"🔄 非同期分析テスト: {'✅ 成功' if async_success else '❌ 失敗'}")
    
    if sync_success and async_success:
        print("\n🎉 統合システムは正常に動作しています！")
        print("\n💡 次のステップ:")
        print("   1. ブラウザで http://localhost:8080 にアクセス")
        print("   2. APIキーを設定")
        print("   3. YouTube動画URLを入力")
        print("   4. 分析開始ボタンをクリック")
    else:
        print("\n⚠️ システムに問題があります。ログを確認してください。")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
統合YouTube分析システム起動スクリプト
"""

import os
import sys
import subprocess
import time
import webbrowser
import signal
import threading
from pathlib import Path

def check_dependencies():
    """依存関係のチェック"""
    print("📋 依存関係チェック中...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'yt_dlp', 'google.generativeai', 
        'googleapiclient', 'requests', 'pydantic'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'google.generativeai':
                import google.generativeai
            elif package == 'googleapiclient':
                import googleapiclient
            else:
                __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  不足しているパッケージ: {', '.join(missing_packages)}")
        print("以下のコマンドでインストールしてください:")
        print(f"pip3 install {' '.join(missing_packages)}")
        return False
    
    return True

def start_backend_server():
    """バックエンドサーバーを起動"""
    print("\n🚀 統合バックエンドサーバーを起動中...")
    
    backend_dir = Path(__file__).parent / "backend"
    if not backend_dir.exists():
        print("❌ backendディレクトリが見つかりません。")
        return False, None
    
    # ポート8000が使用中かチェック
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 8000))
    sock.close()
    
    if result == 0:
        print("⚠️ ポート8000が使用中です。既存のプロセスを停止します...")
        try:
            subprocess.run(["lsof", "-ti", "8000"], capture_output=True)
            subprocess.run(["kill", "-9", "$(lsof -ti:8000)"], shell=True)
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ プロセス停止エラー: {e}")
    
    os.chdir(backend_dir)
    
    try:
        # uvicornを使用してFastAPIアプリケーションを起動
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "integrated_server:app", 
            "--host", "127.0.0.1", "--port", "8000", "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # サーバーが起動するまで待機
        time.sleep(8)
        
        # プロセスが生きているかチェック
        if process.poll() is None:
            # サーバーが実際に応答するかテスト
            max_retries = 5
            for i in range(max_retries):
                try:
                    import requests
                    response = requests.get("http://127.0.0.1:8000/health", timeout=3)
                    if response.status_code == 200:
                        print("✅ 統合バックエンドサーバーが起動しました (http://127.0.0.1:8000)")
                        return True, process
                    else:
                        print(f"⚠️ サーバーは起動しましたが、応答が異常です: {response.status_code}")
                        return True, process
                except Exception as e:
                    if i < max_retries - 1:
                        print(f"⚠️ サーバー応答テスト中... ({i+1}/{max_retries})")
                        time.sleep(2)
                    else:
                        print(f"⚠️ サーバー応答テストエラー: {e}")
                        # プロセスが生きていれば成功とする
                        if process.poll() is None:
                            print("✅ 統合バックエンドサーバーが起動しました (http://127.0.0.1:8000)")
                            return True, process
                        else:
                            stdout, stderr = process.communicate()
                            print("❌ バックエンドサーバーの起動に失敗しました:")
                            print(stderr.decode())
                            return False, None
        else:
            stdout, stderr = process.communicate()
            print("❌ バックエンドサーバーの起動に失敗しました:")
            print(stderr.decode())
            return False, None
            
    except Exception as e:
        print(f"❌ サーバー起動エラー: {e}")
        return False, None

def start_frontend_server():
    """フロントエンドサーバーを起動"""
    print("\n🌐 フロントエンドサーバーを起動中...")
    
    # プロジェクトルートに戻る
    os.chdir(Path(__file__).parent)
    
    try:
        # ポート8080が使用中かチェック
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8080))
        sock.close()
        
        if result == 0:
            print("⚠️ ポート8080が使用中です。既存のプロセスを停止します...")
            subprocess.run(["lsof", "-ti", "8080"], capture_output=True)
            subprocess.run(["kill", "-9", "$(lsof -ti:8080)"], shell=True)
            time.sleep(2)
        
        # HTTPサーバーを起動
        process = subprocess.Popen([
            sys.executable, "-m", "http.server", "8080"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ フロントエンドサーバーが起動しました (http://localhost:8080)")
            return True, process
        else:
            print("❌ フロントエンドサーバーの起動に失敗しました")
            return False, None
            
    except Exception as e:
        print(f"❌ フロントエンドサーバー起動エラー: {e}")
        return False, None

def open_browser():
    """ブラウザでフロントエンドを開く"""
    print("\n🌐 ブラウザでフロントエンドを開いています...")
    
    try:
        webbrowser.open("http://localhost:8080")
        print("✅ ブラウザでフロントエンドが開かれました")
        return True
    except Exception as e:
        print(f"❌ ブラウザ起動エラー: {e}")
        return False

def signal_handler(signum, frame):
    """シグナルハンドラー（Ctrl+C）"""
    print("\n\n🛑 システムを停止中...")
    sys.exit(0)

def main():
    """メイン関数"""
    print("=" * 60)
    print("🎬 統合YouTube動画分析システム - 起動")
    print("=" * 60)
    
    # シグナルハンドラーを設定
    signal.signal(signal.SIGINT, signal_handler)
    
    # 依存関係チェック
    if not check_dependencies():
        print("\n⚠️ 依存関係のインストールが必要です。")
        return
    
    # バックエンドサーバー起動
    backend_success, backend_process = start_backend_server()
    if not backend_success:
        return
    
    # フロントエンドサーバー起動
    frontend_success, frontend_process = start_frontend_server()
    if not frontend_success:
        backend_process.terminate()
        return
    
    # ブラウザでフロントエンドを開く
    open_browser()
    
    print("\n" + "=" * 60)
    print("🎉 統合システムが正常に起動しました！")
    print("=" * 60)
    print("\n📝 使用方法:")
    print("1. ブラウザで http://localhost:8080 が開かれます")
    print("2. APIキーを設定してください")
    print("3. YouTube動画URLを入力して分析を開始")
    print("\n🔧 システム機能:")
    print("   ✅ YouTube動画情報取得（Data API v3）")
    print("   ✅ 動画ファイルダウンロード（yt-dlp）")
    print("   ✅ Gemini AI分析")
    print("   ✅ コメント分析")
    print("   ✅ チャンネル情報取得")
    print("   ✅ 字幕解析")
    print("   ✅ VVPスコア計算")
    print("   ✅ Golden Clip抽出")
    print("   ✅ 非同期処理対応")
    print("\n🛑 サーバーを停止するには Ctrl+C を押してください")
    print("=" * 60)
    
    try:
        # プロセスが終了するまで待機
        while True:
            if backend_process.poll() is not None:
                print("\n❌ バックエンドサーバーが停止しました")
                break
            if frontend_process.poll() is not None:
                print("\n❌ フロントエンドサーバーが停止しました")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 システムを停止中...")
    finally:
        # プロセスを終了
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
        if frontend_process:
            frontend_process.terminate()
            frontend_process.wait()
        print("✅ システムが停止しました")

if __name__ == "__main__":
    main() 
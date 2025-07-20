#!/usr/bin/env python3
"""
フロントエンド用のシンプルなHTTPサーバー
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

def start_frontend_server():
    # フロントエンドディレクトリに移動
    frontend_dir = Path(__file__).parent
    os.chdir(frontend_dir)
    
    # ポート設定
    PORT = 3000
    
    # HTTPサーバーを作成
    Handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🎨 フロントエンドサーバーを起動しました")
        print(f"📱 URL: http://localhost:{PORT}")
        print(f"📁 ディレクトリ: {frontend_dir}")
        print(f"🔄 ブラウザを自動で開きます...")
        
        # ブラウザを自動で開く
        webbrowser.open(f'http://localhost:{PORT}')
        
        try:
            print(f"⏹️  サーバーを停止するには Ctrl+C を押してください")
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🛑 サーバーを停止しました")

if __name__ == "__main__":
    start_frontend_server() 
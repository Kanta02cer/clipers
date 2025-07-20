import requests
import json

def test_different_videos():
    base_url = "http://localhost:8000"
    
    print("=== 異なる動画でのテスト ===")
    
    # 複数の異なるYouTube動画でテスト
    test_urls = [
        "https://www.youtube.com/watch?v=9bZkp7q19f0",  # PSY - GANGNAM STYLE
        "https://www.youtube.com/watch?v=kJQP7kiw5Fk",  # Luis Fonsi - Despacito
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley (元の動画)
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n--- テスト {i} ---")
        try:
            data = {"url": url, "download_audio": True}
            response = requests.post(f"{base_url}/download-audio-simple", json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 成功: {result['video_info']['title']}")
                print(f"   音声ファイル: {result.get('audio_file_path', 'N/A')}")
                print(f"   ファイル一覧: {result['debug_info'].get('all_files', [])}")
            else:
                print(f"❌ 失敗: {response.status_code} - {response.json()}")
                
        except Exception as e:
            print(f"❌ エラー: {e}")
    
    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    test_different_videos()

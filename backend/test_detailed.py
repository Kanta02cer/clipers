import requests
import json

def test_detailed_api():
    base_url = "http://localhost:8000"
    
    print("=== 詳細デバッグ版 API テスト ===")
    
    # 異なる動画でテスト
    test_url = "https://www.youtube.com/watch?v=9bZkp7q19f0"  # PSY - GANGNAM STYLE
    
    try:
        data = {"url": test_url, "download_audio": True}
        response = requests.post(f"{base_url}/download-audio-detailed", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 詳細デバッグ版音声ダウンロード成功:")
            print(f"   タイトル: {result['video_info']['title']}")
            print(f"   音声ファイル: {result.get('audio_file_path', 'N/A')}")
            print(f"   音声時間: {result.get('audio_duration', 'N/A')}秒")
            print(f"   デバッグ情報:")
            for key, value in result['debug_info'].items():
                print(f"     {key}: {value}")
        else:
            print(f"❌ 詳細デバッグ版音声ダウンロード失敗: {response.status_code} - {response.json()}")
            
    except Exception as e:
        print(f"❌ 詳細デバッグ版音声ダウンロードエラー: {e}")
    
    print("=== 詳細デバッグ版テスト完了 ===")

if __name__ == "__main__":
    test_detailed_api()

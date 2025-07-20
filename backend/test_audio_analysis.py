import requests
import json

def test_audio_analysis():
    base_url = "http://localhost:8000"
    
    print("=== 音声分析テスト ===")
    
    test_url = "https://www.youtube.com/watch?v=9bZkp7q19f0"
    
    try:
        data = {"url": test_url, "download_audio": True}
        response = requests.post(f"{base_url}/analyze-audio", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 音声分析成功:")
            print(f"   タイトル: {result['video_info']['title']}")
            print(f"   動画時間: {result['audio_analysis'].get('duration', 'N/A')}秒")
            print(f"   盛り上がりスコア: {result['audio_analysis'].get('overall_excitement_score', 'N/A')}")
            print(f"   盛り上がりポイント数: {len(result['audio_analysis'].get('excitement_points', []))}")
            
            # 盛り上がりポイントの詳細
            for i, point in enumerate(result['audio_analysis'].get('excitement_points', [])[:5]):
                point_type = point.get('type', 'volume')
                print(f"   ポイント{i+1}: {point['time']}秒 (強度: {point['intensity']:.2f}, タイプ: {point_type})")
            
            # 音量分析の詳細
            volume_analysis = result['audio_analysis'].get('volume_analysis', {})
            print(f"   音量分析:")
            print(f"     平均音量: {volume_analysis.get('mean_volume', 'N/A'):.2f} dB")
            print(f"     最大音量: {volume_analysis.get('max_volume', 'N/A'):.2f} dB")
            print(f"     音量変動: {volume_analysis.get('volume_variance', 'N/A'):.2f}")
                
        else:
            print(f"❌ 音声分析失敗: {response.status_code} - {response.json()}")
            
    except Exception as e:
        print(f"❌ 音声分析エラー: {e}")
    
    print("=== 音声分析テスト完了 ===")

if __name__ == "__main__":
    test_audio_analysis() 
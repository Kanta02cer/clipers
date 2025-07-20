import requests
import json
import base64
import os

def test_visualization():
    base_url = "http://localhost:8000"
    
    print("=== 視覚化機能テスト ===")
    
    test_url = "https://www.youtube.com/watch?v=9bZkp7q19f0"
    
    try:
        data = {"url": test_url, "download_audio": True}
        response = requests.post(f"{base_url}/analyze-with-visualization", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 視覚化機能テスト成功:")
            print(f"   タイトル: {result['video_info']['title']}")
            print(f"   動画時間: {result['audio_analysis'].get('duration', 'N/A')}秒")
            print(f"   盛り上がりスコア: {result['audio_analysis'].get('overall_excitement_score', 'N/A')}")
            print(f"   盛り上がりポイント数: {len(result['audio_analysis'].get('excitement_points', []))}")
            
            # レポート情報を表示
            report = result.get('report', {})
            if 'summary' in report:
                summary = report['summary']
                print(f"   レポート概要:")
                print(f"     総再生時間: {summary.get('total_duration', 'N/A'):.2f}秒")
                print(f"     盛り上がりスコア: {summary.get('excitement_score', 'N/A'):.2f}")
                print(f"     盛り上がりポイント数: {summary.get('total_excitement_points', 'N/A')}")
                print(f"     平均音量: {summary.get('average_volume', 'N/A'):.2f} dB")
            
            # 推奨事項を表示
            recommendations = report.get('recommendations', [])
            if recommendations:
                print(f"   推奨事項:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"     {i}. {rec}")
            
            # 視覚化画像を保存
            visualization = result.get('visualization', {})
            if 'timeline_image' in visualization:
                timeline_data = visualization['timeline_image']
                if not timeline_data.startswith('視覚化エラー'):
                    with open('timeline_chart.png', 'wb') as f:
                        f.write(base64.b64decode(timeline_data))
                    print(f"   ✅ タイムラインチャートを保存: timeline_chart.png")
            
            if 'summary_image' in visualization:
                summary_data = visualization['summary_image']
                if not summary_data.startswith('サマリーチャートエラー'):
                    with open('summary_chart.png', 'wb') as f:
                        f.write(base64.b64decode(summary_data))
                    print(f"   ✅ サマリーチャートを保存: summary_chart.png")
                
        else:
            print(f"❌ 視覚化機能テスト失敗: {response.status_code} - {response.json()}")
            
    except Exception as e:
        print(f"❌ 視覚化機能テストエラー: {e}")
    
    print("=== 視覚化機能テスト完了 ===")

if __name__ == "__main__":
    test_visualization() 
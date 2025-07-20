#!/usr/bin/env python3
"""
Gemini API動作確認テストスクリプト
"""

import os
import sys
import json
import logging
import google.generativeai as genai
from datetime import datetime

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gemini_api():
    """Gemini APIの動作確認"""
    print("=" * 60)
    print("🤖 Gemini API動作確認テスト")
    print("=" * 60)
    
    # テスト用APIキー
    gemini_api_key = "AIzaSyDosn3ybHfEAV66TsG1fVlTfNQ-itHSFAI"
    
    try:
        # Gemini API初期化
        print("🔧 Gemini API初期化中...")
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini API初期化成功")
        
        # 簡単なテスト
        print("\n🧪 簡単なテスト実行中...")
        response = model.generate_content("こんにちは！簡単なテストです。")
        print(f"✅ レスポンス: {response.text}")
        
        # 動画分析テスト
        print("\n🎬 動画分析テスト実行中...")
        test_prompt = """
        以下の動画情報を分析してください：
        
        タイトル: Rick Astley - Never Gonna Give You Up
        再生回数: 1,675,998,144
        高評価数: 18,462,501
        コメント数: 2,400,700
        
        この動画の魅力を3つのポイントで説明してください。
        """
        
        response = model.generate_content(test_prompt)
        print(f"✅ 動画分析結果:\n{response.text}")
        
        # 感情分析テスト
        print("\n💭 感情分析テスト実行中...")
        comments_test = """
        以下のコメントの感情を分析してください：
        
        コメント1: "This song is amazing! I love it!"
        コメント2: "Not my type of music"
        コメント3: "Can't stop listening to this!"
        コメント4: "Meh, it's okay"
        
        各コメントの感情（ポジティブ/ネガティブ/ニュートラル）を判定してください。
        """
        
        response = model.generate_content(comments_test)
        print(f"✅ 感情分析結果:\n{response.text}")
        
        # 切り抜きポイント分析テスト
        print("\n✂️ 切り抜きポイント分析テスト実行中...")
        timestamp_test = """
        以下のタイムスタンプ付きコメントを分析して、最も注目すべき切り抜きポイントを特定してください：
        
        0:30 - "This part is so catchy!"
        1:15 - "Love this dance move!"
        2:45 - "The chorus is perfect!"
        3:20 - "This is the best part!"
        4:10 - "Amazing ending!"
        
        最も人気のある切り抜きポイント（時間）とその理由を教えてください。
        """
        
        response = model.generate_content(timestamp_test)
        print(f"✅ 切り抜きポイント分析結果:\n{response.text}")
        
        print("\n🎉 Gemini API動作確認完了！")
        return True
        
    except Exception as e:
        print(f"❌ Gemini APIテスト失敗: {e}")
        return False

def test_gemini_integration():
    """統合システムでのGemini APIテスト"""
    print("\n" + "=" * 60)
    print("🔗 統合システムでのGemini APIテスト")
    print("=" * 60)
    
    try:
        # 統合分析システムをインポート
        from youtube_analyzer_integrated import IntegratedYouTubeAnalyzer
        
        # テスト用データ
        test_data = {
            "title": "PSY - GANGNAM STYLE",
            "view_count": 5645303761,
            "like_count": 30672116,
            "comments": [
                {"text": "This song is amazing!", "timestamp": "0:30"},
                {"text": "Love this dance!", "timestamp": "1:15"},
                {"text": "Perfect chorus!", "timestamp": "2:45"},
                {"text": "Best part ever!", "timestamp": "3:20"}
            ]
        }
        
        # 分析器インスタンス作成
        analyzer = IntegratedYouTubeAnalyzer(
            youtube_api_key="AIzaSyAs5sjHDdfbe8LZPUULNF2QrzAp-cD8lbg",
            gemini_api_key="AIzaSyDosn3ybHfEAV66TsG1fVlTfNQ-itHSFAI"
        )
        
        # Gemini分析テスト
        print("🤖 統合Gemini分析テスト実行中...")
        result = analyzer.analyze_with_gemini(test_data, "テスト字幕テキスト")
        
        print("✅ 統合分析結果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return True
        
    except Exception as e:
        print(f"❌ 統合Gemini APIテスト失敗: {e}")
        return False

def main():
    """メイン関数"""
    print("🧪 Gemini API包括的テスト")
    print("=" * 60)
    
    # 1. 基本Gemini APIテスト
    basic_success = test_gemini_api()
    
    # 2. 統合システムテスト
    integration_success = test_gemini_integration()
    
    # 結果まとめ
    print("\n" + "=" * 60)
    print("📋 テスト結果まとめ")
    print("=" * 60)
    print(f"🔧 基本Gemini APIテスト: {'✅ 成功' if basic_success else '❌ 失敗'}")
    print(f"🔗 統合システムテスト: {'✅ 成功' if integration_success else '❌ 失敗'}")
    
    if basic_success and integration_success:
        print("\n🎉 Gemini APIは正常に動作しています！")
        print("\n💡 次のステップ:")
        print("   1. index.htmlの機能拡張")
        print("   2. 切り抜きポイント分析機能の実装")
        print("   3. 感情分析機能の実装")
    else:
        print("\n⚠️ Gemini APIに問題があります。設定を確認してください。")

if __name__ == "__main__":
    main() 
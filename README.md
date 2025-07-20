# 🎬 統合YouTube動画分析システム v2.0.0

## 📋 概要

YouTube動画の取得・ダウンロード・AI分析・切り抜きポイント分析・感情分析を統合した包括的な分析システムです。

## 🏗️ システム構成

```
Clipers/
├── 📁 backend/                    # バックエンドシステム
│   ├── 🐍 integrated_server.py           # FastAPI統合サーバー
│   ├── 🐍 youtube_analyzer_integrated.py # 統合YouTube分析器
│   ├── 🐍 gemini_analyzer.py             # Gemini AI分析
│   ├── 🐍 analysis_logic.py              # VVPスコア計算ロジック
│   ├── 🐍 content_analyzer.py            # コンテンツ分析
│   ├── 🐍 requirements.txt               # 依存関係
│   ├── 🧪 test_gemini_api.py            # Gemini APIテスト
│   └── 🧪 test_integrated_system.py     # 統合システムテスト
├── 🌐 index.html                  # フロントエンドUI
├── 🚀 start_integrated_system.py  # システム起動スクリプト
├── 📚 docs/                       # ドキュメント
│   ├── 📄 video_evaluation_framework_guide.md
│   └── 📄 youtube_api_setup_guide.md
└── 📖 README.md                   # このファイル
```

## ✨ 主要機能

### 🎯 統合分析機能
- **YouTube動画情報取得** (Data API v3)
- **動画ファイルダウンロード** (yt-dlp)
- **Gemini AI分析** (質的分析)
- **VVPスコア計算** (100点満点)
- **切り抜きポイント分析**
- **感情分析**
- **Golden Clip抽出**

### 🤖 AI分析機能
- **ナラティブ維持率評価**
- **フック効果評価**
- **エンゲージメント評価**
- **技術品質評価**
- **リアルタイム思考プロセス表示**

### 📊 評価ロジック
- **VVPスコア**: ナラティブ維持率(40%) + フック効果(30%) + エンゲージメント(25%) + 技術品質(5%)
- **クリップスコア**: 定量的エンゲージメント(60%) + 定性的インサイト(40%)
- **感情分析**: ポジティブ/ネガティブ/ニュートラル分布
- **切り抜き適性**: スコアとコメント数に基づく評価

## 🚀 クイックスタート

### 1. 依存関係インストール
```bash
cd backend
pip3 install -r requirements.txt
```

### 2. システム起動
```bash
python3 start_integrated_system.py
```

### 3. ブラウザアクセス
- フロントエンド: http://localhost:8080
- バックエンドAPI: http://127.0.0.1:8000

## 🔧 APIエンドポイント

### 主要エンドポイント
- `POST /analyze-video` - 統合動画分析（同期）
- `POST /analyze-video-async` - 統合動画分析（非同期）
- `GET /analysis-status/{task_id}` - 分析状態確認
- `GET /health` - ヘルスチェック
- `GET /api-info` - 機能一覧

### 個別分析エンドポイント
- `GET /clip-points/{video_id}` - 切り抜きポイント分析
- `GET /emotion-analysis/{video_id}` - 感情分析
- `POST /content-analysis` - コンテンツ分析
- `GET /video-info/{video_id}` - 動画情報取得

## 📝 使用方法

### 1. APIキー設定
- YouTube Data API v3キー
- Google Gemini APIキー

### 2. 動画分析実行
```bash
# テスト実行
cd backend
python3 youtube_analyzer_integrated.py <YouTube_URL> <YouTube_API_Key> <Gemini_API_Key>
```

### 3. フロントエンド操作
1. ブラウザで http://localhost:8080 にアクセス
2. APIキーを設定
3. YouTube動画URLを入力
4. 分析オプションを選択
5. 「分析開始」をクリック

## 🧪 テスト

### システムテスト
```bash
cd backend
python3 test_integrated_system.py
```

### Gemini APIテスト
```bash
cd backend
python3 test_gemini_api.py
```

## 🔍 分析結果例

### VVPスコア
```
📈 総合VVPスコア: 85.5/100
- ナラティブ維持率: 88.0/100
- フック効果: 82.0/100
- エンゲージメント: 85.0/100
- 技術品質: 85.0/100
```

### Golden Clip提案
```
💎 ゴールデンクリップ提案:
- 時間: 02:30 - 03:45
- 理由: 視聴者の関心が最も高まったクライマックスシーン
```

### 切り抜き候補
```
🎬 切り抜き候補トップ5:
1. [95点] 02:30 - 感動のクライマックス (15回言及)
2. [87点] 01:15 - 面白い発言 (12回言及)
3. [82点] 04:20 - 重要なポイント (8回言及)
```

## 🛠️ 技術仕様

### バックエンド
- **FastAPI**: 高速Webフレームワーク
- **uvicorn**: ASGIサーバー
- **yt-dlp**: YouTube動画ダウンロード
- **google-generativeai**: Gemini AI API
- **googleapiclient**: YouTube Data API v3

### フロントエンド
- **HTML5/CSS3/JavaScript**: モダンWeb技術
- **リアルタイム更新**: WebSocket風の実装
- **レスポンシブデザイン**: モバイル対応

### 分析エンジン
- **Gemini 1.5 Flash**: 最新のAI分析
- **VVPスコア計算**: 独自の評価アルゴリズム
- **感情分析**: キーワードベース + AI分析
- **タイムスタンプ抽出**: 正規表現パターンマッチング

## 📊 パフォーマンス

### 処理時間
- **短編動画** (<5分): 30-60秒
- **中編動画** (5-15分): 1-3分
- **長編動画** (>15分): 3-10分

### 対応形式
- **動画形式**: mp4, mov, avi, mkv
- **字幕形式**: VTT (日本語・英語)
- **出力形式**: JSON, HTML

## 🔒 セキュリティ

- **APIキー管理**: ローカルストレージ
- **一時ファイル**: 自動クリーンアップ
- **エラーハンドリング**: 包括的例外処理
- **ログ管理**: 詳細なログ出力

## 🚀 今後の展開

- [ ] リアルタイム分析ダッシュボード
- [ ] バッチ処理対応
- [ ] クラウドデプロイ対応
- [ ] 多言語対応
- [ ] 高度な可視化機能

## 📞 サポート

問題や質問がある場合は、GitHubのIssuesページをご利用ください。

---

**🎬 統合YouTube動画分析システム v2.0.0** - 動画分析の未来を創造する 
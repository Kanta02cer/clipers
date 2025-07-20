# 🎬 統合YouTube動画分析システム

YouTube動画の取得・ダウンロード・AI分析を統合した最先端システム

## 📁 プロジェクト構造

```
Clipers/
├── index.html                    # フロントエンド（統合UI）
├── start_integrated_system.py    # システム起動スクリプト
├── backend/
│   ├── youtube_analyzer_integrated.py  # 統合分析エンジン
│   ├── integrated_server.py            # FastAPIサーバー
│   ├── test_integrated_system.py       # システムテスト
│   └── requirements.txt                # 依存関係
└── docs/
    ├── video_evaluation_framework_guide.md
    └── youtube_api_setup_guide.md
```

## 🚀 クイックスタート

### 1. 依存関係のインストール
```bash
cd backend
pip3 install -r requirements.txt
```

### 2. システム起動
```bash
python3 start_integrated_system.py
```

### 3. ブラウザでアクセス
- **URL**: http://localhost:8080
- **API**: http://127.0.0.1:8000

## 🔧 システム機能

### ✅ YouTube動画情報取得
- **YouTube Data API v3**による詳細情報取得
- 動画タイトル、説明、統計情報
- チャンネル情報（登録者数、動画数）
- コメント分析（最新100件）

### ✅ 動画ファイルダウンロード
- **yt-dlp**による高品質動画ファイル取得
- 複数形式対応（mp4, mov, avi, mkv）
- 字幕自動取得（日本語・英語）
- サムネイル取得

### ✅ Gemini AI分析
- **質的分析**：ナラティブ維持率、フックの効力、エンゲージメント、技術品質
- **VVPスコア計算**：100点満点での評価
- **Golden Clip抽出**：最重要区間の特定
- **Executive Summary**：AI戦略要約

### ✅ 非同期処理対応
- 長時間動画の分析対応
- 進捗管理機能
- リアルタイム状態確認

## 📊 分析項目

### 🤖 AI分析スコア
- **ナラティブ維持率** (40%): ストーリーの一貫性と流れ
- **フックの効力** (30%): 視聴者の興味を引く力
- **エンゲージメント** (25%): 視聴者の反応を引き出す力
- **技術品質** (5%): 音声・映像・編集の技術的品質

### 🎯 VVPスコア計算式
```
VVP Score = (narrative_score × 0.40) + (hook_score × 0.30) + 
            (engagement_score × 0.25) + (tech_score × 0.05)
```

## 🔑 APIキー設定

### YouTube Data API v3
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. プロジェクトを作成または選択
3. YouTube Data API v3を有効化
4. APIキーを作成

### Google Gemini API
1. [Google AI Studio](https://makersuite.google.com/app/apikey)にアクセス
2. APIキーを作成

## 🧪 テスト実行

```bash
cd backend
python3 test_integrated_system.py
```

## 📝 使用方法

### 1. フロントエンド（推奨）
1. ブラウザで http://localhost:8080 にアクセス
2. APIキーを設定
3. YouTube動画URLを入力
4. 分析タイプを選択（統合分析/非同期分析）
5. 「分析開始」ボタンをクリック

### 2. API直接呼び出し
```bash
curl -X POST "http://127.0.0.1:8000/analyze-video" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "youtube_api_key": "YOUR_YOUTUBE_API_KEY",
    "gemini_api_key": "YOUR_GEMINI_API_KEY",
    "download_video": true,
    "output_format": "mp4"
  }'
```

## 🌟 システムの特徴

### ✨ 統合性
- **1つのPythonファイル**に全機能を統合
- **シンプルなAPI**で全ての操作を実行
- **自動トリガー**による処理開始

### 🚀 高性能
- **非同期処理**対応
- **進捗管理**機能
- **エラーハンドリング**強化

### 🎨 ユーザビリティ
- **直感的なUI**設計
- **リアルタイム進捗**表示
- **詳細な結果表示**

## 🔍 APIエンドポイント

### 同期分析
- `POST /analyze-video` - 統合動画分析（同期）

### 非同期分析
- `POST /analyze-video-async` - 統合動画分析（非同期）
- `GET /analysis-status/{task_id}` - 分析状態確認

### システム情報
- `GET /` - API情報
- `GET /health` - ヘルスチェック
- `GET /api-info` - 機能一覧

## 🛠️ 技術スタック

- **バックエンド**: Python 3.8+, FastAPI, uvicorn
- **YouTube**: yt-dlp, Google API Python Client
- **AI分析**: Google Generative AI (Gemini)
- **フロントエンド**: HTML5, CSS3, JavaScript
- **サーバー**: Python HTTP Server

## 📄 ライセンス

MIT License

## 🤝 貢献

プルリクエストやイシューの報告を歓迎します。

---

**統合YouTube動画分析システム** - YouTube動画の未来を分析する 
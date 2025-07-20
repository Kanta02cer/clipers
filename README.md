# 🎵 YouTube盛り上がり分析ツール

YouTube動画の音声を分析して、最も盛り上がるポイントを特定するツールです。

## ✨ 機能

- **音声分析**: 音量と音調の変化を分析
- **盛り上がりポイント検出**: 視聴者が最も興奮する瞬間を特定
- **視覚化**: タイムラインとサマリーチャートを生成
- **Webインターフェース**: 美しいUIで簡単操作
- **詳細レポート**: 分析結果と推奨事項を提供

## 🚀 セットアップ

### 1. 環境準備

```bash
# Python 3.11をインストール（推奨）
# macOSの場合
brew install python@3.11

# 仮想環境を作成
python3.11 -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows
```

### 2. 依存関係のインストール

```bash
cd backend
pip install -r requirements.txt
```

### 3. FFmpegのインストール

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# Windows
# https://ffmpeg.org/download.html からダウンロード
```

## 🎯 使用方法

### バックエンドサーバーの起動

```bash
cd backend
source venv/bin/activate
uvicorn main_simple:app --reload --host 0.0.0.0 --port 8000
```

### フロントエンドサーバーの起動

```bash
cd frontend
python test_frontend.py
```

### Webブラウザでアクセス

1. ブラウザで `http://localhost:3000` にアクセス
2. YouTube動画のURLを入力
3. 「分析開始」ボタンをクリック
4. 分析結果を確認

## 📊 API エンドポイント

### 1. 音声分析（視覚化付き）
```
POST /analyze-with-visualization
```

**リクエスト例:**
```json
{
  "url": "https://www.youtube.com/watch?v=9bZkp7q19f0",
  "download_audio": true
}
```

**レスポンス例:**
```json
{
  "video_info": {
    "title": "PSY - GANGNAM STYLE",
    "duration": 252.22
  },
  "audio_analysis": {
    "overall_excitement_score": 4.68,
    "excitement_points": [
      {
        "time": 6.55,
        "intensity": 1.0,
        "type": "volume"
      }
    ],
    "volume_analysis": {
      "mean_volume": -12.88,
      "max_volume": -5.33,
      "volume_variance": 129.13
    }
  },
  "visualization": {
    "timeline_image": "base64_encoded_image",
    "summary_image": "base64_encoded_image"
  },
  "report": {
    "summary": {...},
    "recommendations": [...]
  }
}
```

### 2. ヘルスチェック
```
GET /health
```

## 🧪 テスト

### 音声分析テスト
```bash
cd backend
python test_audio_analysis.py
```

### 視覚化テスト
```bash
cd backend
python test_visualization.py
```

## 📁 プロジェクト構造

```
Clipers/
├── backend/
│   ├── main_simple.py          # メインAPIサーバー
│   ├── audio_analyzer.py       # 音声分析エンジン
│   ├── visualization.py        # 視覚化機能
│   ├── test_*.py              # テストスクリプト
│   └── venv/                  # Python仮想環境
├── frontend/
│   ├── index.html             # Webインターフェース
│   └── test_frontend.py       # フロントエンドサーバー
└── README.md                  # このファイル
```

## 🔧 技術スタック

### バックエンド
- **FastAPI**: Webフレームワーク
- **yt-dlp**: YouTube動画ダウンロード
- **librosa**: 音声分析
- **numpy/scipy**: 数値計算
- **matplotlib**: グラフ生成
- **FFmpeg**: 音声変換

### フロントエンド
- **HTML5/CSS3**: モダンなUI
- **JavaScript**: インタラクティブ機能
- **Base64**: 画像エンコード

## 🎨 分析アルゴリズム

### 盛り上がりポイント検出
1. **音量分析**: RMS（二乗平均平方根）を使用
2. **音調分析**: ピッチ変化を検出
3. **閾値設定**: 動的に調整可能
4. **スコアリング**: 0-100のスケール

### 視覚化機能
- **タイムライン**: 音量変化と盛り上がりポイント
- **サマリーチャート**: 統計情報と分布
- **レポート生成**: 自動推奨事項

## 🚨 注意事項

1. **YouTube利用規約**: 商用利用時はYouTubeの利用規約を確認
2. **著作権**: 動画の著作権を尊重
3. **API制限**: 大量リクエストは避ける
4. **ストレージ**: 一時ファイルは自動削除

## 🔮 今後の開発予定

- [ ] 音声認識（Whisper統合）
- [ ] 感情分析（テキストベース）
- [ ] 複数動画比較機能
- [ ] リアルタイム分析
- [ ] データベース統合
- [ ] ユーザー認証

## 🤝 貢献

1. このリポジトリをフォーク
2. 機能ブランチを作成
3. 変更をコミット
4. プルリクエストを作成

## 📄 ライセンス

MIT License

## 📞 サポート

問題や質問がある場合は、Issueを作成してください。

---

**開発者**: YouTube盛り上がり分析ツール開発チーム  
**バージョン**: 1.0.0  
**最終更新**: 2024年 
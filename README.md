# 🎵 YouTube盛り上がり分析ツール (Enhanced v2.0.0)

YouTube動画の音声分析とエンゲージメント分析を統合した包括的な分析ツールです。

## ✨ 新機能

### 🎵 正確なdB測定
- 標準的な音声レベルに基づく正確なdB値
- RMS（二乗平均平方根）による精密計算
- 動的範囲と変動の詳細分析

### 📊 YouTubeエンゲージメント分析
- YouTube Data API v3を使用
- いいね・コメント・視聴回数分析
- エンゲージメント率の計算

### 🔥 視聴箇所特定機能
- コメントからタイムスタンプを抽出
- ホットタイムスタンプの特定
- 言及回数による重要度判定

### 🚀 包括的分析
- 音声分析 + エンゲージメント分析の統合
- 包括的スコアの計算
- 多角的な盛り上がりポイント特定

## 🏗️ システム構成

```
Clipers/
├── backend/
│   ├── main_enhanced.py          # 新しいAPIサーバー
│   ├── improved_audio_analyzer.py # 改善された音声分析器
│   ├── optimized_audio_analyzer.py # 最適化された音声分析器
│   ├── audio_analyzer.py         # 基本音声分析器
│   ├── visualization.py          # 視覚化機能
│   └── test_enhanced_analysis.py # テストスクリプト
├── frontend/
│   └── index.html               # 統合されたフロントエンド
├── docs/
│   └── youtube_api_setup_guide.md # API設定ガイド
└── README.md
```

## 🚀 クイックスタート

### 1. 環境セットアップ
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 2. サーバー起動
```bash
cd backend
source venv/bin/activate
uvicorn main_enhanced:app --reload --host 0.0.0.0 --port 8000
```

### 3. フロントエンド起動
```bash
cd frontend
python3 test_frontend.py
```

### 4. ブラウザでアクセス
- `http://localhost:8000` にアクセス
- `index.html` を開く

## 🔑 YouTube API Key設定

### 1. Google Cloud Consoleでプロジェクト作成
- [Google Cloud Console](https://console.cloud.google.com/) にアクセス
- 新しいプロジェクトを作成

### 2. YouTube Data API v3を有効化
- APIライブラリから「YouTube Data API v3」を検索
- 「有効にする」をクリック

### 3. APIキーを取得
- 認証情報から「APIキー」を作成
- 生成されたキーをコピー

### 4. フロントエンドで設定
- ブラウザで `index.html` を開く
- 「YouTube API Key設定」セクションでキーを入力
- 「APIキーを保存」をクリック

## 📊 分析機能

### 🎵 基本音声分析
- 従来の音声分析機能
- 盛り上がりポイントの特定
- 視覚化チャートの生成

### 🎵 正確な音声分析
- 正確なdB測定
- 詳細な音量分析
- 精密な盛り上がりポイント検出

### 📊 エンゲージメント分析
- いいね・コメント・視聴回数分析
- エンゲージメント率の計算
- ホットタイムスタンプの抽出

### 🚀 包括的分析
- 音声 + エンゲージメント統合分析
- 包括的スコアの計算
- 多角的な盛り上がりポイント特定

## 🔧 APIエンドポイント

### 基本分析
- `POST /analyze-with-visualization` - 基本音声分析

### 改善された分析
- `POST /analyze-audio-accurate` - 正確な音声分析
- `POST /analyze-engagement` - エンゲージメント分析
- `POST /analyze-comprehensive` - 包括的分析

### ユーティリティ
- `GET /health` - ヘルスチェック
- `GET /api-info` - API情報

## 🧪 テスト

### テストスクリプトの実行
```bash
cd backend
python test_enhanced_analysis.py
```

### 手動テスト
1. 短い動画（5分以下）でテスト
2. 長い動画（10分以上）でテスト
3. 人気動画とマイナー動画でテスト

## 🔒 セキュリティ

### APIキーの保護
- 絶対にGitHubにコミットしない
- 環境変数で管理
- APIキーに制限を設定

### 推奨設定
```bash
export YOUTUBE_API_KEY="your_api_key_here"
```

## 📈 パフォーマンス最適化

### 長い動画の処理
- チャンク分割処理
- 並列処理
- サンプルレート最適化
- 時間制限（最大10分）

### メモリ使用量
- 効率的な音声処理
- 一時ファイルの自動削除
- メモリリーク対策

## 🐛 トラブルシューティング

### よくある問題

#### APIキーが無効
- APIキーが正しくコピーされているか確認
- YouTube Data API v3が有効化されているか確認

#### クォータ制限
- Google Cloud Consoleでクォータ使用量を確認
- 必要に応じてクォータを増加申請

#### サーバーが起動しない
- 仮想環境がアクティブになっているか確認
- ポート8000が使用可能か確認

## 📚 参考資料

- [YouTube Data API v3 ドキュメント](https://developers.google.com/youtube/v3)
- [Google Cloud Console](https://console.cloud.google.com/)
- [FastAPI ドキュメント](https://fastapi.tiangolo.com/)

## 🤝 貢献

1. このリポジトリをフォーク
2. 機能ブランチを作成
3. 変更をコミット
4. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 📞 サポート

問題が発生した場合は、以下を確認してください：

1. **Google Cloud Console**の設定
2. **APIキー**の有効性
3. **ネットワーク接続**
4. **サーバー**の起動状態

---

**Version**: 2.0.0  
**Last Updated**: 2024年12月 
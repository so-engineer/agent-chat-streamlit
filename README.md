# Agent Chat Streamlit 🤖

このプロジェクトは、LangGraphを使用して構築された対話型AIエージェントのStreamlitアプリケーションです。

> [!NOTE]
> 解説記事をQiitaに投稿しています。
> 
> [Streamlit × LangGraphでHuman-in-the-loopを実現する](https://qiita.com/so-engineer/items/7a7f09bb1375c2454dfc)

## 特徴

Agent Chatは、ユーザーとAIエージェントの間でインタラクティブな対話を可能にするWebアプリケーションです。LangGraphを活用することで、複雑な対話フローを管理し、より自然な会話体験を提供します。

特に、本アプリケーションではLangGraphのHuman-in-the-Loop機能を実装しており、AIエージェントが判断に迷った場合や重要な決定が必要な場合に、ユーザーに判断を委ねることができます。

- インタラクティブなチャットインターフェース
- グラフベースの会話フロー管理
- ユーザーの入力に基づく動的な応答生成
- Human-in-the-Loop による対話フロー制御
  - AIが判断に迷った場合のユーザーへの質問機能
  - ユーザーの判断を基にした処理の分岐
  - 重要な決定におけるユーザー承認プロセス

## 技術スタック

- Python
- Streamlit
- LangGraph
- LangChain
- OpenAI GPT
- Docker/Docker Compose

## セットアップ


1. リポジトリのクローン
```bash
git clone https://github.com/so-engineer/agent-chat-streamlit.git
```

2. 設定ファイルの準備:
- `config_template.yaml` を `config.yaml` にコピー
- 各サービスからAPIキーを取得：
  - OpenAI: platform.openai.com
  - LangSmith: smith.langchain.com
  - Tavily: tavily.com
- `config.yaml` の `<Your ... API key>` を取得したAPIキーに置き換え

3. プロジェクトのルートディレクトリで以下のコマンドを実行(Docker/Docker Composeのインストールが必要)
```bash
cd agent-chat-streamlit
docker compose up -d
```

## 使用方法

1. ブラウザで http://localhost:8501 にアクセス

2. ブラウザで表示されるインターフェースを使用して、AIエージェントと対話を開始
   - 起動時にLangGraphのフロー図が表示されます
   - AIが情報不足と判断した場合は ⚠️ アイコンとともに確認メッセージが表示されます

## プロジェクト構造

```
.
├── main.py               # エントリーポイント & UI
├── src/                  # ソースコードディレクトリ
│   ├── agent.py          # AIエージェントの実装
│   └── setup.py          # 設定とロギングのセットアップ
├── config.yaml           # モデルとAPIの設定ファイル
├── config_template.yaml  # 設定ファイルのテンプレート
├── requirement.txt       # プロジェクトの依存関係
├── LICENSE               # MITライセンス
├── .gitignore            # Gitの除外設定
├── pyproject.toml        # Pythonプロジェクト設定
├── .flake8               # コードスタイル設定
└── streamlit_agent.log   # アプリケーションログ
```

## その他

API利用料やセキュリティには十分注意してください。

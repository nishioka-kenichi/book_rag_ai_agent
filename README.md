# LangChain と LangGraph による RAG・AI エージェント［実践］入門

「LangChain と LangGraph による RAG・AI エージェント［実践］入門」の GitHub リポジトリです。

> **Note**: このリポジトリは[書籍公式リポジトリ](https://github.com/GenerativeAgents/agent-book)からフォークし、ローカル環境での実行に対応させたものです。

https://www.amazon.co.jp/dp/4297145308

<img src="assets/cover.jpg" width="50%" />

## 各章のソースコード

| 章 | 内容 |
|---|---|
| 第 1 章 | LLM アプリケーション開発の基礎 |
| 第 2 章 | OpenAI の チャット API の基礎 |
| 第 3 章 | プロンプトエンジニアリング |
| 第 4 章 | LangChain の基礎 |
| 第 5 章 | LangChain Expression Language（LCEL）徹底解説 |
| 第 6 章 | Advanced RAG |
| 第 7 章 | LangSmith を使った RAG アプリケーションの評価 |
| 第 8 章 | AI エージェントとは |
| 第 9 章 | LangGraph で作る AI エージェント実践入門 |
| 第 10 章 | 要件定義書生成 AI エージェントの開発 |
| 第 11 章 | エージェントデザインパターン |
| 第 12 章 | LangChain/LangGraph で実装するエージェントデザインパターン |

## 必要な環境

- Python 3.10-3.13（推奨：3.12）
  - ⚠️ Python 3.13では tiktoken 0.7.0 のビルド済みホイールがないため、追加設定が必要です
- VS Code または Cursor
- Git

Python パッケージの動作確認済みバージョンは、各章のディレクトリの requirements.txt を参照してください。

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone https://github.com/GenerativeAgents/agent-book.git
cd agent-book
```

### 2. 環境構築

```bash
# セットアップスクリプトを実行
./setup.sh
```

このスクリプトは以下を自動実行します：
- Python仮想環境の作成（.venv）
- 必要なパッケージのインストール
- Jupyter kernelの登録
- .envファイルの作成（.env.exampleから）

### 3. APIキーの設定

`.env`ファイルを編集して、必要なAPIキーを設定します：

```bash
# .envファイルを編集
nano .env  # または好みのエディタで開く
```

必要なAPIキー：
- `OPENAI_API_KEY`：全章で必要
- `LANGCHAIN_API_KEY`：Chapter 7以降で必要（LangSmith）
- `COHERE_API_KEY`：Chapter 6で必要
- `ANTHROPIC_API_KEY`：Chapter 12で必要
- `TAVILY_API_KEY`：Chapter 12で必要

### 4. VS Code/Cursorで開く

1. VS Code/Cursorでプロジェクトフォルダを開く
2. Python拡張機能がインストールされていることを確認
3. 各章の`notebook.ipynb`ファイルを開く
4. カーネルとして「RAG AI Agent Book」を選択

## 各章の実行

### 共通の注意事項

- `!pip install`コマンドはコメントアウトされています（事前インストール済み）
- 環境変数からAPIキーを自動読み込み
- ファイルパスは相対パス（`./data/`等）を使用

### 章ごとの追加要件

各章のディレクトリに移動して、追加パッケージをインストール：

```bash
# 例：Chapter 4の場合
cd chapter04
pip install -r requirements.txt
```

## トラブルシューティング

### Python 3.13でtiktokenがインストールできない

#### 方法1: Python 3.12以下を使用（推奨）

```bash
# pyenvの場合
pyenv install 3.12.7
pyenv local 3.12.7
```

#### 方法2: Python 3.13でRustを使用してビルド

1. Rustをインストール：
```bash
brew install rust  # macOSの場合
# または
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

2. ビルドツールをインストール：
```bash
source .venv/bin/activate
pip install setuptools-rust
```

3. requirements.txtを修正（tiktoken>=0.7.0に変更）してインストール：
```bash
pip install -r chapter02/requirements.txt
```

**注意**: tiktoken 0.9.0以降はPython 3.13用のビルド済みホイールが提供されているため、最新版を使用することで問題を回避できます。

### APIキーエラー

`.env`ファイルが正しく設定されているか確認：

```bash
# 環境変数の確認
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
```

### Jupyter kernelが見つからない

再度kernelを登録：

```bash
source .venv/bin/activate
python -m ipykernel install --user --name=rag_ai_agent_book --display-name="RAG AI Agent Book"
```

### パッケージの依存関係エラー

特定のバージョンで問題が発生した場合：

```bash
# キャッシュをクリアして再インストール
pip cache purge
pip install --force-reinstall -r requirements-base.txt
```

## 開発のヒント

- 各章は独立して実行可能
- 仮想環境を有効化してから作業：`source .venv/bin/activate`
- 新しいパッケージを追加した場合は`requirements.txt`を更新

## 既知のエラー

### 「7.4 Ragas による合成テストデータの生成」における RateLimitError

「7.4 Ragas による合成テストデータの生成」において、gpt-4o を使用すると OpenAI API の Usage tier 次第で RateLimitError が発生することが報告されています。

OpenAI API の Usage tier については公式ドキュメントの以下のページを参照してください。

https://platform.openai.com/docs/guides/rate-limits/usage-tiers

このエラーが発生した場合は、以下のどちらかの対応を実施してください。

1. 同じ Tier でも gpt-4o よりレートリミットの高い gpt-4o-mini を使用する
   - この場合、生成される合成テストデータの品質は低くなることが想定されます
2. 課金などにより Tier を上げる
   - Tier 2 で RateLimitError が発生しないことを確認済みです (2024 年 10 月 31 日時点)

#### 2025/3/15 追記

LangChain のドキュメントの増加により、gpt-4o-mini を使用しても Tier 1 ではエラーが発生することが報告されています。

その場合、GitHub からドキュメントをロードする箇所で、以下のように `langchain==0.2.13` という動作確認済みのバージョンを指定するようにしてください。

```python
loader = GitLoader(
    clone_url="https://github.com/langchain-ai/langchain",
    repo_path="./langchain",
    branch="langchain==0.2.13",
    file_filter=file_filter,
)
```

## 書籍の誤り・エラーについて

書籍の誤り（誤字など）や、発生したエラーについては、GitHub の Issue からご連絡ください。

https://github.com/GenerativeAgents/agent-book/issues

## 書籍刊行後のアップデート・正誤表

- [書籍刊行後のアップデート](./updates.md)
- [正誤表](./errata.md)

## リンク

- [書籍公式リポジトリ](https://github.com/GenerativeAgents/agent-book)
- [技術評論社](https://gihyo.jp/book/2024/978-4-297-14530-9)
- [Amazon](https://www.amazon.co.jp/dp/4297145308)
- [OpenAI API ドキュメント](https://platform.openai.com/docs)
- [LangChain ドキュメント](https://python.langchain.com/)
- [LangSmith](https://smith.langchain.com/)

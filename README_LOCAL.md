# ローカル環境での実行ガイド

このガイドは、Google Colab用に作成された「LangChain と LangGraph による RAG・AI エージェント［実践］入門」のコードを、ローカルのVS Code/Cursor環境で実行するための手順を説明します。

## 必要な環境

- Python 3.10-3.13（推奨：3.12）
  - ⚠️ Python 3.13では tiktoken 0.7.0 のビルド済みホイールがないため、追加設定が必要です（下記参照）
- VS Code または Cursor
- Git

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
- Google Colab特有のコード（`userdata.get()`等）は修正済み
- 環境変数からAPIキーを自動読み込み

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

## 元のGoogle Colabとの主な違い

1. **認証方法**
   - Colab: `userdata.get("API_KEY")`
   - ローカル: `.env`ファイルから読み込み

2. **パッケージインストール**
   - Colab: 各ノートブック内で`!pip install`
   - ローカル: 事前に`requirements.txt`でインストール

3. **ファイルパス**
   - Colab: `/content/`ベース
   - ローカル: 相対パス（`./data/`等）

4. **GPU/CUDA**
   - Colab: 自動設定
   - ローカル: 環境依存（CPU版パッケージを使用）

## 開発のヒント

- 各章は独立して実行可能
- 仮想環境を有効化してから作業：`source .venv/bin/activate`
- 新しいパッケージを追加した場合は`requirements.txt`を更新

## 参考リンク

- [書籍公式リポジトリ](https://github.com/GenerativeAgents/agent-book)
- [OpenAI API ドキュメント](https://platform.openai.com/docs)
- [LangChain ドキュメント](https://python.langchain.com/)
- [LangSmith](https://smith.langchain.com/)
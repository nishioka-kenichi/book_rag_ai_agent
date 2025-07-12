#!/bin/bash
# setup.sh - ローカル環境構築スクリプト

echo "=== RAG AI Agent Book ローカル環境構築 ==="
echo ""

# Python バージョンチェック
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
python_major=$(echo $python_version | cut -d'.' -f1)
python_minor=$(echo $python_version | cut -d'.' -f2)

echo "検出されたPythonバージョン: $python_version"

if [[ "$python_major" -eq 3 && "$python_minor" -eq 13 ]]; then
    echo "⚠️  警告: Python 3.13でtiktoken 0.7.0をインストールするにはRustが必要です。"
    echo "次のいずれかの対応が必要です："
    echo "  1. Python 3.10-3.12を使用する（推奨）"
    echo "  2. Rustをインストールしてソースからビルドする"
    echo ""
    echo "Rustをインストールする場合は、このスクリプト実行前に："
    echo "  brew install rust  # macOS"
    echo "  または公式サイトからインストール"
    echo ""
    read -p "このまま続行しますか？ (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 仮想環境作成
echo "仮想環境を作成しています..."
python3 -m venv .venv

# 仮想環境のアクティベート
echo "仮想環境をアクティベートしています..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source .venv/Scripts/activate
else
    # macOS/Linux
    source .venv/bin/activate
fi

# pip アップグレード
echo "pipをアップグレードしています..."
pip install --upgrade pip

# 基本パッケージインストール
echo "基本パッケージをインストールしています..."
pip install -r requirements-base.txt

# Jupyter kernel登録
echo "Jupyter kernelを登録しています..."
python -m ipykernel install --user --name=rag_ai_agent_book --display-name="RAG AI Agent Book"

# .env ファイルの作成
if [ ! -f .env ]; then
    echo ".envファイルを作成しています..."
    cp .env.example .env
    echo "⚠️  .envファイルにAPIキーを設定してください。"
fi

echo ""
echo "✅ 環境構築が完了しました！"
echo ""
echo "次のステップ:"
echo "1. .envファイルを編集してAPIキーを設定"
echo "2. VS Code/CursorでこのフォルダをOpen"
echo "3. 各章のnotebook.ipynbを開いて実行"
echo ""
echo "仮想環境の再アクティベート方法:"
echo "source .venv/bin/activate  # macOS/Linux"
echo "source .venv/Scripts/activate  # Windows"
# AI Council

![llmcouncil](header.jpg)

> **注意:** このプロジェクトは [karpathy/llm-council](https://github.com/karpathy/llm-council) のフォークで、ファイル処理機能、UI改善、および追加機能が強化されています。

## LLM Councilの説明

LLM Council は、複数のLLM（例：OpenAI GPT 5.1、Google Gemini 3.0 Pro、Anthropic Claude Sonnet 4.5、xAI Grok 4など）に同じ質問を投げ、その回答を互いに評価させ、最終的に「合意された答え」を導くための仕組みです。

質問を送信すると次のようなことが起こります：

1. **Stage 1（回答）**: ユーザーの質問が各LLMに個別に送られ、回答が収集されます。個々の回答は「タブビュー」で表示されるため、ユーザーは1つずつ確認できます。
2. **Stage 2（レビュー）**: 各LLMには他のLLMの回答が与えられます。内部では、LLMが出力を判断する際に贔屓できないように、LLMの身元は匿名化されています。LLMは、それらを正確さと洞察力でランク付けするよう求められます。
3. **Stage 3（最終回答）**: AI審議会の指定された議長が、すべてのモデルの回答を受け取り、ユーザーに提示される単一の最終回答にまとめます。

## AI Councilの拡張機能

このフォークは、オリジナルのLLM Councilにいくつかの強力な機能を追加しています：

- **ファイル添付とダウンロード**: PDF、Excelファイル、画像をアップロードできます。ファイルは処理され、その内容がLLMに送られます。チャットから元のファイルを直接ダウンロードすることもできます。
- **自動クリーンアップ**: 会話が削除されると、関連するファイルも自動的に削除され、スペースを節約します。
- **Auto Chairman**: Chairman Modelで「auto」を選択すると、Stage 2の評価で最も高い評価を得たモデルが自動的に議長として最終回答を作成します。質問ごとに最適なモデルが選ばれるため、より質の高い回答が期待できます。

## セットアップと実行

### 1. 依存関係のインストール

このプロジェクトは、プロジェクト管理に [uv](https://docs.astral.sh/uv/) を使用しています。

**バックエンド:**
```bash
uv sync
```

**フロントエンド:**
```bash
cd frontend
npm install
cd ..
```

### 2. アプリケーションの実行

起動スクリプトを使用します：
```bash
./start.sh
```

その後、ブラウザで http://localhost:5173 を開きます。

## 設定

### APIキーの設定

アプリケーション起動後にAPIキーを設定します：
1. アプリケーションを起動します
2. 左下の⚙️ Settingsボタンをクリックします
3. OpenRouter APIキーを入力します
4. 「Save Changes」をクリックします

APIキーは [openrouter.ai](https://openrouter.ai/) で取得できます。必要なクレジットを購入するか、自動チャージにサインアップしてください。

### モデルの設定（オプション）

`backend/config.py`を編集して審議会をカスタマイズします：

```python
COUNCIL_MODELS = [
    "openai/gpt-5.1",
    "google/gemini-3-pro-preview",
    "anthropic/claude-sonnet-4.5",
    "x-ai/grok-4",
]

CHAIRMAN_MODEL = "google/gemini-3-pro-preview"
```

その後、ブラウザで http://localhost:5173 を開きます。

## 技術スタック

- **バックエンド:** FastAPI（Python 3.10+）、async httpx、OpenRouter API
- **フロントエンド:** React + Vite、react-markdown（レンダリング用）
- **ストレージ:** `data/conversations/`内のJSONファイル
- **パッケージ管理:** Python用uv、JavaScript用npm

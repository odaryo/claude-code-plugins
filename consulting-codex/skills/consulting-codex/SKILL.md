---
name: consulting-codex
description: >
  Codex CLIで設計書レビュー・技術相談・セカンドオピニオンを取得。Claude Codeで詰まったとき、
  不明点があるとき、別AIの意見が欲しいときに使用。「/consulting-codex」「codexに聞いて」
  「別の意見が欲しい」「この設計どう思う？」「Codexにレビューしてもらって」「他のAIの見解」で起動。
  技術的な判断に迷ったとき、実装方針の妥当性を確認したいとき、設計のセカンドオピニオンが
  欲しいときに積極的に使う。
user-invocable: true
---

# Codex連携スキル

Codex CLIを呼び出し、設計書のレビュー・不明点の相談・セカンドオピニオンを取得する。

## 前提条件

codex CLIがインストール・認証済みであること。未確認なら `codex --version && codex login status` で確認。

## モード一覧

| モード | 用途 | モデル |
|--------|------|--------|
| `code` | コード相談・実装相談 | codex CLIデフォルト |
| `review` | 設計書・計画書のレビュー | 一般モデル（後述） |
| `arch` | アーキテクチャ相談 | 一般モデル |
| `opinion` | セカンドオピニオン | 一般モデル |

## 入力パターン

| パターン | 例 |
|---------|-----|
| 明示プレフィックス | `/consulting-codex review: .local/plans/xxx.md` |
| ファイル指定 | `/consulting-codex .local/plans/xxx.md この設計に問題はある？` |
| 質問のみ | `/consulting-codex LaravelでN+1問題を解決するには？` |
| 引数なし | `/consulting-codex` （会話コンテキストから推定して即実行） |
| resume | `/consulting-codex resume: 前回の指摘を踏まえて再レビュー` |
| resume＋モード | `/consulting-codex resume: review: .local/plans/xxx.md 修正したので再確認` |

## 手順

### Step 1: 入力解析・モード判定（ツール呼び出し不要）

**優先順位:**

0. **resume** — `resume:` で始まる場合、resumeフラグをオンにしプレフィックスを除去。残りで以下を判断。
1. **明示プレフィックス** — `review:`, `code:`, `arch:`, `opinion:` → そのモード。プレフィックスを除去。
2. **ファイル拡張子** — `.md`, `plan`, `spec` → review / `.php`, `.ts`, `.js`, `.tsx`, `.jsx`, `.py`, `.go`, `.rs`, `.java` → code
3. **キーワード** — 設計・アーキテクチャ・構成・分割・責務 → arch / どう思う・意見・セカンドオピニオン・見解 → opinion
4. **デフォルト** → code

**引数なし**: 会話コンテキストから質問とモードを推定し即実行。推定した質問を出力ヘッダーに表示する。コンテキストが全くない場合のみユーザーに確認する。

### Step 2: プロンプト構築・実行（最大1 Bash呼び出し）

#### 2a. プロンプト組み立て

モードに応じて以下のプロンプトを構築する。変数は入力やコンテキストから埋める。

**code モード:**
```
あなたは熟練したソフトウェアエンジニアです。以下の技術的な質問に回答してください。

## 質問
{{質問}}

## 背景（該当する場合）
- コンテキスト: {{コンテキスト}}

## 期待する回答
- 具体的なコード例を含める
- 複数の選択肢がある場合はメリット・デメリットを説明
- ベストプラクティスに言及する

## 出力制約
- 回答は箇条書きで構造化
- コード例は最小限かつ動作可能な形式で
- 推奨事項は最大3つに絞る
```

**review モード:**（ファイル指定時はReadツールで内容を取得してから実行）
```
あなたは経験豊富なソフトウェアアーキテクトです。以下の設計書/計画書をレビューしてください。

## レビュー観点
- 要件との整合性
- 技術的な実現可能性
- 潜在的なリスクや懸念点
- 改善提案

## 対象ファイル
ファイル: {{ファイルパス}}

---
{{ファイル内容}}
---

追加の質問: {{質問}}

## 出力制約
- 重大度の高い順に箇条書きで最大5項目
- 各項目は「問題点」「影響」「改善案」を含める
- 問題がなければ「特になし」と回答
```

**arch モード:**
```
あなたは経験豊富なソフトウェアアーキテクトです。以下のアーキテクチャに関する質問に回答してください。

## 質問
{{質問}}

## 現在のアーキテクチャ（該当する場合）
{{コンテキスト}}

## 期待する回答
- メリット・デメリットの分析
- 代替案の提示
- 推奨アプローチの理由

## 出力制約
- 選択肢ごとにPros/Consを表形式で
- 推奨案を1つ明示する
- 理由は3点以内で簡潔に
```

**opinion モード:**
```
別のAIエージェント（Claude Code）が以下の提案をしました。この提案についてセカンドオピニオンをください。

## Claude Codeの提案
{{提案内容}}

## 背景（該当する場合）
{{コンテキスト}}

## 期待する回答
- 提案の評価（良い点・懸念点）
- 見落としている観点
- 代替アプローチ（あれば）
- 最終的な推奨

## 出力制約
- 「賛成」「条件付き賛成」「反対」のいずれかを冒頭で明示
- 懸念点は重大度順に最大3つ
- 代替案は具体的なコード例または設計案を含める
```

**変数の置換ルール:**
- `{{質問}}` / `{{提案内容}}` — ユーザー入力のテキスト部分（必須）
- `{{コンテキスト}}` — 会話履歴やプロジェクト情報から抽出。該当なしなら「特になし」
- `{{ファイルパス}}` / `{{ファイル内容}}` — ファイル指定時、Readツールで取得。reviewモードではテンプレートの対象ファイルセクションに埋め込む。codeモードではプロンプト末尾に「対象コード: {{ファイルパス}}\n{{ファイル内容}}」として追加し、要点を `{{コンテキスト}}` にも含める

**resumeフラグがオンの場合:** プロンプトの先頭に以下を追加する。`{{変更サマリ}}` はユーザー入力から抽出、またはファイル指定時は `git diff` の要約。取得できなければ「ユーザー入力を参照」とする。
```
【再レビュー】前回のセッションの議論を踏まえて、以下に回答してください。
前回以降の変更点: {{変更サマリ}}
対象ファイル: {{ファイルパス}}
```

#### 2b. モデル判定と実行（1 Bash呼び出しで完結）

プロンプト内の特殊文字（`"`, `$`, `` ` ``, `\`）は適切にエスケープする。

**code モード（通常）:** `-m` 省略でCLIデフォルトを使用。`{model}` = `default`
```bash
printf '%s' "<プロンプト>" | codex exec -s read-only
```

**review/arch/opinion モード（通常）:** モデル判定と実行を1コマンドで:
```bash
MODEL=$(grep '^model[[:space:]]*=' ~/.codex/config.toml 2>/dev/null \
  | sed -nE 's/model[[:space:]]*=[[:space:]]*"([^"]+)".*/\1/p' | head -1 || true) \
  && MODEL=${MODEL%-codex} \
  && if [ -n "$MODEL" ]; then
       printf '%s' "<プロンプト>" | codex exec -s read-only -m "$MODEL"
     else
       printf '%s' "<プロンプト>" | codex exec -s read-only
     fi
```

`{model}` には決定したモデル名、またはフォールバック時は `default` を設定する。

**resume実行:** フォールバックを `||` チェインで1呼び出しに統合する。`codex exec resume` には `-s` オプションがない点に注意。stdinから読む場合はPROMPT引数に `-` を指定する。

session idが判明している場合（複数行で表記、実行時は1回のBash呼び出し）:
```bash
MODEL=$(grep '^model[[:space:]]*=' ~/.codex/config.toml 2>/dev/null \
  | sed -nE 's/model[[:space:]]*=[[:space:]]*"([^"]+)".*/\1/p' | head -1 || true) \
  && MODEL=${MODEL%-codex} \
  && if [ -n "$MODEL" ]; then
       (printf '%s' "<プロンプト>" | codex exec resume <session-id> - -m "$MODEL" 2>&1) \
         || (echo "---FALLBACK:new---" && printf '%s' "<プロンプト>" | codex exec -s read-only -m "$MODEL" 2>&1)
     else
       (printf '%s' "<プロンプト>" | codex exec resume <session-id> - 2>&1) \
         || (echo "---FALLBACK:new---" && printf '%s' "<プロンプト>" | codex exec -s read-only 2>&1)
     fi
```

session idが不明な場合:
```bash
MODEL=$(grep '^model[[:space:]]*=' ~/.codex/config.toml 2>/dev/null \
  | sed -nE 's/model[[:space:]]*=[[:space:]]*"([^"]+)".*/\1/p' | head -1 || true) \
  && MODEL=${MODEL%-codex} \
  && if [ -n "$MODEL" ]; then
       (printf '%s' "<プロンプト>" | codex exec resume --last - -m "$MODEL" 2>&1) \
         || (echo "---FALLBACK:new---" && printf '%s' "<プロンプト>" | codex exec -s read-only -m "$MODEL" 2>&1)
     else
       (printf '%s' "<プロンプト>" | codex exec resume --last - 2>&1) \
         || (echo "---FALLBACK:new---" && printf '%s' "<プロンプト>" | codex exec -s read-only 2>&1)
     fi
```

code モードのresumeは `-m` 部分を省略:
```bash
(printf '%s' "<プロンプト>" | codex exec resume <session-id> - 2>&1) || (echo "---FALLBACK:new---" && printf '%s' "<プロンプト>" | codex exec -s read-only 2>&1)
```

出力に `---FALLBACK:new---` が含まれる場合、「セッションが見つからないため新規セッションで実行しました」とユーザーに通知する。session id不明で `--last` を使う場合も「session idが見つからないため直近のセッションを使用します」と通知する。

実行後、出力から `session id: <UUID>` を抽出して保持する。

### Step 3: 結果の出力

**通常実行時:**
```markdown
## Codex ({model}) からの回答

[Codexの回答内容をそのまま出力]

---
*Codex ({model}) による回答 | session: {session-id}*
```

**resume実行時:**
```markdown
## Codex ({model}) からの回答 [再レビュー]

[Codexの回答内容をそのまま出力]

---
*Codex ({model}) による回答 | session: {session-id}*
```

## エラーハンドリング

| エラー | 対処 |
|--------|------|
| `command not found: codex` | インストール手順を案内 |
| 認証エラー | `codex login` を案内 |
| ファイル不存在 | 「ファイルが見つかりません: [パス]」 |
| タイムアウト | 質問短縮または再試行を提案 |
| トークン超過 | ファイル分割または要約を提案 |

## パフォーマンス

全モードで **最大1 Bash呼び出し** で完結する（reviewモードのファイル読み込みは別途Readツール1回）。モデル判定・実行・フォールバックはすべて1つのBashコマンドに統合されている。

# 判定ルール集

Claude Code 設定の監査で使用する判定ルール。各ルールは `check → expected state → evidence → remediation` の形式。

## CLAUDE.md 判定ルール

| ID | check | expected state | evidence | remediation |
|----|-------|---------------|----------|-------------|
| CM-01 | プロジェクト概要 | 先頭セクションにプロジェクトの概要・目的がある | CLAUDE.md 先頭20行を確認 | 概要セクションを追加 |
| CM-02 | ビルド/テスト/リントコマンド | 非標準のコマンドが記載されている（標準的な `npm test` 等は不要） | manifest ファイル + CLAUDE.md を照合 | 非標準コマンドセクションを追加 |
| CM-03 | コーディング規約 | 言語デフォルトと異なる規約が具体的に記載されている | CLAUDE.md でスタイル関連セクションを検索 | 差分のみ具体的に記載 |
| CM-04 | セキュリティルール | セキュリティに関するセクションまたはルールがある | CLAUDE.md でセキュリティ関連キーワード検索 | セキュリティセクションを追加 |
| CM-05 | コンテキスト効率 | 100行以内。長い参照は `@path/to/import` で外部化 | CLAUDE.md の行数を確認 | 冗長な内容を外部ファイルに分離し `@import` で参照 |
| CM-06 | 重複排除 | README や manifest と重複する情報がない | CLAUDE.md と README を比較 | 重複情報を削除し、必要なら `@README.md` で参照 |

## settings.json 判定ルール

| ID | check | expected state | evidence | remediation |
|----|-------|---------------|----------|-------------|
| ST-01 | セキュリティフック | PostToolUse の Write\|Edit に機密情報検出フックが設定されている | `.claude/settings.json` の hooks セクション | 機密情報検出フックを追加 |
| ST-02 | フォーマッターフック | プロジェクトにフォーマッターがある場合、PostToolUse に自動フォーマットフックが設定されている | package.json / pyproject.toml 等のフォーマッター設定 + settings.json | フォーマッターフックを追加 |
| ST-03 | matcher スコープ | hooks の matcher が必要最小限のツールに限定されている | settings.json の各 hook の matcher | matcher を必要最小限に修正 |
| ST-04 | timeout 値 | hooks の timeout が30秒以下 | settings.json の各 hook の timeout | timeout を適切な値に調整 |

## スキル判定ルール

| ID | check | expected state | evidence | remediation |
|----|-------|---------------|----------|-------------|
| SK-01 | frontmatter 必須フィールド | name と description が YAML frontmatter に存在する | 各 SKILL.md の frontmatter を解析 | 不足フィールドを追加 |
| SK-02 | description の具体性 | Claude がいつそのスキルを使うべきか判断できる具体的な記述がある | description の文字数と内容 | トリガー条件や使用場面を description に追加 |
| SK-03 | 副作用スキルの安全策 | ファイル変更を伴うスキルにユーザー確認ステップがある | SKILL.md の本文で確認フローの有無 | 確認ゲートをワークフローに追加 |

## 一般判定ルール

| ID | check | expected state | evidence | remediation |
|----|-------|---------------|----------|-------------|
| GN-01 | .gitignore | `.env`、機密ファイル、`CLAUDE.local.md` が除外されている | .gitignore の内容 | 必要なエントリを追加 |
| GN-02 | .claude/rules/ | プロジェクトに固有のルールが `.claude/rules/` に配置されている（推奨） | rules/ ディレクトリの存在と内容 | パスベースルールの作成を提案 |
| GN-03 | settings.local.json | チーム共有設定と個人設定が分離されている | `.claude/settings.local.json` の存在 | 個人設定の分離を提案 |

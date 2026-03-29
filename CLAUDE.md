# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code プラグインを開発・管理するリポジトリ。プラグインはスキル、フック、エージェント、コマンド、MCP サーバー統合を含む。

## Plugin Structure

各プラグインは以下の構造に従う:
- `plugin.json` — マニフェスト（name, description, components の定義）
- `skills/` — SKILL.md ファイル（YAML frontmatter + 指示文）
- `hooks/` — フック定義（シェルスクリプト）
- `agents/` — エージェント定義（AGENT.md）
- `commands/` — スラッシュコマンド定義

## Security Rules (CRITICAL)

### 機密情報の保護
- API キー、トークン、パスワード、シークレットをコードやスキル定義にハードコードしない
- `.env` ファイル、`credentials.json`、秘密鍵ファイルはコミットしない
- 環境変数参照 (`$ENV_VAR`) を使い、値を直接埋め込まない
- テスト用のダミーデータには明示的にフェイクとわかる値を使う（例: `sk-test-fake-key-12345`）

### プロンプトインジェクション対策
- スキルやフックの入力値（`$ARGUMENTS` 等）を信頼しない — シェルコマンドに渡す前に必ずクォートまたはサニタイズする
- ユーザー入力をそのまま `eval` や `bash -c` に渡さない
- スキルの指示文に外部 URL からのコンテンツ取得を含めない
- `disable-model-invocation: true` を副作用のあるスキルに設定し、ユーザーの明示的な呼び出しのみ許可する

### 危険なコマンド実行の防止
- `rm -rf`、`git push --force`、`git reset --hard` などの破壊的コマンドをフックに含めない
- フックのコマンドは最小権限で実行する
- ネットワークアクセスを伴うフックは、送信先を明示的にホワイトリストで制限する

## Development Guidelines

- プラグインのスキル説明文 (`description`) は、Claude がいつそのスキルを使うべきか判断できるよう具体的に書く
- フックは高速で冪等であること（毎回の編集で実行されるため）
- 新しいプラグインコンポーネントを追加したら `/validate` で構造を検証する
- セキュリティに関わる変更は `/security-review` でレビューする

## セカンドオピニオン（Codex 連携）

`/consulting-codex` スキルが利用可能な場合、設計書や検討事項のレビューに積極的に活用する。

### いつ使うか
- 設計書・改善計画を作成したとき
- アーキテクチャや実装方針に複数の選択肢があるとき
- セキュリティに関わる判断を行うとき

### 改善ループ
1. 設計書や検討事項を `/consulting-codex` でレビュー依頼する
2. 指摘された懸念点を設計に反映する
3. 懸念点が解消されるまで 1-2 を繰り返す
4. 全懸念点が解消されたら実装に進む

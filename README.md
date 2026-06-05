# my-ai-plugins

Claude Code / Codex 両対応のプラグインマーケットプレイスリポジトリ。

## インストール

### Claude Code

`/plugin` の marketplace 追加で以下のソースを指定:

```
git@github.com:odaryo/my-ai-plugins.git
```

または:

```
odaryo/my-ai-plugins
```

### Codex

marketplace を追加してから `/plugins` でインストール:

```
codex plugin marketplace add odaryo/my-ai-plugins
```

- プラグイン本体の manifest: 各プラグインの `.codex-plugin/plugin.json`
- marketplace 定義: `.agents/plugins/marketplace.json`
- リポジトリローカルの補助スキルは `.agents/skills`（`.claude/skills` への symlink）から読み込まれる

## プラグイン一覧

| プラグイン | バージョン | 説明 |
|-----------|-----------|------|
| [consulting-codex](./consulting-codex) | 1.0.2 | Codex CLIを使った設計レビュー・技術相談・セカンドオピニオン取得 |
| [best-practices](./best-practices) | 1.0.1 | Claude Code ベストプラクティスの調査・監査・適用ワークフロー |
| [goal-implement](./goal-implement) | 1.0.0 | 指定した goal・要件の実装を、TDD実装・Codexレビュー・PR作成・相互レビュー・CI対応まで再開可能に完遂するオーケストレーション |

## consulting-codex

Codex CLI と連携し、設計書のレビュー・技術相談・セカンドオピニオンを取得するスキル。

**モード:**
- `code` — コード相談・実装相談
- `review` — 設計書・計画書のレビュー
- `arch` — アーキテクチャ相談
- `opinion` — セカンドオピニオン

**使用例:**
```
/consulting-codex review: .local/plans/feature-plan.md
/consulting-codex LaravelでN+1問題を解決するには？
/consulting-codex arch: マイクロサービスに分割すべきか？
```

**前提条件:** codex CLI がインストール・認証済みであること。

## best-practices

Web検索で最新のベストプラクティスを調査し、現在の設定と比較して改善計画を作成、ステップバイステップで適用するワークフロー。

## goal-implement

goal・要件（または issue）を渡すと、設計書作成 → TDD 実装（Red-Green-Refactor、毎サイクル2回の Codex レビュー）→ PR 作成 → Opus×Codex 相互レビュー（上限5往復）→ CI 対応 →（goal 指定時のみ）マージまでを自律的に完遂するオーケストレーションスキル。進捗を state として永続化し、中断しても `resume` で続きから再開できる。

**使用例:**
```
/goal-implement
# goal
- 要件を全て満たすこと
- PRを作成してエージェントレビューが終わること

# 目的
ログイン機能の追加

# 要件
- メールアドレスとパスワードで認証できる
```

**サブコマンド:**
- `/goal-implement resume [run-id]` — 中断した run を再開
- `/goal-implement status [run-id]` — 進捗の確認のみ
- `/goal-implement abort <run-id>` — run の中断

**前提条件:**
- codex CLI がインストール・認証済みであること（独立レビュアーとして使用）
- gh CLI が認証済みであること（PR 操作）
- Claude Code の Task サブエージェント（`model: sonnet` 指定）が利用可能であること

**注意:** branch 作成・PR 作成・（指定時）マージの副作用を持つため、モデルの自動呼び出しは無効（`disable-model-invocation: true`）。`/goal-implement` で明示的に起動する。

## ライセンス

MIT

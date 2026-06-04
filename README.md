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
| [consulting-codex](./consulting-codex) | 1.1.0 | Codex CLIを使った設計レビュー・技術相談・セカンドオピニオン取得 |
| [best-practices](./best-practices) | 1.0.1 | Claude Code ベストプラクティスの調査・監査・適用ワークフロー |

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

## ライセンス

MIT

# エラーハンドリング

原則: エラーに遭遇したら ①state.json を保存 ②この表に従って対応 ③表に無いエラーは状況と選択肢をユーザーに提示して blocked。**エラーを握りつぶして先に進まない。**

## 環境・前提

| 事象 | 対応 |
|------|------|
| `command not found: codex` | blocked。インストール手順を案内（レビュー省略での続行は不可） |
| codex 認証エラー | blocked。`codex login` を案内 |
| `gh` 未認証 | blocked。`gh auth login` を案内 |
| Task サブエージェント / `model: sonnet` 指定が利用不可 | blocked。環境制約を報告しユーザーの指示を仰ぐ |

## Git / GitHub

| 事象 | 対応 |
|------|------|
| dirty worktree（P3 開始時） | blocked。stash / commit をユーザーに確認（勝手に stash しない） |
| base branch がリモートと分岐 | blocked。rebase / merge の選択をユーザーに確認（勝手に reset しない） |
| push 失敗（権限・protected branch） | blocked。不足している権限・条件を報告 |
| PR 作成失敗 | `gh pr list --head <branch>` で既存 PR を確認（冪等性照合）。既存があればそれを使う。無ければ1回再試行し、失敗なら blocked |
| merge 失敗（branch protection・コンフリクト） | blocked。不足条件（レビュー必須等）またはコンフリクト状況を報告 |

## CI（P7 の分類詳細）

| 分類 | 判定基準 | 対応 |
|------|---------|------|
| 変更起因 | 失敗ログが今回の変更ファイル・テスト・lint 対象に紐づく | CI 修正ワーカー（SUBAGENT.md）で修正。最大3回。超過で blocked |
| flaky | 同一コミットに成功歴あり / タイムアウト・ネットワーク系の失敗 | `gh run rerun <run-id> --failed` を1回だけ。再失敗なら変更起因として扱う |
| 外部障害 | GitHub/インフラ/依存サービスの障害（変更と無関係なジョブも落ちている等） | 修正せず blocked。状況を報告し、復旧後に resume |

## ループ・暴走防止

| 事象 | 対応 |
|------|------|
| フェーズの試行上限到達 | blocked。試行履歴と残課題を報告 |
| 同一エラーが3回連続（`last_error.consecutive_count >= 3`） | **failed**。エラー内容と試行履歴を報告 |
| P6+P7 の合計戻り回数が8回超（`loop.p6_p7_roundtrips`） | blocked。レビューと CI が収束しない状況を報告 |
| Sonnet の報告とテスト実態の不一致（green と報告したが失敗する等） | 1回だけ具体的な失敗出力付きで再依頼。再発なら blocked |

## state / 実行管理

| 事象 | 対応 |
|------|------|
| state.json が破損・欠落 | 実状態＋run 成果物から再推定（STATE.md の resume 手順7）。特定不能なら再開位置をユーザーに確認 |
| ロックが取得できない | `.lock/owner.txt` を表示し、解除可否をユーザーに確認（勝手に解除しない） |
| pending_action が残留 | STATE.md の冪等性照合表で完了/未完了を判定してから続行 |
| Codex session 喪失 | 新規セッションにフォールバック（CODEX.md）。session_id を更新して続行 |
| コンテキスト逼迫の兆候 | state.json と成果物を保存し、`resume` での再開方法を報告して安全に区切る |

## blocked 時の報告フォーマット

```markdown
## ⛔ blocked: <run-id>
- フェーズ: <P*> / step: <step>
- 理由: <blocked_reason>
- これまでの達成: <要件チェックリストの状況、PR URL 等>
- 必要な対応: <ユーザーにしてほしいこと>
- 再開方法: `/goal-implement resume <run-id>`
```

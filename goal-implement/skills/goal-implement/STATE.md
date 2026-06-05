# 状態管理

真実源は Git/GitHub の実状態。state.json は再開位置を素早く特定するための補助キャッシュであり、Git/GitHub から復元できないローカル情報は run ディレクトリの成果物として残す。

## run ディレクトリ

### 保存先の発見

1. 実行先プロジェクトの CLAUDE.md / AGENTS.md / README から AI 作業文書の保存規約（例: 「.ai_text 配下に保存」）を探す
2. 規約があれば `<規約ディレクトリ>/runs/<run-id>/` を使う
3. なければ `.ai_text/runs/<run-id>/` を使い、完了報告で gitignore 追加を案内する
4. `run-id` は `goal-impl-<YYYYMMDD>-<内容を表す短い slug>`（例: `goal-impl-20260605-add-login`）

### 成果物レイアウト

```
<run-dir>/
├── state.json                      # 状態キャッシュ（コメントなしの有効な JSON）
├── .lock/                          # 排他ロック（mkdir で取得）
│   └── owner.txt                   # session 識別子と取得時刻
├── requirements.md                 # 要件チェックリストと判定根拠
├── reviews/<phase>-<連番>.json     # Codex/Opus の各レビュー結果（構造化形式）
├── test-results/<feature>-<連番>.md  # テスト実行結果サマリ
└── pr_review.md                    # P6 の統合レビューファイル
```

Git/GitHub から復元できない情報（要件判定・レビュー結果・テスト結果）は必ずこのディレクトリに書き残すこと。

## state.json スキーマ

コメントを含まない有効な JSON として生成する。フィールドの意味:

```json
{
  "schema_version": 1,
  "run_id": "goal-impl-20260605-add-login",
  "status": "running",
  "phase": "P4",
  "step": "F2:green",
  "last_completed_action": "commit F1 cycle 1",
  "pending_action": null,
  "goal": { "raw": "<入力全文>", "merge_requested": false },
  "requirements": [ { "id": "R1", "text": "...", "status": "pending" } ],
  "design_doc": "<設計書パス>",
  "base_branch": "main",
  "work_branch": "feat/add-login",
  "features": [ { "id": "F1", "name": "...", "status": "reviewed", "cycle_count": 1 } ],
  "pr": { "number": null, "url": null, "head_sha": null },
  "review": { "round": 0, "reviewed_sha": null, "open_findings": [], "review_file": "pr_review.md" },
  "ci": { "last_status": null, "ci_sha": null, "run_ids": [], "fix_attempts": 0 },
  "loop": { "p6_p7_roundtrips": 0 },
  "codex_session_id": null,
  "attempts": { "P0": 0, "P1": 0, "P2": 0, "P3": 0, "P5": 0, "P8": 0 },
  "last_error": { "message": null, "consecutive_count": 0 },
  "blocked_reason": null,
  "updated_at": "2026-06-05T10:00:00+09:00"
}
```

- `status`: `running | completed | blocked | failed | aborted`
- `features[].status`: `pending | red | green | refactored | reviewed`
- `requirements[].status`: `pending | done`
- `pending_action`: 構造化形式 `{ "id": "act-7", "type": "pr-comment", "target": "PR #12", "expected_result": "round-2 マーカー付きコメント", "started_at": "<ISO8601>" }`
- `loop.p6_p7_roundtrips`: P6→P7 / P7→P6 の遷移ごとにインクリメントする（上限8。中断・再開をまたいで保持される）

### フェーズ別カウンターの対応

| フェーズ | 使用するカウンター | 上限 |
|---------|------------------|------|
| P0/P1/P2/P3/P5/P8 | `attempts.<フェーズ名>` | PHASES.md の表どおり |
| P4 | `features[].cycle_count`（機能ごと） | 3 |
| P6 | `review.round` | 5 |
| P7 | `ci.fix_attempts` | 3 |
| P6⇔P7 往復 | `loop.p6_p7_roundtrips` | 8 |

## 状態の保存（atomic write）

state.json の更新は必ず一時ファイル経由で行う。`goal.raw` には任意のユーザー入力（クォート・`$` 等を含みうる）が入るため、**シェル展開されないクォート付き heredoc** で書く:

```bash
cat > "<run-dir>/state.json.tmp" <<'GOAL_IMPL_EOF'
<JSON全文>
GOAL_IMPL_EOF
mv "<run-dir>/state.json.tmp" "<run-dir>/state.json"
```

更新タイミング: ①各フェーズ終了時 ②副作用のある操作（branch 作成・commit・push・PR 作成・PR コメント・merge）の直前（`pending_action` セット）と完了確認後（結果記録＋`pending_action` を null に戻す）。

## 排他ロック（単一実行者）

run 開始・resume 時に取得する。`mkdir` はアトミックなのでロック取得に使える:

```bash
mkdir "<run-dir>/.lock" 2>/dev/null && printf 'session: %s\nacquired: %s\n' "<セッション識別子>" "<ISO8601>" > "<run-dir>/.lock/owner.txt" && echo LOCKED
```

- `mkdir` が失敗（既にロックあり）→ `.lock/owner.txt` の内容をユーザーに表示し、**解除して続行するかをユーザーに確認する**（期限切れに見えても勝手に解除しない）
- **終了状態（completed/blocked/failed/aborted）への遷移時に必ず解放する**: `rm -rf "<run-dir>/.lock"`

## 操作別の冪等性照合（resume 時・pending_action 残留時）

`pending_action` が残ったまま中断していた場合、その操作が実際に完了したかを以下で照合し、完了していればスキップ、未完了なら再実行する:

| 操作 type | 照合コマンド | 完了判定 |
|-----------|------------|---------|
| branch | `git branch --list <name>` / `git rev-parse --verify <name>` | ブランチが存在する |
| commit | `git log --oneline -5` | 該当メッセージ・内容のコミットが存在する |
| push | `git rev-parse <branch>` と `git rev-parse origin/<branch>` | SHA が一致する |
| pr-create | `gh pr list --head <branch> --json number,url` | PR が存在する |
| pr-comment | `gh pr view <番号> --json comments` | 本文に一意マーカーが存在する |
| merge | `gh pr view <番号> --json state` | state が MERGED |

PR コメントには必ず一意マーカーを本文先頭に付ける:

```markdown
<!-- goal-implement:<run-id>:round-<N>:<head-sha> -->
```

## SHA 整合

- PR への push のたびに `pr.head_sha` を更新する
- P6 完了時に `review.reviewed_sha = head_sha`、P7 成功時に `ci.ci_sha = head_sha` を記録する
- **head_sha が変わったら、古い `reviewed_sha`/`ci_sha` に基づく合格判定は無効**。該当フェーズを再実行する
- P8 では `reviewed_sha == ci_sha == 現在の head_sha`（`gh pr view <番号> --json headRefOid`）を確認してから完了/マージする

## resume 手順

1. run-id を特定する（引数指定、なければ run ディレクトリ群から最新の `running`/`blocked` を選ぶ）
2. ロックを取得する（上記。取得できなければユーザー確認）
3. state.json を読み、**実状態と照合する**:
   ```bash
   git status --short && git branch --list "<work_branch>" && git log --oneline -5
   gh pr list --head "<work_branch>" --json number,state,headRefOid   # PR があれば
   gh pr checks <番号>                                                 # PR があれば
   ```
4. `pending_action` が残っていれば冪等性照合表で完了/未完了を判定する
5. 実状態で完了が確認できたステップはスキップし、`phase`/`step` の位置から再開する
6. `status == blocked` の場合は `blocked_reason` を表示してユーザーの解除判断を確認し、**解除されたフェーズに対応するカウンター（上記「フェーズ別カウンターの対応」表を参照）のみ 0 にリセット**して再開する。`loop.p6_p7_roundtrips` はユーザーが明示的に「修正継続」を選んだ場合のみリセットする
7. state.json が破損・欠落している場合は、実状態＋run 成果物（requirements.md, reviews/, test-results/, pr_review.md）から `phase`/`step` を再推定する。特定できなければ状況を提示して再開位置の指定をユーザーに求める（**推測で続行しない**）

# フェーズ定義

各フェーズの手順・成功条件・試行上限。フェーズ終了ごとに state.json を更新する（`STATE.md`）。

## フェーズ一覧と上限

| # | フェーズ | 成功条件 | 最大試行 | 上限到達時 |
|---|---------|---------|---------|-----------|
| P0 | 入力・環境確認 | 必須項目が揃い完了条件が機械判定可能、環境前提を充足 | 1 | blocked |
| P1 | 方針検討 | 方針が要件全件をカバー | 2 | blocked |
| P2 | 設計書作成 | 設計書ファイル保存済み | 2 | blocked |
| P3 | ブランチ準備 | 作業ブランチ上で clean な状態 | 2 | blocked |
| P4 | TDD 実装 | 全機能実装済み・全テスト green・未解決 Critical/High ゼロ | 機能ごと3サイクル | blocked |
| P5 | PR 作成 | PR が OPEN | 2 | blocked |
| P6 | PR レビュー | open の懸念ゼロ（詳細: `REVIEW.md`） | 5往復 | 重大度による（下記） |
| P7 | CI 対応 | 必須 CI 全件 success | 3 | blocked |
| P8 | 完了処理 | 終了状態の確定 | 1 | — |

- P6⇔P7 は相互に遷移しうる（レビュー修正→CI 再実行、CI 修正→レビュー再確認）。遷移のたびに `state.loop.p6_p7_roundtrips` をインクリメントし、**8回を上限**として超過時は blocked（中断・再開をまたいで保持する）
- 同一エラーが3回連続したらフェーズを問わず `failed`

## P0: 入力・環境確認

1. 引数を入力契約（SKILL.md）に照らして解析する。issue 指定があれば `gh issue view <番号> --json title,body` で本文を取得し要件に統合する
2. 要件を `R1, R2, ...` の ID 付きチェックリストに変換する。「完了とは何か」が判定不能な要件はユーザーに確認する
3. 環境プリフライト（全て満たさなければ不足項目を報告して blocked）:
   ```bash
   codex --version && codex login status   # Codex CLI 存在＋認証
   gh auth status                          # gh 認証
   ```
   - Task ツールで `model: sonnet` のサブエージェントが利用可能であること（利用できない環境ならユーザーに確認）
4. マージ指定の有無を goal の記述から判定し、`state.goal.merge_requested` に記録する

## P1: 方針検討

1. 要件・目的・既存コードベースを調査し、対応方針を策定する
2. goal に対応方針が書かれている場合は、その方針で要件全件を満たせるか検証する。満たせない場合は差分と代替案を方針に明記する
3. 方針が要件全件（R1..Rn）をどうカバーするかの対応表を作る

## P2: 設計書作成

1. 保存先を発見する: 実行先プロジェクトの CLAUDE.md / AGENTS.md / README から AI 作業文書の保存規約を探す。規約があればそれに従う。なければ `.ai_text/plans/` 配下に保存し、gitignore 推奨を完了報告で案内する
2. 設計書には「方針・要件対応表・実装する機能の分割（F1, F2, ...）・各機能のテスト観点」を含める
3. 機能分割 F1..Fn を `state.features` に記録する

## P3: ブランチ準備

1. git プリフライト:
   ```bash
   git status --short          # dirty なら blocked（stash/commit をユーザーに確認）
   git fetch origin
   git rev-parse --abbrev-ref HEAD
   ```
2. base branch（入力指定 or デフォルトブランチ）のローカルが fast-forward 可能か確認する:
   ```bash
   git merge-base --is-ancestor <base> origin/<base> && echo ff-ok
   ```
   分岐していたら blocked（勝手に reset しない）。fast-forward 可能なら `git pull --ff-only` で最新化する
3. 作業ブランチを作成する（名前衝突時は連番を付ける）。`state.work_branch` に記録する

## P4: TDD 実装（機能 F1..Fn を順に）

1機能 = 1サイクル以上の Red-Green-Refactor。**1サイクル内の Codex レビューは2回**。

1. **Red**: Sonnet サブエージェント（`SUBAGENT.md` のテストワーカー）にテスト作成を委譲。テストが**失敗する**ことを確認する
2. **レビュー①（テストレビュー）**: Codex にテストをレビューさせる（`CODEX.md` のテストレビュープロンプト）。Critical/High があれば Sonnet が修正→1回だけ再レビュー
3. **Green**: Sonnet に最小実装を委譲。テストが通ることを確認する
4. **Refactor**: Sonnet にリファクタリングを委譲。テスト green を維持する
5. **レビュー②（実装レビュー）**: Codex に diff をレビューさせる。Critical/High があれば Sonnet が修正し再テスト→1回だけ再レビュー
6. **checkpoint commit**: サイクル完了ごとに作業ブランチへコミットする（未 push 変更の消失防止）:
   ```bash
   git add -A && git commit -m "feat: <機能名> (goal-implement F<n> cycle <m>)"
   ```
7. レビュー結果・テスト結果サマリは run ディレクトリに成果物として保存する（`STATE.md` の成果物レイアウト）
8. 残 Critical/High は次サイクルに持ち越す。機能あたり3サイクルで解消しなければ blocked

## P5: PR 作成

1. コミットを整理し push する（`pending_action` を記録してから実行）
2. PR を作成する。本文に含めるもの: 目的、要件チェックリスト（R1..Rn と達成状況）、設計書への参照、テスト結果。本文は任意テキスト（クォート等を含みうる）のため、ファイルに書いてから `--body-file` で渡す:
   ```bash
   gh pr create --title "<タイトル>" --body-file "<run-dir>/pr_body.md"
   ```
3. `state.pr.number` / `state.pr.head_sha` を記録する

## P6: PR レビュー

`REVIEW.md` の収束プロトコルに従う。終了条件:

- open の懸念ゼロ → 通過
- 5往復到達・**Medium/Low のみ残存** → 残懸念を PR にコメント投稿して通過
- 5往復到達・**Critical/High 残存** → 残懸念を PR にコメント投稿して **blocked**（ユーザーが「修正継続 / リスク受容 / 中止」を選択するまでマージ禁止）

## P7: CI 対応

1. `gh pr checks <番号>` で CI 状態を取得する。全件 success なら通過
2. 失敗があれば `gh run view <run-id> --log-failed` でログを取得し、分類する:

| 分類 | 判定基準 | 対応 |
|------|---------|------|
| 変更起因 | 失敗ログが今回の変更ファイル・テストに紐づく | Sonnet が修正（最大3回）。修正後 push し CI 再確認 |
| flaky | 同一コミットで成功歴がある / タイムアウト系 | 1回だけ re-run。再失敗なら変更起因として扱う |
| 外部障害 | インフラ・依存サービス起因 | 修正せず blocked、ユーザーに報告 |

3. push で head_sha が変わったら P6 のレビュー判定を無効化し、P6 を再実行する（SHA 整合は `STATE.md`）

## P8: 完了処理

1. SHA 整合検証: `reviewed_sha == ci_sha == 現在の PR head_sha` を確認する。不一致なら該当フェーズ（P6/P7）へ戻る
2. `state.goal.merge_requested == true` の場合のみマージする。false なら**絶対にマージしない**
   - マージ方式を確認する: `gh repo view --json squashMergeAllowed,mergeCommitAllowed,rebaseMergeAllowed`。squash 可なら `--squash`、不可なら許可されている方式を使う
   - `pending_action` 記録 → `gh pr merge <方式> <番号>` → 結果記録
3. state.json を終了状態に更新し、ロックを解放し、完了報告を出す

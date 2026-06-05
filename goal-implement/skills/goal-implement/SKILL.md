---
name: goal-implement
description: >
  指定した goal・目的・要件（または issue）の実装を、設計書作成→TDD実装→Codexレビュー→
  PR作成→Opus×Codex相互レビュー→CI対応→（goal指定時のみ）マージまで、途中で止まらず
  完遂する再開可能なオーケストレーション。「実装を完遂して」「ゴールまで実装して」
  「issueを最後まで実装して」のような依頼や、goal/目的/要件形式のプロンプトで使用する。
  `resume`（再開）/ `status`（状態確認）/ `abort`（中断）のサブコマンドを持つ。
disable-model-invocation: true
---

# goal-implement: 実装完遂オーケストレーション

goal・要件を受け取り、PR 作成とエージェントレビュー完了（goal にマージ指定があればマージ）まで自律的に完遂する。役割分担:

| エージェント | 役割 |
|---|---|
| このセッション（オーケストレーター） | フェーズ進行・state 管理・レビュー採否の最終判定・PR レビューの一方の書き手 |
| Sonnet サブエージェント（Task ツール, `model: sonnet`） | テスト作成・実装・リファクタリング・修正（テンプレート: `SUBAGENT.md`） |
| Codex CLI（独立レビュアー） | 実装レビュー・PR レビューのもう一方の書き手（呼び出し方: `CODEX.md`） |

これは「保証」ではなく**再開可能なオーケストレーション**である。中断しても `resume` で続きから再開できるよう、各フェーズの進捗を state に永続化しながら進める。

## 引数解釈（最初に判定する）

| 入力 | 動作 |
|------|------|
| `status [run-id]` | state.json を読んで要約表示のみ（実行しない）。run-id 省略時は最新の run |
| `resume [run-id]` | 中断した run を再開（→ `STATE.md` の resume 手順） |
| `abort <run-id>` | run を `aborted` にして停止。ブランチ・PR は消さず手動整理を案内 |
| 上記以外 | goal 形式の新規 run として解釈（下記） |

### goal 形式の入力契約

```markdown
# goal
- 要件を全て満たすこと
- PRを作成してエージェントレビューが終わること
- （任意）レビュー・CI完了後にマージすること   ← この記述がある場合のみ自動マージ

# 目的
（背景・目的）

# 要件
- 要件1
- 要件2

# 任意項目
- issue: #123 または URL（gh issue view で本文を取得し要件に統合）
- base_branch: main（省略時はデフォルトブランチ）
- test_commands: テストコマンド（省略時はプロジェクトから自動検出）
```

- `# goal` と `# 要件`（または issue 指定）は必須。不足していたらユーザーに質問し、回答が得られなければ `blocked` で停止する
- **マージ可否は goal 内の明示記述のみで判定する。推測しない**

## 実行原則

1. **止まらない**: ユーザーへの質問は P0（入力・環境確認）と blocked 時のみ。それ以外のフェーズでは自己判断で進める
2. **真実源は Git/GitHub**: state.json は再開位置のキャッシュ。判断に迷ったら `git`/`gh` の実状態を確認する
3. **副作用の前後で state 保存**: branch 作成・commit・push・PR 作成・PR コメント・merge の直前に `pending_action` を記録し、完了後に結果（SHA・PR 番号等）を記録する（手順: `STATE.md`）
4. **各フェーズの試行上限を守る**: 上限到達で `blocked`、同一エラー3回連続で `failed`。無限リトライしない
5. **レビュー省略での完遂は不可**: Codex CLI が使えない場合はスキップせず `blocked` にする

## フェーズループ

run 開始時に `STATE.md` を読み、run ディレクトリ・state.json・ロックを初期化してから、P0 から順に実行する。**各フェーズの開始時に該当 reference を Read し、終了時に state.json を更新してから次へ進む。**

| # | フェーズ | 内容 | 詳細 |
|---|---------|------|------|
| P0 | 入力・環境確認 | 入力契約の充足確認、環境プリフライト（codex CLI・gh 認証・Task 利用可否） | `PHASES.md` |
| P1 | 方針検討 | 要件から対応方針を策定（goal に方針があれば妥当性を検証） | `PHASES.md` |
| P2 | 設計書作成 | 方針を設計書化し、実行先プロジェクトの規約に従い保存 | `PHASES.md` |
| P3 | ブランチ準備 | git プリフライト → base branch 最新化 → 作業ブランチ作成 | `PHASES.md` |
| P4 | TDD 実装 | 機能単位の Red-Green-Refactor。**毎サイクル2回の Codex レビュー**（①テスト作成後 ②実装・リファクタ後） | `PHASES.md` `SUBAGENT.md` `CODEX.md` |
| P5 | PR 作成 | commit 整理 → push → PR 作成（本文に要件チェックリスト） | `PHASES.md` |
| P6 | PR レビュー | Opus×Codex 独立レビュー → 相互評価 → 統合 → ブラッシュアップ（上限5往復） | `REVIEW.md` |
| P7 | CI 対応 | CI 失敗を分類（変更起因/flaky/外部障害）し、変更起因のみ Sonnet が修正 | `PHASES.md` `ERRORS.md` |
| P8 | 完了処理 | SHA 整合検証 → goal にマージ指定があればマージ → 完了報告 | `PHASES.md` |

reference は `${CLAUDE_PLUGIN_ROOT}/skills/goal-implement/` 配下にある。プラグインとしてではなくリポジトリローカルのスキルとして実行されている場合（`CLAUDE_PLUGIN_ROOT` 未設定）は、**この SKILL.md と同じディレクトリ**から Read する。

## 終了状態

| 状態 | 条件 |
|------|------|
| `completed` | 要件チェックリスト全件 done・全テスト成功・未解決 Critical/High ゼロ・PR 作成済み・必須 CI 成功（＋マージ指定時はマージ済み） |
| `blocked` | 試行上限到達・入力/環境不足・PR レビュー5往復後に Critical/High 残存など、ユーザー判断が必要。理由と再開方法を必ず報告する |
| `failed` | 同一エラー3回連続など自動回復不能 |
| `aborted` | ユーザーの明示中断 |

終了状態への遷移時は必ず: ①state.json を最終更新 ②ロックを解放 ③ユーザーに「終了状態・要件の達成状況・PR の URL・残課題・再開方法（blocked 時）」を報告する。

## エラー時

エラーや想定外の状況に遭遇したら `ERRORS.md` の対応表に従う。対応表にないエラーは、state を保存した上で状況と選択肢をユーザーに提示して `blocked` にする。

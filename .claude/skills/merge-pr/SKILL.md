---
name: merge-pr
description: >
  指定した PR を squash マージし、マージ後の後片付け（デフォルトブランチへの切替・pull・
  マージ済みローカルブランチの削除）までを一括で行う。「PR をマージして」「PR #3 を取り込んで」
  「マージして後片付けして」「squash マージして」のような依頼で使用する。
  CI 通過の確認とユーザーへの最終確認を挟んでから実行する。
disable-model-invocation: true
---

# PR の squash マージと後片付け

引数: PR 番号（例: `/merge-pr 3`）。省略時は現在のブランチに紐づく PR を自動特定する。

マージは取り消しが難しい操作のため、各ステップの前提が崩れていたら**先に進まず中止して報告する**こと。

## 手順

### 1. 事前チェック

1. `git status --short` で作業ツリーを確認する。未コミット変更があれば中止し、commit または stash を案内する（後続の checkout に巻き込まれるのを防ぐため）。
2. PR を特定する。
   - 引数あり → その番号を使う。
   - 引数なし → `gh pr view --json number,title` で現在ブランチの PR を探す。見つからなければ `gh pr list` を提示してユーザーに選んでもらう。
3. PR 情報を取得する:
   ```bash
   gh pr view <番号> --json number,title,state,headRefName,baseRefName,mergeStateStatus,url
   ```
   - `state` が `OPEN` でなければ中止する（MERGED なら後片付けのみ提案する）。
4. デフォルトブランチを取得する:
   ```bash
   git symbolic-ref --short refs/remotes/origin/HEAD | sed 's@^origin/@@'
   ```
   取得できない場合は `main` とする。`baseRefName` がデフォルトブランチと異なる場合は、その旨を伝えて続行するか確認する。

### 2. CI 確認

`gh pr checks <番号>` で CI の状態を確認する。

- **fail がある** → 中止し、失敗したジョブ名とリンクを報告する。
- **pending がある** → バックグラウンドで完了を待つ:
  ```bash
  until [ "$(gh pr checks <番号> --json bucket --jq 'all(.bucket != "pending")' 2>/dev/null)" = "true" ]; do sleep 10; done; gh pr checks <番号>
  ```
  完了後に fail があれば中止する。

### 3. 最終確認（必須）

PR のタイトル・ブランチ・変更概要（`gh pr diff <番号> --stat`）を表示し、ユーザーの承認を得る。
**承認なしでマージを実行しない**（このリポジトリは auto-merge を無効化し、必ずレビューを挟む方針のため）。

### 4. squash マージ

```bash
gh pr merge --squash <番号>
```

リモートブランチはリポジトリ設定で自動削除される。自動削除されない設定のリポジトリでは `--delete-branch` の追加を検討する。

### 5. ローカル後片付け

1. デフォルトブランチへ切り替えて最新化する:
   ```bash
   git checkout <デフォルトブランチ> && git pull --ff-only
   ```
2. 削除済みリモート追跡ブランチを掃除する:
   ```bash
   git fetch --prune
   ```
3. PR の `headRefName` と同名のローカルブランチが存在すれば削除する:
   ```bash
   git branch -D "<headRefName>"
   ```
   - squash マージではローカルブランチが「マージ済み」と判定されず `git branch -d` は失敗するため `-D` を使う。**`-D` は PR のマージ完了を確認した後にのみ使うこと**（未マージのコミットを失わないため）。
   - ローカルに存在しなければスキップする。ブランチ名は必ずクォートする。

### 6. 結果報告

以下を報告する:

- マージした PR（番号・タイトル・URL）
- デフォルトブランチの最新コミット（`git log --oneline -1`）
- 削除したローカルブランチ名（スキップした場合はその旨）

途中で失敗した場合は、**どのステップまで完了したか**と残りの手動手順を正確に報告する。

## エラー時の対応

| 状況 | 対応 |
|------|------|
| 未コミット変更がある | 中止。commit / stash を案内 |
| CI が fail | 中止。失敗ジョブとログのリンクを報告 |
| `mergeStateStatus` が DIRTY（コンフリクト） | 中止。デフォルトブランチの取り込み（rebase / merge）を案内 |
| `gh pr merge` が branch protection で拒否 | 中止。不足している条件（レビュー必須など）を報告 |
| `git pull --ff-only` が失敗 | ローカルのデフォルトブランチが分岐している。状況を報告し、勝手に reset しない |

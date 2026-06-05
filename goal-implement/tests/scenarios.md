# goal-implement テストシナリオ

実プロジェクトでの手動テスト計画。構造検証（validate_plugins.py）では動作は確認できないため、配布前に実行先プロジェクトで以下を確認する。

## 1. 正常系: start → completed（マージ指定なし）

```
/goal-implement
# goal
- 要件を全て満たすこと
- PRを作成してエージェントレビューが終わること

# 目的
サンプル機能の追加

# 要件
- <小さな機能要件1つ>
```

**確認項目:**
- [ ] P0 で環境プリフライト（codex / gh / Task）が実行される
- [ ] run ディレクトリと state.json・ロックが作成される
- [ ] 設計書が実行先プロジェクトの規約に従う場所に保存される
- [ ] P4 で Red（失敗確認）→ レビュー① → Green → Refactor → レビュー② の順に進む
- [ ] Codex レビューが構造化 JSON で `reviews/` に保存される
- [ ] サイクル完了ごとに checkpoint commit が作られる
- [ ] PR 本文に要件チェックリストが含まれる
- [ ] P6 で pr_review.md が作成され、Opus・Codex 両方の所見が統合される
- [ ] **マージされない**（goal にマージ指定なし）
- [ ] 終了時にロックが解放され、完了報告が出る

## 2. 正常系: マージ指定あり

goal に「レビュー・CI完了後にマージすること」を追加して実行。

- [ ] P6 通過・CI 成功後に `gh pr merge --squash` が実行される
- [ ] マージ前に reviewed_sha == ci_sha == head_sha の検証が行われる

## 3. resume: 中断からの再開

シナリオ1の P4 途中でセッションを中断し、新しいセッションで:

```
/goal-implement resume <run-id>
```

- [ ] state.json と実状態（ブランチ・コミット）の照合が行われる
- [ ] 完了済みステップ（作成済みブランチ・コミット済み機能）がスキップされる
- [ ] PR・コメントが重複作成されない

## 4. status / abort

```
/goal-implement status
/goal-implement abort <run-id>
```

- [ ] status は表示のみで何も実行しない
- [ ] abort で status が aborted になり、ロックが解放され、ブランチ・PR は残る

## 5. blocked: 入力不足

`# goal` のみで要件・issue 指定なしで実行。

- [ ] 質問が出る → 回答しないと blocked になり、再開方法が案内される

## 6. blocked: 環境不足

codex 未認証の状態（または PATH から外す）で実行。

- [ ] P0 で blocked になり、`codex login` 等の案内が出る
- [ ] レビューをスキップして進まない

## 7. blocked: dirty worktree

未コミット変更がある状態で実行。

- [ ] P3 で blocked になり、stash/commit の確認が出る（勝手に stash しない）

## 8. PR レビュー上限

（観察ベース）P6 で懸念が解消しない場合:

- [ ] 5往復で打ち切られる
- [ ] Critical/High 残存なら PR コメント＋blocked（マージされない）
- [ ] Medium/Low のみなら PR コメント＋通過
- [ ] PR コメント先頭に `<!-- goal-implement:... -->` マーカーが付く

## 9. CI 失敗対応

意図的に lint エラー等を仕込んだ状態で PR を作らせる。

- [ ] CI 失敗が分類され、変更起因として Sonnet が修正する
- [ ] 修正 push 後、P6 のレビュー判定が無効化され再レビューされる（SHA 整合）

## 10. 多重実行防止

run 実行中に別セッションから同じ run を resume する。

- [ ] ロック取得に失敗し、owner 情報が表示され、ユーザー確認なしに解除されない

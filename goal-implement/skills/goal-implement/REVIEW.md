# レビュー形式と PR レビュー収束プロトコル

## 構造化レビュー形式（全レビュー共通）

```json
{
  "severity": "Critical | High | Medium | Low",
  "file": "src/auth/login.ts",
  "line": 42,
  "evidence": "問題の根拠（コード断片・挙動）",
  "required_fix": "修正担当がそのまま着手できる具体的な修正手順",
  "status": "open | fixed | accepted | rejected"
}
```

- **合格基準: Critical/High ゼロ**。Medium/Low はオーケストレーターが採否を判断し、不採用（rejected）は理由を記録する
- `accepted` = リスク受容（理由と判断者を記録）。`fixed` は修正コミットの SHA を添える

## P4（実装フェーズ）のレビュー運用

- レビュー①（テスト）・レビュー②（実装）とも、Critical/High があれば Sonnet に修正させ、**再レビューは1回まで**
- 再レビュー後も残る Critical/High は次サイクルに持ち越す。機能あたり3サイクルで解消しなければ blocked
- 各レビュー結果は `<run-dir>/reviews/P4-<連番>.json` に保存する

## P6: PR レビュー収束プロトコル（Opus × Codex）

### 手順（1往復 = 手順4→5の1周）

1. **独立レビュー**: 自分（オーケストレーター）と Codex がそれぞれ PR diff を独立にレビューし、構造化形式で所見を出す。自分のレビューは Codex の結果を見る**前に**書き終えること（バイアス防止）
2. **相互評価**: Codex に自分の所見を渡して評価（agree/disagree＋補足）を得る。Codex の所見は自分が同様に評価する
3. **統合**: 両者の所見を `<run-dir>/pr_review.md` に統合する（下記フォーマット）。重複は1件にまとめ、相互評価で disagree が出た指摘は根拠を比較して採否を決める（判断はオーケストレーターが行い、判断理由を記録する）
4. **修正**: open の Critical/High（および採用した Medium）を Sonnet に修正させ、push する。head_sha 更新により CI が再実行される点に注意（P7 との往復は `state.loop.p6_p7_roundtrips` で数え、合計8回まで）
5. **再確認**: 修正後の diff を Codex に再レビューさせ（resume）、自分も確認し、pr_review.md の各 finding の status を更新する

### pr_review.md フォーマット

```markdown
# PR #<番号> 統合レビュー

- run: <run-id> / round: <N> / reviewed_sha: <sha>

## Findings

| ID | severity | file:line | 指摘 | 出所 | status | 判断メモ |
|----|----------|-----------|------|------|--------|---------|
| PR-1 | High | src/x.ts:42 | ... | Codex | fixed (abc1234) | |
| PR-2 | Medium | src/y.ts:10 | ... | Opus | rejected | <理由> |
```

### 終了条件

| 状況 | 動作 |
|------|------|
| open の懸念ゼロ | 早期終了。P6 通過（round 数は問わない） |
| 5往復到達・Medium/Low のみ残存 | 残懸念を PR にコメント投稿 → P6 通過 |
| 5往復到達・Critical/High 残存 | 残懸念を PR にコメント投稿 → **blocked**。ユーザーが「修正継続 / リスク受容（accepted に変更し理由を記録）/ 中止」を選択するまでマージ禁止 |

### PR コメント

残懸念のコメントは冪等性マーカーを本文先頭に付けて投稿する。本文は任意テキスト（クォート等を含みうる）のため、クォート付き heredoc でファイルに書いてから `--body-file` で渡す:

```bash
cat > "<run-dir>/pr_comment.md" <<'GOAL_IMPL_EOF'
<!-- goal-implement:<run-id>:round-<N>:<head-sha> -->
## goal-implement レビュー残懸念
<pr_review.md の open 部分の要約>
GOAL_IMPL_EOF
gh pr comment <番号> --body-file "<run-dir>/pr_comment.md"
```

投稿前に同一マーカーのコメントが既に無いか `gh pr view <番号> --json comments` で確認する（resume 時の重複防止）。

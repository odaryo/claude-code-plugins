# consulting-codex テストシナリオ

## テストケース

### 1. コード相談（デフォルト）

**入力:**
```
/consulting-codex LaravelでN+1問題を解決するには？
```

**期待される動作:**
- モード: `code`
- モデル: codex CLIデフォルト（`-m` 省略）
- Bash呼び出し: **1回**（codex exec のみ）

**検証ポイント:**
- [ ] キーワード判断でコード相談モードが選択される
- [ ] `-m` が省略されcodex CLIデフォルトモデルが使用される
- [ ] インラインのcodeプロンプトが使用される

---

### 2. ファイル指定（.md → review）

**入力:**
```
/consulting-codex .local/plans/feature-plan.md この設計に問題はある？
```

**期待される動作:**
- モード: `review`
- モデル: 一般モデル（config.tomlから取得、`-codex`除去）
- Bash呼び出し: **1回**（モデル判定+exec統合）
- Read呼び出し: **1回**（対象ファイルのみ）

**検証ポイント:**
- [ ] 拡張子 `.md` で設計レビューモードが選択される
- [ ] Readツールでファイル内容が読み込まれる
- [ ] モデル判定とexecが1つのBashコマンドで実行される

---

### 3. ファイル指定（.php → code）

**入力:**
```
/consulting-codex src/app/Services/UserService.php このコードの改善点は？
```

**期待される動作:**
- モード: `code`
- モデル: codex CLIデフォルト（`-m` 省略）
- Bash呼び出し: **1回**

**検証ポイント:**
- [ ] 拡張子 `.php` でコード相談モードが選択される
- [ ] ファイル内容が `{{コンテキスト}}` に含まれる

---

### 4. 明示プレフィックス

**入力:**
```
/consulting-codex arch: マイクロサービスに分割すべきか？
```

**期待される動作:**
- モード: `arch`
- モデル: 一般モデル
- Bash呼び出し: **1回**（モデル判定+exec統合）

**検証ポイント:**
- [ ] 明示プレフィックス `arch:` でモードが上書きされる
- [ ] プレフィックスはプロンプトから除去される

---

### 5. 引数なし（会話コンテキストから即実行）

**入力:**
```
（直前の会話でDB設計について議論中）
/consulting-codex
```

**期待される動作:**
- 直前の会話から質問を推定し即実行
- 推定した質問を出力ヘッダーに表示
- コンテキストが全くない場合のみ確認

**検証ポイント:**
- [ ] 会話コンテキストから適切な質問が推定される
- [ ] モードが会話内容に基づいて自動選択される
- [ ] 推定結果が出力に含まれる（確認なしで即実行）

---

### 6. エラーケース: codex未インストール

**入力:**
```
/consulting-codex テスト質問
```

**検証ポイント:**
- [ ] 適切なエラーメッセージが表示される
- [ ] インストール手順が案内される

---

### 7. エラーケース: ファイル不存在

**入力:**
```
/consulting-codex nonexistent-file.md レビューして
```

**検証ポイント:**
- [ ] ファイル存在チェックが行われる
- [ ] 「ファイルが見つかりません: nonexistent-file.md」と表示される

---

### 8. config取得失敗時のフォールバック

**入力:**
```
/consulting-codex review: .local/plans/feature-plan.md
```

**シミュレーション:** config.toml が存在しない、またはmodel行がない

**検証ポイント:**
- [ ] MODELが空のため `-m` フラグなしでcodex CLIデフォルトにフォールバックする
- [ ] `{model}` が `default` と表示される
- [ ] モデル判定+exec統合コマンド内でフォールバックが完結する

---

### 9. セカンドオピニオン（キーワード判断）

**入力:**
```
/consulting-codex Claude Codeがこの設計を提案したけど、どう思う？
```

**期待される動作:**
- モード: `opinion`
- Bash呼び出し: **1回**

**検証ポイント:**
- [ ] 「どう思う」キーワードでセカンドオピニオンモードが選択される

---

### 10. resume: session id指定で再開

**入力:**
```
（前回の実行でsession id: 019d0a9c-8fa8-7503-9c67-f79594fe2b67 が表示されている）
/consulting-codex resume: 前回の指摘を踏まえて再レビュー
```

**期待される動作:**
- resumeフラグ: オン
- Bash呼び出し: **1回**（resume + フォールバックchain統合）
- コマンド: `codex exec resume <session-id> - ... || (echo "---FALLBACK:new---" && codex exec -s read-only ...)`

**検証ポイント:**
- [ ] `resume:` プレフィックスが検出・除去され、resumeフラグがオンになる
- [ ] 会話コンテキストからsession idが取得される
- [ ] `codex exec resume <session-id> -` で実行される（`-s` なし、stdinは `-` 指定）
- [ ] 失敗時は `||` で `---FALLBACK:new---` を出力し新規execにフォールバック
- [ ] 出力に `[再レビュー]` と session id が表示される

---

### 11. resume＋モード指定

**入力:**
```
/consulting-codex resume: review: .local/plans/feature-plan.md 修正したので再確認
```

**期待される動作:**
- resumeフラグ: オン
- モード: `review`
- Bash呼び出し: **1回**（モデル判定+resume+フォールバック統合）

**検証ポイント:**
- [ ] `resume:` と `review:` が順に検出・除去される
- [ ] reviewモードでresume実行される
- [ ] ファイルのgit diffが変更サマリとして取得される

---

### 12. resume: session id不明時の--lastフォールバック

**入力:**
```
（新しい会話セッションで、前回のsession idが不明）
/consulting-codex resume: 前回の議論の続き
```

**期待される動作:**
- session idが会話コンテキストにない
- `--last` で実行、失敗時は新規execにフォールバック
- Bash呼び出し: **1回**（--last || new exec の chain）

**検証ポイント:**
- [ ] session id不明が正しく検出される
- [ ] `codex exec resume --last` で実行される
- [ ] フォールバック通知がユーザーに表示される

---

### 13. resume: セッション存在しない場合の新規execフォールバック

**入力:**
```
/consulting-codex resume: 前回のレビューの続き
```

**シミュレーション:** 指定したsession idのセッションが既に削除されている

**期待される動作:**
- `codex exec resume` がエラーを返す
- `||` チェインで新規execにフォールバック
- 出力に `---FALLBACK:new---` マーカーが含まれる
- Bash呼び出し: **1回**

**検証ポイント:**
- [ ] resumeエラーが `||` チェインでキャッチされる
- [ ] 新規execにフォールバックして実行される
- [ ] フォールバック通知がユーザーに表示される
- [ ] 新規セッションのsession idが出力に表示される

---

## パフォーマンス検証

| シナリオ | 期待Bash | 期待Read |
|---------|---------|---------|
| code通常 | 1 | 0 |
| review通常 | 1 | 1（対象ファイル） |
| arch/opinion通常 | 1 | 0 |
| resume（全モード） | 1 | 0-1 |

## 実行方法

各シナリオを手動で実行し、期待される動作と実際の動作を比較する。

```bash
# 事前確認
codex --version && codex login status
```

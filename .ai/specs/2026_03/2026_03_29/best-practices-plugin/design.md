# best-practices プラグイン設計書

## 概要

Claude Code の運用ベストプラクティスをWeb検索で調査し、現在の設定と比較して改善を適用するプラグイン。3つのスキル（調査→監査→適用）のワークフローを提供する。

## プラグイン構造

```
best-practices/
  .claude-plugin/
    plugin.json              # プラグインマニフェスト
  skills/
    research/
      SKILL.md               # /bp-research: Web調査・評価
    audit/
      SKILL.md               # /bp-audit: 監査・改善計画作成
      REFERENCE.md           # 評価基準・チェックリスト
    apply/
      SKILL.md               # /bp-apply: 改善適用
```

## スキル詳細

### `/bp-research` — ベストプラクティス調査

**目的:** Web検索でClaude Codeの最新ベストプラクティスを調査し、有用な知見をレポートにまとめる

**ワークフロー:**
1. 過去レポートの読み込み（差分追加方式）
   - `.ai/setting_reports/**/bp-research.md` を全件検索・読み込み
   - 既出の URL リストを作成（重複スキップ用）
2. WebSearch で複数クエリを実行
3. 検索結果から既出 URL を除外
4. WebFetch で新規記事の本文を取得
5. 4軸で評価（信頼性・正確性・コミュニティ評価・改善効果）
6. 新規知見のみレポートに保存
   - 保存先: `.ai/setting_reports/{YYYY_MM}/{DD}/bp-research.md`
   - 同日に既存ファイルがある場合は連番付与: `bp-research-2.md`, `bp-research-3.md`
   - ヘッダーに参照した過去レポート一覧を記載
   - 既出としてスキップした URL 数も記録

**検索クエリ戦略:**
| クエリ | 目的 |
|--------|------|
| `"Claude Code" best practices CLAUDE.md` | CLAUDE.md の書き方 |
| `"Claude Code" hooks settings.json configuration` | フック・設定パターン |
| `"Claude Code" productivity tips workflow` | ワークフロー最適化 |
| `"Claude Code" skills plugins custom commands` | スキル・プラグインパターン |
| `site:docs.anthropic.com Claude Code` | 公式ドキュメント |
| `site:github.com "CLAUDE.md" example` | 実際の CLAUDE.md 事例 |

**評価基準（5軸）:**
| 軸 | High | Medium | Low |
|----|------|--------|-----|
| 公式整合性 | 公式ドキュメントと一致・公式リポジトリ由来 | 概ね正確だが一部古い可能性 | 矛盾あり・非公式のみ |
| 要件適合性 | Claude Code設定に直接適用可能 | 適用にカスタマイズが必要 | 一般論・具体性なし |
| 安全性 | 破壊的変更なし・ロールバック容易 | 一部設定に影響あるが限定的 | 既存設定を壊すリスクあり |
| 導入コスト | 1ファイルの追加/変更で完了 | 複数ファイルの変更が必要 | 大規模な構成変更が必要 |
| 検証容易性 | 適用後の効果をすぐ確認可能 | 確認に手動テストが必要 | 効果測定が困難 |

**情報源の優先順位（固定）:**
1. 公式ドキュメント（docs.anthropic.com）
2. 公式リポジトリ・サンプル（github.com/anthropics）
3. 実績あるコミュニティ記事（技術ブログ、高スターリポジトリ）
4. その他（SNS、個人投稿）

**出力フォーマット:**
```markdown
---
type: bp-research
created_at: {ISO 8601 datetime}
claude_code_version: {claude --version の出力}
source_urls: [{URL1}, {URL2}, ...]
based_on_reports: [{過去レポートパス1}, ...]
tool_version: "1.0.0"
---

# Claude Code ベストプラクティス調査レポート
日付: {date}

## 調査サマリ
- 検索クエリ: [list]
- 調査記事数: N
- 有用な知見数: N
- 既出スキップ数: N
- 参照した過去レポート: [list of paths]

## 知見一覧

### 1. {知見タイトル}
- 出典: {URL}
- 公式整合性: {High/Medium/Low} — {理由}
- 要件適合性: {High/Medium/Low} — {理由}
- 安全性: {High/Medium/Low} — {理由}
- 導入コスト: {High/Medium/Low} — {理由}
- 検証容易性: {High/Medium/Low} — {理由}
- カテゴリ: {CLAUDE.md / settings / hooks / skills / workflow}
- 内容: {具体的な推奨事項}
- 期待効果: {何が改善されるか}

## カテゴリ別まとめ
### CLAUDE.md 関連
### settings.json 関連
### フック関連
### スキル・ワークフロー関連
```

---

### `/bp-audit` — 設定監査・改善計画作成

**目的:** 調査レポートと現在の設定を比較し、ギャップを特定して優先度付き改善計画を作成する

**ワークフロー:**
1. 最新の `.ai/setting_reports/{YYYY_MM}/{DD}/bp-research.md` を読み込み（または引数でパス指定）
2. 現在��設定を収集（デフォルト: repo-local のみ）:
   - `CLAUDE.md`（ルート＋サブディレ��トリ）
   - `.claude/settings.json` / `.claude/settings.local.json`
   - `.claude/skills/` の全 SKILL.md
   - `.claude/rules/` のルールファイル
   - `.gitignore` の Claude 関連エントリ
   - **[opt-in]** `~/.claude/settings.json`（���ローバル設定）— `$ARGUMENTS` に `--global` 指定時のみ。計画書では「参考提案」セクションに分離
3. 各知見に対して互換性チェック:
   - 現行 Claude Code バージョンで有効か（`claude --version` で確認）
   - 設定キーが実在するか（公式ドキュメントと照合）
   - 廃止・非推奨項目でないか
4. 各知見に対して現状を評価: Already Implemented / Partial / Missing
5. 影響度×難易度で優先度付け
6. 改善計画を `.ai/setting_reports/{YYYY_MM}/{DD}/bp-plan.md` に保存

**REFERENCE.md に含める判定ルール集:**

各ルールは `check → expected state → evidence → remediation` の形式で定義する。

#### CLAUDE.md 判定ルール
| check | expected state | evidence | remediation |
|-------|---------------|----------|-------------|
| プロジェクト概要 | 先頭セクションに概要あり | CLAUDE.md 先頭20行 | 概要セクション追加 |
| ビルド/テスト/リントコマンド | 非標準コマンドが記載 | manifest + CLAUDE.md | コマンドセクション追加 |
| コーディング規約 | 言語デフォルトと異なる規約が記載 | CLAUDE.md 検索 | 差分のみ記載 |
| セキュリティルール | セキュリティセクションあり | CLAUDE.md 検索 | セクション追加 |
| コンテキスト効率 | 100行以内、`@import` で外部化 | CLAUDE.md 行数 | 長い参照を外部化 |

#### settings.json 判定ルール
| check | expected state | evidence | remediation |
|-------|---------------|----------|-------------|
| セキュリティフック | PostToolUse Write\|Edit に機密検出フックあり | settings.json | フック追加 |
| フォーマッターフック | プロジェクトにフォーマッターがある場合、PostToolUse に設定 | package.json等 + settings.json | フック追加 |
| matcher スコープ | 必要最小限のツールに限定 | settings.json hooks | matcher 修正 |
| timeout | 30秒以下 | settings.json hooks | timeout 調整 |

#### スキル判定ルール
| check | expected state | evidence | remediation |
|-------|---------------|----------|-------------|
| frontmatter | name, description が存在 | SKILL.md YAML | frontmatter 追加 |
| description 具体性 | いつ使うか判断できる記述 | description 文字列 | description 改善 |
| 副作用スキルの制御 | ファイル変更スキルは安全策あり | SKILL.md 内容 | 確認ゲート追加 |

#### 一般判定ルール
| check | expected state | evidence | remediation |
|-------|---------------|----------|-------------|
| .gitignore | `.env`, 機密ファイルが除外 | .gitignore 内容 | エントリ追加 |
| .claude/rules/ | パスベースルールを活用（任意） | rules/ ディレクトリ | ルール作成提案 |

**出力フォーマット:**
```markdown
---
type: bp-plan
created_at: {ISO 8601 datetime}
based_on_research: {bp-research.md のパス}
claude_code_version: {claude --version の出力}
scope: repo-local  # または repo-local+global
tool_version: "1.0.0"
---

# Claude Code 改善計画
日付: {date}
調査レポート: {path}

## 現状サマリ
- CLAUDE.md: {有/無, 行数}
- settings.json: {有/無, フック数}
- スキル数: N
- ルール数: N

## 改善アクション一覧

### [P1] {タイトル} (影響: High / 難易度: Easy)
- 現状: {現在の状態}
- 推奨: {推奨される状態}
- 対象ファイル: {path}
- 変更内容: {具体的な追加・変更内容}
- 根拠: 知見 #{N}

### [P2] ...

## 適用しない推奨事項（理由付き）
```

---

### `/bp-apply` — 改善適用

**目的:** 監査計画に基づき、ユーザー確認を取りながら設定を改善する

**フラグ:** `disable-model-invocation` は設定しない（対話的ワークフローに必要なため）。安全性はユーザー確認ゲートで担保する。

**ワークフロー:**
1. 事前チェック:
   - `git status` でクリーンな作業ツリーか確認
   - ダーティな場合は先にコミットを推奨
2. 最新の `.ai/setting_reports/{YYYY_MM}/{DD}/bp-plan.md` を読み込み（または引数でパス指定）
3. 優先度順に各アクションを処理:
   a. 変更内容を表示（対象ファイル、before/after の diff）
   b. 「この変更を適用しますか？」とユーザーに確認
   c. Yes → 変更を適用（Edit/Write ツール使用）
   d. 適用後にファイルを読み戻して検証
   e. No → スキップして次へ
4. 適用結果サマリを `.ai/setting_reports/{YYYY_MM}/{DD}/bp-applied.md` に保存

**安全策:**
- 各変更で個別にユーザー確認
- 適用前にクリーンな git 状態を推奨
- ロールバック手順を提示（`git checkout -- <file>`）
- APIキーやトークンを含む設定変更は行わない

**出力フォーマット:**
```markdown
---
type: bp-applied
created_at: {ISO 8601 datetime}
based_on_plan: {bp-plan.md のパス}
claude_code_version: {claude --version の出力}
tool_version: "1.0.0"
---

# Claude Code 改善適用結果
日付: {date}
改善計画: {path}

## 適用結果

| # | アクション | 状態 | 対象ファイル |
|---|-----------|------|------------|
| P1 | {タイトル} | 適用済み | {path} |
| P2 | {タイトル} | スキップ | {path} |

## ロールバック手順
git checkout -- <file1> <file2> ...
```

---

## データフロー

```
WebSearch/WebFetch
       ↓
/bp-research → .ai/setting_reports/{YYYY_MM}/{DD}/bp-research.md
                       ↓
現在の設定 → /bp-audit → .ai/setting_reports/{YYYY_MM}/{DD}/bp-plan.md
                       ↓
            /bp-apply → 設定更新 → .ai/setting_reports/{YYYY_MM}/{DD}/bp-applied.md
```

各フェーズは独立して実行可能。引数なしなら最新のレポートを自動検出、引数ありなら指定パスを使用。

### ファイル検索ロジック

**過去レポートの走査（Phase 1 の差分追加用）:**
1. `.ai/setting_reports/` 配下の全 `bp-research*.md` を Glob で検索
2. パターン: `.ai/setting_reports/*/*/bp-research*.md`
3. 全件読み込み、各レポートの「出典 URL」を抽出して既出リストを構築

**最新レポートの検索（Phase 2, 3 での入力ファイル検出）:**
1. `.ai/setting_reports/*/*/bp-{research|plan}*.md` を Glob で検索
2. 各ファイルの frontmatter から `created_at` を読み取り
3. `created_at` が最新のファイルを使用（メタデータ駆動）
4. frontmatter がないファイルはディレクトリ名から日付を復元（フォールバック）
5. `$ARGUMENTS` でパスが指定された場合はそちらを優先

**連番ルール:**
- 初回: `bp-research.md`（連番なし）
- 2回目: `bp-research-2.md`
- N回目: `bp-research-{N}.md`
- bp-plan, bp-applied も同様

## セキュリティ考慮事項

1. **プロンプトインジェクション:** WebFetch で取得した外部コンテンツは信頼せず、評価結果としてのみ使用
2. **機密情報保護:** `/bp-apply` はAPIキーやトークンの値そのものを設定ファイルに書き込まない
3. **破壊的変更防止:** `/bp-apply` は各変更でユーザー確認を必須とし、事前に git 状態をチェック
4. **スコープ制限:** フックの matcher を最小限にスコープし、全ツールイベントに対して発火しないようにする
5. **互換性検証:** Phase 2 で各知見の互換性を検証（現行バージョンで有効か、設定キーが実在するか、廃止項目でないか）
6. **監査スコープ分離:** デフォルトは repo-local のみ。グローバル設定は opt-in で参考提案に留める

## plugin.json

```json
{
  "name": "best-practices",
  "description": "Claude Code ベストプラクティスの調査・監査・適用ワークフロー。Web検索で最新のベストプラクティスを調査し、現在の設定と比較して改善計画を作成、ステップバイステップで適用する。",
  "version": "1.0.0",
  "author": {
    "name": "odaryo"
  }
}
```

## 実装順序

1. `best-practices/.claude-plugin/plugin.json` — マニフェスト
2. `best-practices/skills/research/SKILL.md` — Phase 1 スキル
3. `best-practices/skills/audit/SKILL.md` + `REFERENCE.md` — Phase 2 スキル
4. `best-practices/skills/apply/SKILL.md` — Phase 3 スキル
5. `/validate` でプラグイン構造を検証
6. `/security-review` でセキュリティレビュー

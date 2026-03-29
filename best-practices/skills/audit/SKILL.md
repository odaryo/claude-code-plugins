---
name: bp-audit
description: >
  bp-research の調査レポートと現在の Claude Code 設定を比較し、改善計画を作成する。
  CLAUDE.md、settings.json、スキル、フック、ルールの現状を判定ルール集に基づいて評価し、
  互換性チェック後にギャップを特定して優先度付きのアクションリストを出力する。
  「設定を診断」「改善計画」「監査」「audit」時に使用。
---

Claude Code の設定を監査し、改善計画を作成してください。

## Phase 1: 調査レポートの読み込み

1. `$ARGUMENTS` でレポートパスが指定されている場合はそのファイルを読み込み
2. 指定がない場合、`.ai/setting_reports/*/*/bp-research*.md` を Glob で検索
3. 各ファイルの frontmatter から `created_at` を読み取り、最新のファイルを選択
4. frontmatter がないファイルはディレクトリ名から日付を復元（フォールバック）
5. レポートが見つからない場合は「先に `/bp-research` を実行してください」と案内

## Phase 2: 現在の設定を収集

**デフォルトスコープ: repo-local のみ**

以下のファイルを読み込み:
- `CLAUDE.md`（プロジェクトルート）
- サブディレクトリの `CLAUDE.md`（Glob: `**/CLAUDE.md`、ルート以外）
- `.claude/settings.json`
- `.claude/settings.local.json`（存在する場合）
- `.claude/skills/` 配下の全 SKILL.md（Glob: `.claude/skills/**/SKILL.md`）
- `.claude/rules/` 配下の全ファイル（存在する場合）
- `.gitignore`

**`$ARGUMENTS` に `--global` が含まれる場合のみ追加:**
- `~/.claude/settings.json`（グローバル設定）
- グローバル設定の改善提案は計画書で「参考提案」セクションに分離する

各ファイルが存在しない場合は「未設定」として記録（エラーにしない）。

## Phase 3: 互換性チェック

調査レポートの各知見に対して:

1. **バージョン確認:** `claude --version` を実行し、知見が現行バージョンで有効か確認
2. **設定キー確認:** 推奨される設定キーが実在するか（settings.json のスキーマと照合）
3. **廃止項目確認:** 非推奨・廃止された設定やフラグが含まれていないか

互換性チェックに失敗した知見は「互換性なし」として計画から除外し、理由を記録する。

## Phase 4: ギャップ分析

`${CLAUDE_PLUGIN_ROOT}/skills/audit/REFERENCE.md` の判定ルール集を読み込み、各ルールに対して:

1. **check**: 何を確認するか
2. **expected state**: 期待される状態
3. **evidence**: 現在の設定から得た実際の状態
4. **remediation**: 改善アクション

判定結果を3段階で分類:
- **Already Implemented**: 期待状態を満たしている
- **Partial**: 一部満たしているが改善の余地あり
- **Missing**: 未実装

加えて、調査レポートの知見のうち判定ルール集にない項目も個別に評価する。

## Phase 5: 優先度付け

各改善アクションに優先度を付与:

| 影響度 \ 難易度 | Easy | Medium | Hard |
|----------------|------|--------|------|
| **High** | P1 | P2 | P3 |
| **Medium** | P2 | P3 | P4 |
| **Low** | P3 | P4 | P5 |

## Phase 6: 改善計画の作成・保存

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
日付: {YYYY-MM-DD}
調査レポート: {bp-research.md のパス}

## 現状サマリ
- CLAUDE.md: {有/無, 行数, 主要セクション一覧}
- settings.json: {有/無, フック数, フック一覧}
- スキル数: N（一覧）
- ルール数: N
- スコープ: repo-local / repo-local+global

## 改善アクション一覧

### [P1] {アクションタイトル} (影響: High / 難易度: Easy)
- 現状: {現在の状態}
- 推奨: {推奨される状態}
- 対象ファイル: {path}
- 変更内容:
  ```
  {具体的な追加・変更内容（diff形式推奨）}
  ```
- 根拠: 知見 #{N} / 判定ルール {rule name}
- 互換性: 確認済み

### [P2] ...

## 互換性なしのため除外した項目
| 知見 | 理由 |
|------|------|
| {タイトル} | {除外理由} |

## 参考提案（グローバル設定）
（--global 指定時のみ。repo-local とは別セクション）

## 適用しない推奨事項（理由付き）
```

**保存先:** `.ai/setting_reports/{YYYY_MM}/{DD}/bp-plan.md`（同日連番: `-2`, `-3`...）

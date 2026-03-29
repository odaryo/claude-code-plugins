---
name: validate
description: プラグインの構造を検証する。plugin.json の整合性、スキル・フック・エージェントの定義が正しいか、必須フィールドの欠落がないかをチェックする。プラグインを作成・変更した後に使用する。
---

以下の手順でプラグインの構造を検証してください:

1. **plugin.json の検証**
   - ファイルが存在し、有効な JSON であること
   - `name`, `description` フィールドが存在すること
   - 参照されているコンポーネントファイルが実際に存在すること

2. **スキルの検証** (skills/ ディレクトリ)
   - 各 SKILL.md に有効な YAML frontmatter があること
   - `name` と `description` が frontmatter に含まれていること
   - 副作用のあるスキルに `disable-model-invocation: true` が設定されていること

3. **フックの検証** (hooks/ ディレクトリ)
   - フック定義が有効な JSON/YAML 形式であること
   - イベントタイプ（PreToolUse, PostToolUse, Stop）が正しいこと
   - コマンドが実行可能であること（パスが存在するか確認）

4. **エージェントの検証** (agents/ ディレクトリ)
   - 各 AGENT.md に有効な YAML frontmatter があること
   - `name` と `description` が含まれていること

5. **結果レポート**
   - 問題があれば具体的な修正方法を提示
   - 問題がなければ「検証OK」と報告

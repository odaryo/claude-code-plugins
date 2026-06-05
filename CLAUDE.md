# CLAUDE.md

Claude Code でこのリポジトリを扱う場合も、共通の作業指示は [AGENTS.md](./AGENTS.md) を正とします。

## Claude Code 固有の補足

- Claude Code 向けのローカル設定と補助スキルは `.claude/` 配下を正とする。
- 新しい Claude Code 補助スキルを追加する場合は `.claude/skills/<skill-name>/SKILL.md` に配置する。
- `.agents/skills`（Codex の探索パス）は `.claude/skills` への symlink のため、共通利用したい補助スキルは `.claude/skills` 側に追加する。
- 配布用プラグインのスキルをこのリポジトリ内でも使う場合は、`.claude/skills/<skill-name>` から `../../<plugin>/skills/<skill-name>` への symlink を張る（例: `goal-implement`）。実体はプラグイン側を正とし、二重管理しない。
- プラグイン本体を変更した後は、必要に応じて `/validate` で構造を確認する。CI（GitHub Actions）でも `scripts/validate_plugins.py` による同等の構造検証が PR ごとに実行される。
- セキュリティに関わる変更やリリース前の確認では、必要に応じて `/security-review` を使う。

## Claude Plugin 構成

- Claude Code plugin manifest は各プラグインの `.claude-plugin/plugin.json` に置く。
- marketplace 定義はルートの `.claude-plugin/marketplace.json` を更新する。Codex 用の `.agents/plugins/marketplace.json` と各プラグインの `.codex-plugin/plugin.json` も同期する（`scripts/validate_plugins.py` で整合性を検証できる）。
- Claude Code 向けのスキル説明文 `description` は、自動選択しやすいよう具体的に書く。
- 副作用のある Claude Code スキルには `disable-model-invocation: true` を設定する。

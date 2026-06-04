# .codex

Codex 向けのリポジトリローカル補足です。

共通の作業指示はリポジトリルートの `AGENTS.md` を正とします。Claude Code 固有の補足は `CLAUDE.md` を参照してください。

## Skills

このリポジトリの補助スキルは `.claude/skills` を正とします。

Codex CLI が探索するリポジトリローカルのスキル配置は `.agents/skills` です。`.agents/skills` を `.claude/skills` へのシンボリックリンクとして管理し、同じ補助スキルを Claude Code と Codex の両方から参照できるようにします。

`.codex/skills` は旧構成との互換のために残しているシンボリックリンクです。新しい参照は `.agents/skills` を正とします。

## Plugins

Codex 向けの plugin marketplace 定義は `.agents/plugins/marketplace.json` に置きます。各プラグインの Codex 用 manifest は `<plugin>/.codex-plugin/plugin.json` です。

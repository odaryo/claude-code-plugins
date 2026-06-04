#!/usr/bin/env python3
"""マーケットプレースとプラグインの構造を検証するスクリプト。

検証項目:
- .claude-plugin/marketplace.json の JSON 構文と必須フィールド
- 各プラグインの source ディレクトリと .claude-plugin/plugin.json の存在・必須フィールド
- marketplace.json と plugin.json の name / version の一致
- SKILL.md の YAML frontmatter（name / description 必須、disable-model-invocation は boolean）

エラーは全件収集してから報告し、1件以上あれば exit 1。
"""

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

errors: list[str] = []


def error(msg: str) -> None:
    errors.append(msg)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        error(f"{path.relative_to(ROOT)}: invalid JSON: {e}")
        return None


def check_frontmatter(path: Path) -> None:
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        error(f"{rel}: YAML frontmatter がありません")
        return
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        error(f"{rel}: frontmatter の YAML が不正です: {e}")
        return
    if not isinstance(data, dict):
        error(f"{rel}: frontmatter がマッピングではありません")
        return
    for key in ("name", "description"):
        if not data.get(key):
            error(f"{rel}: frontmatter.{key} は必須です")
    dmi = data.get("disable-model-invocation")
    if dmi is not None and not isinstance(dmi, bool):
        error(f"{rel}: disable-model-invocation は boolean である必要があります")


def check_plugin(entry: dict) -> None:
    name = entry.get("name", "(name 未設定)")
    source = entry.get("source")
    if not entry.get("name"):
        error("marketplace.json: plugins[].name は必須です")
    if not source:
        error(f"marketplace.json: {name}: source は必須です")
        return

    source_dir = (ROOT / source).resolve()
    if not source_dir.is_dir():
        error(f"{name}: source ディレクトリが存在しません: {source}")
        return

    manifest_path = source_dir / ".claude-plugin" / "plugin.json"
    if not manifest_path.is_file():
        error(f"{name}: .claude-plugin/plugin.json がありません")
        return

    manifest = load_json(manifest_path)
    if manifest is None:
        return
    rel = manifest_path.relative_to(ROOT)

    for key in ("name", "description", "version"):
        if not manifest.get(key):
            error(f"{rel}: {key} は必須です")

    if manifest.get("name") and manifest["name"] != entry.get("name"):
        error(
            f"{rel}: name '{manifest['name']}' が marketplace の "
            f"'{entry.get('name')}' と一致しません"
        )
    if (
        manifest.get("version")
        and entry.get("version")
        and manifest["version"] != entry["version"]
    ):
        error(
            f"{rel}: version '{manifest['version']}' が marketplace の "
            f"'{entry['version']}' と一致しません"
        )

    # SKILL.md の発見（2形式に対応）
    # - skills: "./" → プラグインルート直下の SKILL.md
    # - それ以外 → skills/*/SKILL.md
    skills_field = manifest.get("skills")
    if skills_field == "./":
        skill_files = [source_dir / "SKILL.md"]
        if not skill_files[0].is_file():
            error(f"{name}: skills が './' ですがルートに SKILL.md がありません")
            return
    else:
        skill_files = sorted((source_dir / "skills").glob("*/SKILL.md"))
        if not skill_files:
            error(f"{name}: SKILL.md が1件も見つかりません")
            return

    for skill_file in skill_files:
        check_frontmatter(skill_file)


def main() -> int:
    marketplace_path = ROOT / ".claude-plugin" / "marketplace.json"
    if not marketplace_path.is_file():
        print(f"ERROR: {marketplace_path} がありません", file=sys.stderr)
        return 1

    marketplace = load_json(marketplace_path)
    if marketplace is not None:
        for key in ("name", "owner", "plugins"):
            if not marketplace.get(key):
                error(f"marketplace.json: {key} は必須です")
        for entry in marketplace.get("plugins") or []:
            check_plugin(entry)

    if errors:
        for msg in errors:
            print(f"ERROR: {msg}", file=sys.stderr)
        print(f"\n{len(errors)} 件のエラーがあります", file=sys.stderr)
        return 1

    print("OK: すべての検証に合格しました")
    return 0


if __name__ == "__main__":
    sys.exit(main())

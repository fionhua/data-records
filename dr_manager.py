# dr_manager.py
# data-records category manager (single-file, zero-deps)
# Windows-friendly. Python 3.9+

from __future__ import annotations
import argparse
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


DEFAULT_ROOT = r"D:\workSpace\data-records"


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def slugify_filename(name: str) -> str:
    """
    Convert product name to a safe filename for Windows:
    - trims spaces
    - converts whitespace to "-"
    - removes illegal characters: <>:"/\|?* and control chars
    - collapses multiple '-' and '_' runs
    """
    name = (name or "").strip()
    if not name:
        return "unnamed-product"

    # Replace whitespace with hyphen
    name = re.sub(r"\s+", "-", name)

    # Remove illegal Windows filename chars and control chars
    name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "", name)

    # Normalize repeated separators
    name = re.sub(r"[-_]{2,}", "-", name).strip("-_.")

    return name or "unnamed-product"


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


@dataclass
class Store:
    root: Path
    meta_dir: Path
    meta_file: Path
    data: Dict[str, Dict[str, List[str]]]  # country -> cat1 -> [cat2...]

    @staticmethod
    def load(root: Path) -> "Store":
        meta_dir = root / "_meta"
        meta_file = meta_dir / "categories.json"
        ensure_dir(meta_dir)

        if meta_file.exists():
            raw = json.loads(meta_file.read_text(encoding="utf-8"))
        else:
            raw = {"cn": {}}  # default country only
            meta_file.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")

        # basic normalization
        if "cn" not in raw:
            raw["cn"] = {}

        return Store(root=root, meta_dir=meta_dir, meta_file=meta_file, data=raw)

    def save(self) -> None:
        self.meta_file.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    def countries(self) -> List[str]:
        return sorted(self.data.keys())

    def cat1_list(self, country: str) -> List[str]:
        return sorted(self.data.get(country, {}).keys())

    def cat2_list(self, country: str, cat1: str) -> List[str]:
        return sorted(self.data.get(country, {}).get(cat1, []))

    def add_country(self, country: str) -> None:
        if country not in self.data:
            self.data[country] = {}

    def add_cat1(self, country: str, cat1: str) -> None:
        self.add_country(country)
        self.data[country].setdefault(cat1, [])

    def add_cat2(self, country: str, cat1: str, cat2: str) -> None:
        self.add_cat1(country, cat1)
        lst = self.data[country][cat1]
        if cat2 not in lst:
            lst.append(cat2)
            lst.sort()

    def remove_cat2(self, country: str, cat1: str, cat2: str) -> bool:
        lst = self.data.get(country, {}).get(cat1)
        if not lst:
            return False
        if cat2 in lst:
            lst.remove(cat2)
            return True
        return False

    def remove_cat1(self, country: str, cat1: str) -> bool:
        c = self.data.get(country)
        if not c or cat1 not in c:
            return False
        del c[cat1]
        return True

    def sync_dirs(self, country: Optional[str] = None) -> List[Path]:
        created: List[Path] = []
        countries = [country] if country else self.countries()
        for c in countries:
            for cat1 in self.cat1_list(c):
                for cat2 in self.cat2_list(c, cat1):
                    p = self.root / c / cat1 / cat2
                    if not p.exists():
                        ensure_dir(p)
                        created.append(p)
        return created

    def target_dir(self, country: str, cat1: str, cat2: str) -> Path:
        # does not auto-create; caller may call sync_dirs first
        return self.root / country / cat1 / cat2


def yaml_escape_multiline(text: str, indent: int = 2) -> str:
    """
    YAML block literal | with indentation.
    """
    text = text or ""
    pad = " " * indent
    # Preserve line breaks
    lines = text.splitlines() or [""]
    return "\n".join(pad + line for line in lines)


def render_yaml_template(product_name: str, description: str, country: str, cat1: str, cat2: str) -> str:
    safe_name = product_name.replace('"', '\\"')
    header = [
        "# data-records.net product stub",
        f"# generated_at: {now_iso()}",
        f"# path: {country}/{cat1}/{cat2}/{slugify_filename(product_name)}.yaml",
        "",
        "product:",
        f'  name: "{safe_name}"',
        "  description: |",
        yaml_escape_multiline(description, indent=4),
        "",
    ]
    return "\n".join(header).rstrip() + "\n"


def cmd_list(store: Store, country: str) -> None:
    print(f"Root: {store.root}")
    print(f"Countries: {', '.join(store.countries())}")
    if country not in store.data:
        print(f"[WARN] country '{country}' not found in meta, existing only.")
        return
    cat1s = store.cat1_list(country)
    if not cat1s:
        print(f"No categories under {country}.")
        return
    for cat1 in cat1s:
        cat2s = store.cat2_list(country, cat1)
        print(f"- {country}/{cat1}: {', '.join(cat2s) if cat2s else '(no cat2)'}")


def cmd_add(store: Store, country: str, cat1: Optional[str], cat2: Optional[str]) -> None:
    if not cat1:
        store.add_country(country)
        store.save()
        print(f"Added/ensured country: {country}")
        return
    if not cat2:
        store.add_cat1(country, cat1)
        store.save()
        print(f"Added/ensured cat1: {country}/{cat1}")
        return
    store.add_cat2(country, cat1, cat2)
    store.save()
    print(f"Added/ensured cat2: {country}/{cat1}/{cat2}")


def cmd_rm(store: Store, country: str, cat1: str, cat2: Optional[str]) -> None:
    if cat2:
        ok = store.remove_cat2(country, cat1, cat2)
        store.save()
        print("Removed." if ok else "Not found.")
    else:
        ok = store.remove_cat1(country, cat1)
        store.save()
        print("Removed." if ok else "Not found.")


def cmd_sync(store: Store, country: Optional[str]) -> None:
    created = store.sync_dirs(country=country)
    if not created:
        print("No new directories needed (already in sync).")
    else:
        print("Created directories:")
        for p in created:
            print(f"  {p}")


def cmd_gen(store: Store, country: str, cat1: str, cat2: str, name: str, desc: str, overwrite: bool) -> None:
    # Ensure meta paths exist (but do not force-add unless you want)
    # We choose to be strict to prevent accidental typos.
    if country not in store.data:
        raise SystemExit(f"country '{country}' not in meta. Add it first.")
    if cat1 not in store.data[country]:
        raise SystemExit(f"cat1 '{cat1}' not in meta under {country}. Add it first.")
    if cat2 not in store.data[country].get(cat1, []):
        raise SystemExit(f"cat2 '{cat2}' not in meta under {country}/{cat1}. Add it first.")

    store.sync_dirs(country=country)
    target_dir = store.target_dir(country, cat1, cat2)
    ensure_dir(target_dir)

    fname = slugify_filename(name) + ".yaml"
    out_path = target_dir / fname

    if out_path.exists() and not overwrite:
        raise SystemExit(f"File already exists: {out_path} (use --overwrite to replace)")

    yaml_text = render_yaml_template(name, desc, country, cat1, cat2)
    out_path.write_text(yaml_text, encoding="utf-8")
    print(f"Generated: {out_path}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dr_manager",
        description="Manage data-records categories and generate YAML stubs.",
    )
    p.add_argument("--root", default=DEFAULT_ROOT, help=f"Root path (default: {DEFAULT_ROOT})")

    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("list", help="List countries/cat1/cat2")
    sp.add_argument("--country", default="cn")

    sp = sub.add_parser("add", help="Add country/cat1/cat2 to meta")
    sp.add_argument("--country", default="cn")
    sp.add_argument("--cat1", default=None)
    sp.add_argument("--cat2", default=None)

    sp = sub.add_parser("rm", help="Remove cat1 or cat2 from meta (does not delete files)")
    sp.add_argument("--country", default="cn")
    sp.add_argument("--cat1", required=True)
    sp.add_argument("--cat2", default=None)

    sp = sub.add_parser("sync", help="Create missing directories based on meta")
    sp.add_argument("--country", default=None, help="Sync only one country (default: all)")

    sp = sub.add_parser("gen", help="Generate a product YAML stub at selected path")
    sp.add_argument("--country", default="cn")
    sp.add_argument("--cat1", required=True)
    sp.add_argument("--cat2", required=True)
    sp.add_argument("--name", required=True, help="Product name (used as filename too)")
    sp.add_argument("--desc", default="", help="Description/label text")
    sp.add_argument("--overwrite", action="store_true")

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    root = Path(args.root)
    ensure_dir(root)
    store = Store.load(root)

    if args.cmd == "list":
        cmd_list(store, args.country)
    elif args.cmd == "add":
        cmd_add(store, args.country, args.cat1, args.cat2)
    elif args.cmd == "rm":
        cmd_rm(store, args.country, args.cat1, args.cat2)
    elif args.cmd == "sync":
        cmd_sync(store, args.country)
    elif args.cmd == "gen":
        cmd_gen(store, args.country, args.cat1, args.cat2, args.name, args.desc, args.overwrite)
    else:
        raise SystemExit("Unknown command")


if __name__ == "__main__":
    main()

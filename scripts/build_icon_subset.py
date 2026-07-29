"""Build tiny Font Awesome webfonts and CSS for icons used by public templates."""
from __future__ import annotations

import re
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_TEMPLATES = ROOT / "app" / "templates"
FONT_AWESOME = ROOT / "node_modules" / "@fortawesome" / "fontawesome-free"
SOURCE_CSS = FONT_AWESOME / "css" / "all.css"
OUTPUT_CSS = ROOT / "app" / "static" / "css" / "icons.min.css"
OUTPUT_FONTS = ROOT / "app" / "static" / "fonts"
ICON_PATTERN = re.compile(r"\b(fab|fas|far|fa)\s+(fa-[a-z0-9-]+)\b", re.IGNORECASE)


def discover_icons() -> tuple[set[str], set[str]]:
    solid: set[str] = set()
    brands: set[str] = set()
    for template in PUBLIC_TEMPLATES.glob("*.html"):
        contents = template.read_text(encoding="utf-8")
        for prefix, icon_name in ICON_PATTERN.findall(contents):
            (brands if prefix.lower() == "fab" else solid).add(icon_name.lower())
    return solid, brands


def find_codepoint(css: str, icon_name: str) -> int:
    match = re.search(
        rf"\.{re.escape(icon_name)}:{{1,2}}before\s*\{{\s*content:\s*\"\\([0-9a-fA-F]+)\";",
        css,
    )
    if not match:
        raise RuntimeError(f"Font Awesome mapping not found: {icon_name}")
    return int(match.group(1), 16)


def subset_font(source: Path, destination: Path, codepoints: set[int]) -> None:
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = ["*"]
    options.desubroutinize = True
    font = TTFont(source)
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(unicodes=codepoints)
    subsetter.subset(font)
    destination.parent.mkdir(parents=True, exist_ok=True)
    font.save(destination)


def main() -> None:
    source_css = SOURCE_CSS.read_text(encoding="utf-8")
    solid_icons, brand_icons = discover_icons()
    solid_map = {name: find_codepoint(source_css, name) for name in sorted(solid_icons)}
    brand_map = {name: find_codepoint(source_css, name) for name in sorted(brand_icons)}

    subset_font(
        FONT_AWESOME / "webfonts" / "fa-solid-900.woff2",
        OUTPUT_FONTS / "fa-solid-subset.woff2",
        set(solid_map.values()),
    )
    subset_font(
        FONT_AWESOME / "webfonts" / "fa-brands-400.woff2",
        OUTPUT_FONTS / "fa-brands-subset.woff2",
        set(brand_map.values()),
    )

    rules = [
        '@font-face{font-family:"Font Awesome 6 Free";font-style:normal;font-weight:900;font-display:swap;src:url("../fonts/fa-solid-subset.woff2") format("woff2")}',
        '@font-face{font-family:"Font Awesome 6 Brands";font-style:normal;font-weight:400;font-display:swap;src:url("../fonts/fa-brands-subset.woff2") format("woff2")}',
        ".fa,.fas,.far,.fab{display:inline-block;font-style:normal;font-variant:normal;line-height:1;text-rendering:auto;-webkit-font-smoothing:antialiased}",
        '.fa,.fas,.far{font-family:"Font Awesome 6 Free";font-weight:900}',
        '.fab{font-family:"Font Awesome 6 Brands";font-weight:400}',
    ]
    for icon_name, codepoint in sorted({**solid_map, **brand_map}.items()):
        rules.append(f'.{icon_name}::before{{content:"\\{codepoint:x}"}}')
    OUTPUT_CSS.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_CSS.write_text("".join(rules) + "\n", encoding="utf-8")
    print(f"Built {len(solid_map)} solid and {len(brand_map)} brand icons.")


if __name__ == "__main__":
    main()

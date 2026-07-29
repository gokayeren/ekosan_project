"""Copy pinned browser assets from node_modules into the application bundle."""
from pathlib import Path
from shutil import copyfile


ROOT = Path(__file__).resolve().parents[1]
SWIPER = ROOT / "node_modules" / "swiper"
OUTPUT = ROOT / "app" / "static" / "vendor"


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for filename in ("swiper-bundle.min.css", "swiper-bundle.min.js"):
        source = SWIPER / filename
        if not source.is_file():
            raise FileNotFoundError(f"Run 'pnpm install' first: {source}")
        copyfile(source, OUTPUT / filename)
    print("Copied pinned Swiper assets.")


if __name__ == "__main__":
    main()

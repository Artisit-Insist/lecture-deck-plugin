#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — slides.md 의 내용을 통째로 박아 '자립형 deck.html'을 만든다.

핵심:
  · deck.html 은 모든 것(슬라이드 디자인·엔진·슬라이드 내용)을 내장한 단일 파일이다.
  · 그래서 서버 없이 '더블클릭'만 하면 바로 열린다. (file:// 제약 없음)
  · 내용을 고치는 곳은 항상 slides.md → build.py 를 돌리면 deck.html 에 반영된다.

만들어지는 것:
  · deck.html         (루트, 더블클릭용 자립형 — 이게 발표 파일)
  · dist/index.html   (동일 내용. 웹 배포·백업용)

사용법:
  python3 build.py
"""
import re, shutil
from pathlib import Path

HERE = Path(__file__).parent
TEMPLATE = HERE / "_deck_template.html"   # 외부 참조(css/js/fetch)를 쓰는 원본 틀
SLIDES   = HERE / "slides.md"
OUT_DECK = HERE / "deck.html"             # 자립형(더블클릭용)
OUT_DIST = HERE / "dist" / "index.html"   # 사본(웹 배포용)

def build(html, md):
    # 1) slides.css 인라인
    css = HERE / "slides.css"
    if css.exists():
        html = html.replace('<link rel="stylesheet" href="slides.css" />',
                             f"<style>\n{css.read_text(encoding='utf-8')}\n</style>", 1)
    # 2) engine.js 인라인
    engine = HERE / "engine.js"
    if engine.exists():
        js = engine.read_text(encoding="utf-8").replace("</script", "<\\/script")
        html = html.replace('<script src="engine.js"></script>', f"<script>\n{js}\n</script>", 1)
    # 3) slides.md 를 내장(더블클릭 시 이 내용으로 바로 렌더)
    md_safe = md.replace("</script", "<\\/script")
    block = f"<!-- FALLBACK_START -->\n{md_safe}\n<!-- FALLBACK_END -->"
    html, n = re.subn(r"<!-- FALLBACK_START -->.*?<!-- FALLBACK_END -->",
                      lambda _: block, html, flags=re.S)
    if n == 0:
        raise SystemExit("템플릿에서 FALLBACK 블록을 찾지 못했습니다.")
    return html

def main():
    if not TEMPLATE.exists():
        raise SystemExit("_deck_template.html 이 없습니다. (deck.html 을 cp 해서 만들어 두세요)")
    if not SLIDES.exists():
        raise SystemExit("slides.md 가 없습니다.")
    md = SLIDES.read_text(encoding="utf-8")
    html = build(TEMPLATE.read_text(encoding="utf-8"), md)

    OUT_DECK.write_text(html, encoding="utf-8")
    OUT_DIST.parent.mkdir(parents=True, exist_ok=True)
    OUT_DIST.write_text(html, encoding="utf-8")

    # 이미지 동봉(있으면 dist 로도 복사)
    assets = HERE / "assets"
    if assets.exists() and any(assets.iterdir()):
        shutil.copytree(assets, OUT_DIST.parent / "assets", dirs_exist_ok=True)

    kb = len(html.encode("utf-8")) // 1024
    n = md.count("\n---\n") + 1
    print(f"✅ deck.html 갱신(자립형) · {n}장 · {kb}KB")
    print(f"   → deck.html 을 '더블클릭'하면 서버 없이 바로 열립니다.")
    print(f"   → 사본: dist/index.html (웹 배포·백업용)")

if __name__ == "__main__":
    main()

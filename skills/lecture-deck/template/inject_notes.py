#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inject_notes.py — 강사노트.md 의 슬라이드별 노트를 slides.md 의 각 슬라이드에 ??? 발표자 노트로 주입.

규칙:
  · 강사노트.md 는 모듈별 `## MODULE N …` 안에 슬라이드별 `### 제목` 노트를 가진다.
  · slides.md 는 `<!-- section -->` 로 모듈이 나뉜다(인트로=모듈0, 노트 없음).
  · 모듈별 슬라이드 수 == 노트 수 이면 '위치(순서) 정렬'(가장 정확).
    다르면 제목 유사도(정규화 부분포함/difflib)로 best-match.
  · 이미 ??? 가 있는 슬라이드는 건너뜀(재실행 안전).

사용: python3 inject_notes.py            (slides.md + 강사노트.md → slides.md 갱신)
      python3 inject_notes.py 노트파일.md
"""
import re, sys, pathlib
from difflib import SequenceMatcher

HERE = pathlib.Path(__file__).parent
SLIDES = HERE / "slides.md"
NOTES  = HERE / (sys.argv[1] if len(sys.argv) > 1 else "강사노트.md")

norm = lambda s: re.sub(r"\s+", " ", s).strip()
sp   = lambda h: re.sub(r"\s*[\(（][^)）]*[\)）]\s*$", "", h).strip()   # 끝 (주석) 제거
key2 = lambda s: re.sub(r"[^0-9A-Za-z가-힣]", "", s)
ratio = lambda a, b: SequenceMatcher(None, a, b).ratio()

def split_slides(md):
    out, buf, fence = [], [], False
    for ln in md.replace("\r", "").split("\n"):
        if ln.startswith("```"): fence = not fence
        if (not fence) and re.match(r"^---+\s*$", ln): out.append("\n".join(buf)); buf = []
        else: buf.append(ln)
    out.append("\n".join(buf)); return out

def heading_of(p):
    m = re.search(r"(?m)^#{1,6}\s+(.+)$", p); return norm(m.group(1)) if m else None

def main():
    if not NOTES.exists(): sys.exit(f"{NOTES.name} 를 찾을 수 없습니다.")
    notes_raw = NOTES.read_text(encoding="utf-8")
    note_mods = []
    for blk in re.split(r"(?m)^## (?:MODULE|SECTION|모듈|파트) ", notes_raw)[1:]:
        items = []
        for e in re.split(r"(?m)^### ", blk)[1:]:
            line, _, body = e.partition("\n")
            items.append((norm(sp(line)), body.strip().replace("```", "").replace("\n---", "\n—")))
        note_mods.append(items)
    if not note_mods: sys.exit("강사노트.md 에서 '## MODULE N' / '### 제목' 구조를 찾지 못했습니다.")

    parts = split_slides(SLIDES.read_text(encoding="utf-8"))
    groups = {}; mod = 0
    for idx, p in enumerate(parts):
        if re.search(r"^\s*<!--[^>]*\bsection\b[^>]*-->", p, re.M): mod += 1
        groups.setdefault(mod, []).append(idx)

    def good(s, n):
        ks, kn = key2(s), key2(n)
        if ks and kn and (ks in kn or kn in ks): return True
        return ratio(s, n) >= 0.62

    assign = {}
    for m, items in enumerate(note_mods, 1):
        sidx = [i for i in groups.get(m, []) if heading_of(parts[i])]
        if len(sidx) == len(items):                       # 위치 정렬
            for k, i in enumerate(sidx): assign[i] = items[k][1]
        else:                                             # 유사도 best-match
            used = set()
            for i in sidx:
                h = heading_of(parts[i]); best, bs = -1, 0
                for j, (t, _) in enumerate(items):
                    if j in used: continue
                    s = 1.0 if good(h, t) else ratio(h, t)
                    if s > bs: bs, best = s, j
                if best >= 0 and bs >= 0.5: assign[i] = items[best][1]; used.add(best)

    new = []
    for i, p in enumerate(parts):
        if i in assign and "\n???" not in p:
            new.append(p.rstrip() + "\n\n???\n" + assign[i] + "\n")
        else:
            new.append(p)
    SLIDES.write_text("\n---\n".join(new), encoding="utf-8")
    total = sum(1 for p in parts if p.strip())
    print(f"✅ 발표자 노트 주입: {len(assign)}개 / 슬라이드 {total}장")
    print("   → 이어서 'python3 build.py' 로 deck.html 갱신하세요.")

if __name__ == "__main__":
    main()

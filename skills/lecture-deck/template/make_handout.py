#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_handout.py — slides.md(슬라이드용)를 '읽기용 줄글 문서'(.md)로 변환한다.
  · 모듈(<!-- section -->) → ## 큰 제목
  · 슬라이드(## 제목)     → ### 소제목 (앞에 kicker 라벨)
  · @src 출처            → '> 출처: …' 인용으로
  · @img 자리            → '> 🖼 이미지: …' 표시로
  · :: 큰숫자, +++ 2단, 지시어 주석 등은 읽기 좋게 정리
사용: python3 make_handout.py   → dist/<제목>_읽기용.md 생성
"""
import re, pathlib

HERE = pathlib.Path(__file__).parent
SRC = HERE / "slides.md"

def split_slides(md):
    out, buf, fence = [], [], False
    for ln in md.replace("\r", "").split("\n"):
        if ln.startswith("```"):
            fence = not fence
        if (not fence) and re.match(r"^---+\s*$", ln):
            out.append("\n".join(buf)); buf = []
        else:
            buf.append(ln)
    out.append("\n".join(buf))
    return [s for s in out if s.strip()]

def parse(raw):
    lines = raw.split("\n")
    # 발표자 노트(??? 이후)는 읽기용 문서에서 제외
    ni = next((i for i, l in enumerate(lines) if l.strip() == "???"), None)
    if ni is not None:
        lines = lines[:ni]
    classes, kicker, heading, subtitle = [], None, None, None
    body, imgs, srcs = [], [], []
    # 지시어(첫 비어있지 않은 줄)
    di = next((i for i, l in enumerate(lines) if l.strip()), None)
    if di is not None:
        m = re.match(r"^\s*<!--\s*(.*?)\s*-->\s*$", lines[di])
        if m:
            for tok in m.group(1).split():
                classes.append(tok.split(":")[0])
            lines.pop(di)
    seen_heading = False
    for l in lines:
        s = l.strip()
        if not s:
            if body and body[-1] != "":
                body.append("")
            continue
        mk = re.match(r"^\^\s+(.+)$", s)
        mh = re.match(r"^(#{1,6})\s+(.+)$", s)
        mi = re.match(r"^@img\s+(.+)$", s)
        ms = re.match(r"^@src\s+(.+)$", s)
        mt = re.match(r"^::\s+(.+)$", s)
        if mk and kicker is None:
            kicker = mk.group(1); continue
        if mi:
            imgs.append(mi.group(1)); continue
        if ms:
            srcs.append(ms.group(1)); continue
        if s == "+++":
            body.append(""); continue
        if mt:
            body.append(f"**{mt.group(1)}**"); body.append(""); continue
        if mh:
            if not seen_heading:
                heading = mh.group(2); seen_heading = True; continue
            else:  # 본문 속 소제목 → 굵게
                body.append(f"**{mh.group(2)}**"); continue
        body.append(l)
    # 본문 정리
    while body and body[0] == "": body.pop(0)
    while body and body[-1] == "": body.pop()
    return dict(classes=classes, kicker=kicker, heading=heading,
                body="\n".join(body).strip(), imgs=imgs, srcs=srcs)

def main():
    md = SRC.read_text(encoding="utf-8")
    slides = [parse(s) for s in split_slides(md)]
    toc, title = [], "강의안"
    cover, content = [], []
    for sl in slides:
        cls = sl["classes"]
        if "title" in cls:
            title = sl["heading"] or title
            cover.append(f"# {title}")
            if sl["kicker"]:
                cover.append(f"\n*{sl['kicker']}*")
            if sl["body"]:
                cover.append("\n" + sl["body"])
            continue
        if "section" in cls:
            label = sl["kicker"] or ""
            head = f"{label} · {sl['heading'] or ''}".strip(" ·")
            toc.append(head)
            content.append(f"\n## {head}")
            if sl["body"]:
                content.append(f"*{sl['body'].splitlines()[0]}*")
            continue
        # 일반 슬라이드
        if sl["kicker"] and sl["heading"]:
            content.append(f"\n### {sl['kicker']} — {sl['heading']}")
        else:
            content.append(f"\n### {sl['heading'] or sl['kicker'] or ''}")
        if sl["body"]:
            content.append(sl["body"])
        for im in sl["imgs"]:
            content.append(f"> 🖼 **이미지 자리** — {im}")
        if sl["srcs"]:
            content.append("> 출처: " + " / ".join(sl["srcs"]))

    toc_md = "## 목차\n\n" + "\n".join(f"{i+1}. {t}" for i, t in enumerate(toc))
    doc = "\n".join(cover) + "\n\n---\n\n" + toc_md + "\n\n" + "\n\n".join(content) + "\n"

    out_path = HERE / "dist" / f"{title}_읽기용.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(doc, encoding="utf-8")
    print(f"✅ 읽기용 문서 생성: {out_path}")
    print(f"   모듈 {len(toc)}개 · 슬라이드 {len(slides)}개 · {len(doc.encode('utf-8'))//1024}KB")

if __name__ == "__main__":
    main()

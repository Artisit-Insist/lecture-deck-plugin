#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import_deck.py — 기존 .pdf / .pptx → slides.md '초안' + 이미지 추출.

기존 강의안을 마크다운 뼈대로 끌어옵니다(페이지/슬라이드 1장 = 슬라이드 1장).
★결과는 '초안'입니다 — Claude에게 "이 초안 다듬어줘"라고 하면 스타일·구조·출처를 정리합니다.

사용:
  (새 강의안 폴더 안에서)
  python3 import_deck.py 원본.pdf
  python3 import_deck.py 원본.pptx
  python3 import_deck.py 원본.pdf  출력폴더

요구: PDF는 poppler(pdftotext/pdfimages) 필요. PPTX는 표준 라이브러리만 사용.
"""
import sys, re, subprocess, zipfile, html, pathlib

HERE = pathlib.Path(__file__).parent

def nonblank(text):
    return [l.strip() for l in text.replace("\r", "").split("\n") if l.strip()]

def to_slide(idx, lines):
    if not lines:
        return f"## (빈 슬라이드 {idx})\n\n@img 원본 {idx}쪽 — 이미지/도식 확인"
    title = re.sub(r"\s{2,}", " ", lines[0])[:60]
    head = f"<!-- title -->\n# {title}" if idx == 1 else f"## {title}"
    bullets = [re.sub(r"\s{2,}", " ", b) for b in lines[1:] if len(b) > 1][:8]
    out = [head]
    if bullets:
        out.append("")
        out += [f"- {b}" for b in bullets]
    return "\n".join(out)

def import_pdf(path, outdir):
    try:
        res = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                             capture_output=True, text=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        sys.exit("PDF 텍스트 추출 실패 — poppler 설치 필요(brew install poppler).")
    pages = res.stdout.split("\f")
    assets = outdir / "assets"; assets.mkdir(parents=True, exist_ok=True)
    n_img = 0
    try:
        subprocess.run(["pdfimages", "-p", "-png", str(path), str(assets / "p")],
                       capture_output=True, check=True)
        n_img = len(list(assets.glob("p-*.png")))
    except Exception:
        pass  # 이미지 추출은 best-effort
    return pages, n_img

def import_pptx(path, outdir):
    assets = outdir / "assets"; assets.mkdir(parents=True, exist_ok=True)
    pages, n_img = [], 0
    with zipfile.ZipFile(path) as z:
        names = sorted([n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)],
                       key=lambda n: int(re.search(r"slide(\d+)", n).group(1)))
        for n in names:
            xml = z.read(n).decode("utf-8", "ignore")
            lines = []
            for para in re.findall(r"<a:p>(.*?)</a:p>", xml, re.S):
                runs = re.findall(r"<a:t>(.*?)</a:t>", para, re.S)
                t = html.unescape(re.sub(r"<[^>]+>", "", "".join(runs))).strip()
                if t:
                    lines.append(t)
            pages.append("\n".join(lines))
        for m in z.namelist():
            if m.startswith("ppt/media/") and pathlib.Path(m).suffix.lower() in (
                    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"):
                (assets / pathlib.Path(m).name).write_bytes(z.read(m)); n_img += 1
    return pages, n_img

def main():
    if len(sys.argv) < 2:
        sys.exit("사용: python3 import_deck.py <파일.pdf|.pptx> [출력폴더]")
    src = pathlib.Path(sys.argv[1]).expanduser()
    if not src.exists():
        sys.exit(f"파일을 찾을 수 없습니다: {src}")
    outdir = pathlib.Path(sys.argv[2]).expanduser() if len(sys.argv) > 2 else HERE
    ext = src.suffix.lower()
    if ext == ".pdf":
        pages, n_img = import_pdf(src, outdir)
    elif ext == ".pptx":
        pages, n_img = import_pptx(src, outdir)
    else:
        sys.exit("지원 형식: .pdf 또는 .pptx")

    while len(pages) > 1 and not pages[-1].strip():  # 끝의 빈 페이지(\f 아티팩트) 제거
        pages.pop()
    slides = [to_slide(i, nonblank(pg)) for i, pg in enumerate(pages, 1)]
    doc = "\n\n---\n\n".join(slides) + "\n"
    out = outdir / "slides.md"
    if out.exists():
        bak = outdir / "slides.import-backup.md"
        out.replace(bak)
        print(f"   (기존 slides.md → {bak.name} 로 백업)")
    out.write_text(doc, encoding="utf-8")
    print(f"✅ 임포트 완료: {out}")
    print(f"   슬라이드 {len(slides)}장 · 이미지 {n_img}개 → assets/")
    print("   ⚠ 이건 '초안'입니다. Claude에게 \"이 import 초안을 강의안으로 다듬어줘\" 라고 하세요.")
    print("     → 제목·불릿 정리, 섹션 구분, @img 배치, 통계 @src 표기까지 손봅니다.")

if __name__ == "__main__":
    main()

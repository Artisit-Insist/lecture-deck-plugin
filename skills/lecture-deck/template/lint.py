#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lint.py — slides.md 자가 점검(강의 전 1분 체크).

검사 항목:
  ✗ 깨진 이미지   : ![](assets/x) 인데 파일이 없음
  ⚠ 출처 누락     : 통계·수치(%/배/억/달러/연도 등)가 있는데 @src 없음
  ⚠ 내용 넘침     : 불릿 과다·긴 줄·총 글자수 과다(한 장에 너무 많음)
  ⚠ 제목 없음     : 본문 슬라이드에 ## 제목이 없음

사용:  python3 lint.py            (slides.md 점검)
       python3 lint.py 다른.md
"""
import re, sys, pathlib

HERE = pathlib.Path(__file__).parent
SLIDES = HERE / (sys.argv[1] if len(sys.argv) > 1 else "slides.md")

# 내용 넘침 임계값(1280×720 기준 경험값)
MAX_BULLETS = 6
MAX_LINE_CHARS = 130
MAX_BODY_CHARS = 480

# '측정된 수치'로 보이는 패턴(단순 순번 3가지/1단계 등은 제외하려 단위를 요구)
STAT_RE = re.compile(
    r"\d[\d,\.]*\s?%"                  # 52% / 12.5%
    r"|\d[\d,\.]*\s?배"                # 30배
    r"|[\d,]+\s?(?:억|만|조)"           # 89억 / 360만
    r"|[\d,]+\s?(?:달러|포인트)"        # 1800억 달러 / 데이터 포인트
    r"|[+\-]\s?\d[\d,\.]*\s?%"         # +74% / -35%
    r"|\b(?:19|20)\d{2}\s?년"          # 1930년 / 2026년 (연도 사실)
)

def split_slides(md):
    out, buf, fence = [], [], False
    for ln in md.replace("\r", "").split("\n"):
        if ln.startswith("```"): fence = not fence
        if (not fence) and re.match(r"^---+\s*$", ln): out.append("\n".join(buf)); buf = []
        else: buf.append(ln)
    out.append("\n".join(buf))
    return [s for s in out if s.strip()]

def strip_meta(raw):
    """디렉티브·발표자노트(???) 제거한 본문만"""
    lines = raw.split("\n")
    ni = next((i for i, l in enumerate(lines) if l.strip() == "???"), None)
    if ni is not None: lines = lines[:ni]
    lines = [l for l in lines if not re.match(r"^\s*<!--.*-->\s*$", l)]
    return "\n".join(lines).strip()

def heading(raw):
    m = re.search(r"(?m)^#{1,6}\s+(.+)$", raw)
    return m.group(1).strip() if m else None

def main():
    if not SLIDES.exists(): sys.exit(f"{SLIDES.name} 가 없습니다.")
    md = SLIDES.read_text(encoding="utf-8")
    slides = split_slides(md)
    assets_ok = True
    errors = warns = 0
    report = []

    for i, raw in enumerate(slides, 1):
        body = strip_meta(raw)
        h = heading(raw)
        label = f"#{i:>2} { (h or '(제목 없음)')[:34] }"
        issues = []

        # ✗ 깨진 이미지(로컬 경로만)
        for alt, path in re.findall(r"!\[([^\]]*)\]\(([^)\s]+)", raw):
            if path.startswith(("http", "data:")): continue
            if not (HERE / path).exists():
                issues.append(("✗", f"이미지 없음: {path}")); errors += 1

        # ⚠ 출처 누락(통계 있는데 @src 없음). @img/코드/표지·섹션 제외
        classes = re.findall(r"<!--\s*(.*?)\s*-->", raw)
        is_cover = any(("title" in c or "section" in c) for c in classes)
        has_src = bool(re.search(r"(?m)^@src\s", raw))
        # 코드펜스 안 숫자는 제외
        body_nocode = re.sub(r"```.*?```", "", body, flags=re.S)
        nums = [m.strip() for m in STAT_RE.findall(body_nocode)]
        if nums and not has_src and not is_cover:
            sample = ", ".join(list(dict.fromkeys(nums))[:3])
            issues.append(("⚠", f"통계({sample}) 있는데 @src 없음")); warns += 1

        # ⚠ 내용 넘침 (본문 기준 — 발표자노트 제외)
        bullets = len(re.findall(r"(?m)^\s*[-*]\s+", body))
        if bullets > MAX_BULLETS:
            issues.append(("⚠", f"불릿 {bullets}개(>{MAX_BULLETS}) — 분할 권장")); warns += 1
        long_lines = [l for l in body.split("\n") if len(l) > MAX_LINE_CHARS and not l.startswith("|")]
        if long_lines:
            issues.append(("⚠", f"긴 줄 {len(long_lines)}개(>{MAX_LINE_CHARS}자)")); warns += 1
        plain = re.sub(r"[#*`>\-\^@:|]", "", body)
        if len(plain) > MAX_BODY_CHARS:
            issues.append(("⚠", f"본문 {len(plain)}자(>{MAX_BODY_CHARS}) — 내용 많음")); warns += 1

        # ⚠ 제목 없음(인용/이미지 전용이 아니면)
        if not h and not re.search(r"!\[|^>", body, re.M):
            issues.append(("⚠", "## 제목 없음")); warns += 1

        if issues:
            report.append((label, issues))

    # 출력
    print(f"\n📋 lint — {SLIDES.name} · 슬라이드 {len(slides)}장\n" + "─"*52)
    if not report:
        print("✅ 문제 없음. 깔끔합니다!")
    else:
        for label, issues in report:
            print(label)
            for mark, msg in issues:
                print(f"     {mark} {msg}")
    print("─"*52)
    print(f"결과: ✗ 오류 {errors} · ⚠ 경고 {warns} · 정상 {len(slides)-len(report)}/{len(slides)}장")
    if errors: print("→ ✗(깨진 이미지)는 고쳐야 발표 시 깨집니다.")
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()

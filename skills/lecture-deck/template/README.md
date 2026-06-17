# HTML 강의 플러그인

PPTX 대신 **마크다운 한 파일**로 강의안을 만들고, 화면 발표·인쇄 배포본·웹 배포를 한 번에.
의존성 0 · 빌드 도구 0 · 더블클릭으로 열림.

> 디자인: obsidianmrchoi 데크와 같은 **다크 'Obsidian' 스타일** — 차콜 배경 + 흰색 위계 + 블루 강조, Pretendard·JetBrains Mono, 청록 글로우 라벨(`^ 라벨`). 색은 3색 원칙(배경·글자·강조).

## 발표 — `deck.html` 더블클릭

**`deck.html` 을 더블클릭하면 끝.** 서버도 인터넷도 필요 없습니다 — 모든 내용이 파일 안에 들어 있는 자립형입니다.
- **넘기기**: 마우스 클릭=다음 · 우클릭=이전 · 프레젠터 리모컨(PageUp/Down) · 키보드 `←` `→`
- 기타: **`E` 즉석 편집**(현재 슬라이드 수정·삭제) · `F` 전체화면 · `S` 발표자 노트 · `O` 한눈에 보기 · `P` 인쇄(PDF)

## 내용 고치기 (Claude Code로)

내용은 **`slides.md`** 한 파일에 있습니다. Claude에게 "○○ 고쳐줘"라고 하면 `slides.md`를 수정하고 **`python3 build.py`로 `deck.html`을 자동 갱신**합니다. 그다음 `deck.html`을 다시 열면 반영돼 있습니다.

> 직접 손볼 일이 있으면 `editor.html`(에디터)도 있지만 필수는 아닙니다. (에디터는 미리보기 서버 필요: `python3 -m http.server 8000` → `localhost:8000/editor.html`)

## 파일 안내

| 파일 | 역할 |
|---|---|
| **`deck.html`** | ⭐ **발표 파일.** 더블클릭하면 바로 열림(자립형, 모든 내용 내장). |
| **`slides.md`** | 강의 내용 원본. 여기를 고치고 `build.py`로 `deck.html`에 반영. |
| `build.py` | `python3 build.py` → `slides.md`를 `deck.html`(+`dist/index.html`)에 굽기. |
| `slides.css` · `engine.js` · `_deck_template.html` | 빌드 재료(디자인·파서·틀). |
| `editor.html` | (선택) 브라우저 편집기. |
| `assets/` | 사진·이미지 모음. |
| `make_handout.py` | 읽기용/강사노트 문서 생성. |
| **`PROCESS.md`** | 📖 제작 프로세스 전체 가이드. |

## 발표 조작

- **넘기기**: 화면 클릭=다음 · 우클릭=이전 · 리모컨(PageUp/Down) · `←` `→`
- `E` 즉석 편집 · `F` 전체화면 · `O` 한눈에 보기 · `S` 발표자 노트 · `P` 인쇄(PDF) · `.` 깜깜이 · `?` 도움말
- 슬라이드 안 링크는 클릭해도 넘어가지 않고 링크가 열립니다.

## 배포

- **인쇄본 PDF**: 브라우저에서 `P` → PDF로 저장(가로/A4, 배경 그래픽 켜기)
- **단일 파일**: `python3 build.py` → `dist/index.html`
- **웹**: 폴더를 Netlify/Vercel에 드래그&드롭

자세한 내용은 [PROCESS.md](PROCESS.md).

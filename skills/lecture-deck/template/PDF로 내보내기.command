#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  강의안을 PDF로 내보내기 — 이 파일을 '더블클릭' 하세요.
#  결과: dist/강의안.pdf  (16:9 슬라이드, 한 장당 한 페이지)
#  ※ 이미지를 넣으셨다면 assets/ 폴더의 사진까지 그대로 들어갑니다.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cd "$(dirname "$0")"
PORT=8801
OUT="dist/강의안.pdf"
mkdir -p dist

# Chrome 계열 브라우저 찾기
CHROME=""
for p in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
         "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" \
         "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" \
         "/Applications/Chromium.app/Contents/MacOS/Chromium"; do
  [ -x "$p" ] && CHROME="$p" && break
done

if [ -z "$CHROME" ]; then
  echo "  ⚠ Chrome/Edge/Brave 가 없어 자동 변환을 못 합니다."
  echo "  → 브라우저에서 deck.html 을 열고 P(인쇄) → 'PDF로 저장'"
  echo "     용지: 가로 / 배경 그래픽 켜기."
  read -n1 -p "  엔터를 누르면 닫힙니다..."
  exit 1
fi

# 임시 서버 → PDF 출력 → 서버 종료
python3 -m http.server $PORT >/dev/null 2>&1 &
SRV=$!
sleep 1
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
  --virtual-time-budget=20000 --run-all-compositor-stages-before-draw \
  --print-to-pdf="$OUT" "http://localhost:$PORT/deck.html" 2>/dev/null
RESULT=$?
kill $SRV 2>/dev/null

if [ $RESULT -eq 0 ]; then
  echo "  ✅ 완료: $OUT"
  open "$OUT"
else
  echo "  ⚠ 변환 실패 — 브라우저에서 deck.html → P(인쇄)로 저장해 주세요."
fi
echo ""
read -n1 -p "  엔터를 누르면 이 창이 닫힙니다..."

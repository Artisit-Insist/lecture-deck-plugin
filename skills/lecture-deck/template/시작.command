#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  강의안 에디터 시작 — 이 파일을 '더블클릭' 하세요.
#  (터미널 창이 하나 뜨고, 브라우저에 에디터가 열립니다.
#   강의 작업이 끝나면 그 터미널 창을 닫으면 됩니다.)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cd "$(dirname "$0")"
PORT=8000
# 이미 켜져 있으면 그 포트 재사용, 아니면 새로 켬
if ! curl -s "http://localhost:$PORT/editor.html" >/dev/null 2>&1; then
  python3 -m http.server $PORT >/dev/null 2>&1 &
  sleep 1
fi
open "http://localhost:$PORT/editor.html"
echo ""
echo "  ✅ 브라우저에 '강의안 에디터'가 열렸습니다."
echo "  ─ 편집이 끝나면 이 창을 닫으세요."
echo ""
echo "  · 발표만 보려면: http://localhost:$PORT/deck.html"
echo ""
# 서버를 살려두기 위해 창을 유지
wait

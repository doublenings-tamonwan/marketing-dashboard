#!/usr/bin/env bash
# แสงฟุ้ง (soft glow / bloom) + โทนอุ่นนิด ๆ สำหรับคลิปแนวตั้ง
# ใช้: bash office/editor/glow.sh in.mp4 out.mp4 [ความแรง 0.0-1.0, ค่าเริ่มต้น 0.35]
# ใส่ก่อน sparkles.py และ burn_subs.py
# หมายเหตุ: ต้อง format=gbrp ก่อน blend ไม่งั้นโหมด screen ไปผสมช่องสี U/V ภาพจะติดม่วง
set -euo pipefail
IN="$1"; OUT="$2"; S="${3:-0.35}"
ffmpeg -nostdin -v error -y -i "$IN" -filter_complex \
"[0:v]format=gbrp,split[a][b];[b]curves=all='0/0 0.55/0.25 1/1',gblur=sigma=28[g];\
[a][g]blend=all_mode=screen:all_opacity=${S},\
colorbalance=rs=0.03:gs=0.0:bs=-0.03:rm=0.02:bm=-0.02,eq=saturation=1.04,format=yuv420p[v]" \
-map "[v]" -map 0:a? -c:v libx264 -preset medium -crf 18 -c:a copy -movflags +faststart "$OUT"

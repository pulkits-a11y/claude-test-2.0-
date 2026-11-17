#!/usr/bin/env bash
# Snapshots of the v05 demo at exact frames (HyperFrames 0.9.52), renamed f<frame>_<what>.png into review/snap,
# plus labelled contact sheets (review/sheet_*.jpg). Run from _demo-v05.
set -euo pipefail
FRAMES=(
  0:A_flash-f0 1:A_after-flash 7:A_Why-pop-f0 8:A_Why-pop-f1 9:A_Why-pop-f2 11:A_Why-pop-f4 15:A_does-appears 26:A_every-appears 40:A_GTA-appears 54:A_end
  62:B_Because 85:B_1995-f0 86:B_flick-f1 87:B_flick-f2 88:B_flick-f3 89:B_flick-f4 90:B_flick-f5 92:B_flick-f7 95:B_flick-f10 100:B_steady
  130:C_broke_errPop 133:C_pop-landed 136:C_cascade-1 140:C_cascade-3 146:C_cascade-6 155:C_cascade-all 160:C_And 176:C_bug 178:C_bug-split-f2 182:C_bug-f6 190:C_bug-jitter 196:C_snap-f0 199:C_snap-f3 202:C_snap-f6 205:C_flash 212:C_pill-f0 215:C_pill-f3 218:C_pill-landed 230:C_pill-hold 242:C_pillOut-f0 244:C_pillOut-f2 246:C_pillOut-f4 249:C_gone
  255:D_page 258:D_hl-f0 262:D_hl-f4 266:D_hl-done 270:D_circle-f0 274:D_circle-f4 279:D_circle-done 325:D_push-end
  335:E_card 338:E_arrow-f0 342:E_arrow-f4 347:E_arrow-done 379:E_card-end 382:E_dark-Until 395:E_finally 410:E_dark-hold
  424:F_name-f0 427:F_name-f3 430:F_name-landed_awful-pop-f0 431:F_awful-f1 432:F_awful-f2 434:F_awful-f4 447:F_too-pop 453:F_simy-pop 470:F_quote
  500:G_its 508:G_dull 519:G_from 530:G_cops-pop-f0 531:G_cops-f1 532:G_cops-f2 534:G_cops-f4 545:G_settled
  569:H_pre 570:H_slam-f0 572:H_slam-f2 574:H_impact 576:H_landed 578:H_shake 608:H_zoom-f0 612:H_zoom-f4 615:H_zoom-f7 616:H_cut 619:H_land-f3 622:H_landed
  654:I_slot-f0 657:I_slot-f3 660:I_slot-f6 664:I_slot-f10 668:I_slot-landed 690:I_hold
  705:J_cal 706:J_tear-f0 708:J_tear-f2 711:J_tear-f5 714:J_tear-f8 718:J_tear-done 730:J_glow-steady 743:J_pre 744:J_loc-f0 748:J_loc-f4 752:J_loc-f8 756:J_loc-landed 770:J_hold
  788:K_pre 789:K_glitch-f0 790:K_f1 791:K_f2 792:K_f3-cut 793:K_f4 794:K_f5 795:K_f6 796:K_after 800:K_next
  825:Z_ca-calibration
)
OUT=review/snap
mkdir -p "$OUT"
AT=""
for fw in "${FRAMES[@]}"; do f=${fw%%:*}; AT="$AT,$(python3 -c "print(f'{$f/30+0.00002:.5f}')")"; done
[ "${1:-}" = "--rename-only" ] || npx --yes hyperframes@0.9.52 snapshot . --at "${AT:1}" --no-end --keep -o "$OUT" --timeout 180000 > review/snap.log 2>&1
for fw in "${FRAMES[@]}"; do
  f=${fw%%:*}; w=${fw#*:}
  t=$(python3 -c "print(f'{$f/30+0.00002:.3f}'.rstrip('0').rstrip('.'))")
  src=$(ls "$OUT"/at-"$t"s.png 2>/dev/null || true)
  if [ -z "$src" ]; then echo "missing snapshot for f$f ($t s)"; continue; fi
  mv "$src" "$OUT/$(printf 'f%04d' "$f")_${w}.png"
done
python3 tools/sheets.py "$OUT"

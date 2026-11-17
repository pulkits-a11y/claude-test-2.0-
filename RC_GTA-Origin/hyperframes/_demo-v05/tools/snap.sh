#!/usr/bin/env bash
# Snapshots of the v05 demo at exact frames (HyperFrames 0.9.52), renamed f<frame>_<what>.png into review/snap,
# plus labelled contact sheets (review/sheet_*.jpg). Run from _demo-v05.
set -euo pipefail
FRAMES=(
  6:A_pre 7:A_Why-f0 8:A_Why-f1 9:A_Why-f2 11:A_Why-f4 13:A_Why-f6 15:A_does-f0 16:A_does-f1 18:A_does-f3 26:A_every-f0 27:A_every-f1 40:A_GTA-f0 41:A_GTA-f1 43:A_GTA-f3 44:A_GTA-f4 46:A_GTA-f6 48:A_GTA-f8 54:A_drift-end
  62:B_Because-f0 63:B_f1 65:B_f3 85:B_1995-f0 86:B_1995-f1 87:B_1995-f2 88:B_1995-f3 89:B_1995-f4 90:B_1995-f5 92:B_1995-f7 95:B_1995-f10 100:B_steady 125:B_end
  130:C_broke-f0_errPop 131:C_f1 133:C_pop-landed 136:C_cascade-1 140:C_cascade-3 146:C_cascade-6 155:C_cascade-all 160:C_And 176:C_bug-f0 178:C_bug-f2 182:C_bug-f6 190:C_bug-jitter 196:C_snap-f0 199:C_snap-f3 202:C_snap-f6 205:C_flash 206:C_after-flash 212:C_pill-f0 215:C_pill-f3 218:C_pill-wiped 222:C_pill-typing 230:C_pill-typed 242:C_pillOut-f0 244:C_pillOut-f2 246:C_pillOut-f4 249:C_gone
  255:D_page 258:D_hl-f0 262:D_hl-f4 266:D_hl-done 270:D_circle-f0 274:D_circle-f4 279:D_circle-done 290:D_stamp-f0 291:D_stamp-f1 293:D_stamp-impact 294:D_f4 295:D_stamp-landed 300:D_shake-done 325:D_push-end
  335:E_card 338:E_arrow-f0 342:E_arrow-f4 347:E_arrow-done 360:E_card-push 379:E_card-end 382:E_dark-Until 384:E_Until-f2 395:E_finally 410:E_dark-hold
  424:F_name-f0 427:F_name-f3 430:F_awful-f0_typing 440:F_typing 450:F_name-typed 455:F_simy 470:F_quote 495:F_end
  500:G_its 508:G_dull-f0 512:G_dull 519:G_from 530:G_cops-f0 531:G_cops-f1 532:G_cops-f2 533:G_cops-f3 534:G_cops-f4 536:G_cops-f6 538:G_cops-f8 545:G_settled
  569:H_pre 570:H_slam-f0 572:H_slam-f2 574:H_impact 575:H_f5 576:H_landed 578:H_shake 590:H_hold 608:H_whip-f0 612:H_whip-f4 615:H_whip-f7 616:H_cut 619:H_land-f3 622:H_landed 640:H_next
  657:I_pre 658:I_flip-f0 661:I_flip-f3 663:I_flip-f5 665:I_flip-f7 668:I_flip-done 680:I_back 694:I_slot-f0 697:I_slot-f3 700:I_slot-f6 704:I_slot-f10 708:I_slot-landed 720:I_hold
  735:J_cal 736:J_tear-f0 738:J_tear-f2 741:J_tear-f5 744:J_tear-f8 748:J_tear-done 760:J_glow-steady 773:J_pre 774:J_loc-f0 778:J_loc-f4 782:J_loc-f8 786:J_loc-landed 800:J_hold
  818:K_pre 819:K_glitch-f0 820:K_f1 821:K_f2 822:K_f3-cut 823:K_f4 824:K_f5 825:K_f6 826:K_after 830:K_next
  855:Z_ca-calibration
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

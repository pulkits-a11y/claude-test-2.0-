#!/usr/bin/env bash
# Snapshots of the v03 demo at exact frames (HyperFrames 0.9.52), renamed f<frame>_<what>.png into review/snap,
# plus labelled contact sheets (review/sheet_*.jpg). Run from _demo-v03.
set -euo pipefail
FRAMES=(
  6:A_solo-Dont-onset 18:A_solo-me-onset 31:A_lockup2-Open-onset_hardcut 39:A_GTA-onset_pop-f0 40:A_GTA-pop-f1 41:A_GTA-pop-f2
  45:A_Online-onset_pop-f0 51:A_Online-settled 57:A_and-onset 63:A_buy-onset 69:A_an-onset 75:A_arcade-onset_full 99:A_lockup2-last-frame
  100:A_lockup3-One_hardcut 113:A_machines-onset 130:A_called_full 145:A_Race-pop-f0 147:A_Race-pop-f2 153:A_Chase-onset 165:A_title-settled
  175:B_T3-Its 182:B_T3-1995-roll 200:B_T3-landed 228:B_T3-push
  245:C_planned 262:C_take 267:C_18-onset 274:C_months-full 310:C_cal-filled
  333:D_calIn-f0 345:D_calIn-landed 380:D_turn 395:D_thirty-pop-f0 397:D_thirty-pop-f2 401:D_settled 420:D_counter-30
  430:E_card 440:E_awful-pop-f0 442:E_awful-pop-f2 457:E_too 463:E_simy 470:E_simy-settled 495:E_name
  528:F_star1-glitch-f0 529:F_star1-f1 530:F_star1-f2 531:F_star2-f0 533:F_wanted-pop-f0 536:F_stars-mid 540:F_stars-mid2 545:F_stars-word-pop 552:F_last-star-glitch 560:F_all-clean
  605:G_Until 614:G_finally 630:G_card-hold 645:G_Grand-pop-f0 647:G_Grand-pop-f2 651:G_Theft-pop-f0 661:G_Auto-pop-f0 675:G_title-settled
  705:H_doc 711:H_hl-mid 720:H_hl-done_errbox 750:H_hold
  762:I_ink-tiles 766:I_centre-tile-1-cleared 775:I_both-cleared 795:I_hold
)
OUT=review/snap
mkdir -p "$OUT"
AT=""
for fw in "${FRAMES[@]}"; do f=${fw%%:*}; AT="$AT,$(python3 -c "print(f'{$f/30+0.00002:.5f}')")"; done
[ "${1:-}" = "--rename-only" ] || npx --yes hyperframes@0.9.52 snapshot . --at "${AT:1}" --no-end --keep -o "$OUT" --timeout 120000 > review/snap.log 2>&1
for fw in "${FRAMES[@]}"; do
  f=${fw%%:*}; w=${fw#*:}
  t=$(python3 -c "print(f'{$f/30+0.00002:.3f}'.rstrip('0').rstrip('.'))")
  src=$(ls "$OUT"/at-"$t"s.png 2>/dev/null || true)
  if [ -z "$src" ]; then echo "missing snapshot for f$f ($t s)"; continue; fi
  mv "$src" "$OUT/$(printf 'f%04d' "$f")_${w}.png"
done
python3 tools/sheets.py "$OUT"

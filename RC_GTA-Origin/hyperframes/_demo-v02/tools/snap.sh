#!/usr/bin/env bash
# Snapshots of the v02 demo at exact frames (HyperFrames 0.9.52 render path), renamed f<frame>_<what>.png into review/,
# plus labelled contact sheets (review/sheet_*.jpg). Run from _demo-v02.
set -euo pipefail
FRAMES=(
  7:A_Why-onset 8:A_Why+1 15:A_does-onset 20:A_Why-does-landed 26:A_every-onset 40:A_GTA-onset_cut_punch115 42:A_punch-f+2 50:A_punch-landed
  69:A_GTA-onset 80:A_6-onset 93:A_have-onset 98:A_you-onset 105:A_running 114:A_T2-from 120:A_T2-the 125:A_T2-cops-onset_keyPunch
  126:A_cops+1 128:A_cops+3 131:A_cops-settled 147:A_T2-exit-f2of3
  181:B_a-onset 183:B_police-onset 192:B_officer-onset 203:B_chasing
  286:C_rest-B-6 289:C_out-B-3 290:C_out-B-2 291:C_out-peak-B-1 292:C_cut-in-130 293:C_in+1 295:C_in+3 301:C_in-landed 308:C_T3-digits-landed
  369:D1_planned 380:D1_to 386:D1_take 391:D1_18-onset 398:D1_months 410:D1_settled
  428:D2_calIn-f0 430:D2_calIn-f2 434:D2_calIn-f6 440:D2_calIn-landed 481:D2_turn 492:D2_into 496:D2_thirty-counter-lands 505:D2_settled
  531:E1_Dundee 546:E1_Scotland 560:E1_both
  587:E2_The 592:E2_wanted 604:E2_stars 622:E2_The2 628:E2_sirens_keyPunch 653:E2_running
  692:F_The 696:F_whole 705:F_series 715:F_started 728:F_with 735:F_a 736:F_bug 745:F_settled
  770:G_type-f0 774:G_type-f4 781:G_type-f11 790:G_type-f20 796:G_type-done 830:G_hold
  868:H_quote-f0 871:H_quote-f3 876:H_quote-done 888:H_name 940:H_hold
  962:I_glitch-f0 965:I_glitch-f3 968:I_clean 993:I_label-pop 1000:I_label
  1038:J_flash-C-2 1039:J_flash-C-1 1040:J_flash-C 1042:J_flash-C+2 1061:J_blinds-B-4 1063:J_blinds-B-2 1065:J_blinds-shut 1067:J_blinds-B+2
)
OUT=review/snap
mkdir -p "$OUT"   # re-runs overwrite the same names
AT=""
for fw in "${FRAMES[@]}"; do f=${fw%%:*}; AT="$AT,$(python3 -c "print(f'{$f/30+0.00002:.5f}')")"; done
[ "${1:-}" = "--rename-only" ] || npx --yes hyperframes@0.9.52 snapshot . --at "${AT:1}" --no-end --keep -o "$OUT" --timeout 120000 > /dev/null
for fw in "${FRAMES[@]}"; do
  f=${fw%%:*}; w=${fw#*:}
  t=$(python3 -c "print(f'{$f/30+0.00002:.3f}'.rstrip('0').rstrip('.'))")   # the CLI names stills with 3 decimals
  src=$(ls "$OUT"/at-"$t"s.png 2>/dev/null || true)
  if [ -z "$src" ]; then echo "missing snapshot for f$f ($t s)"; continue; fi
  mv "$src" "$OUT/$(printf 'f%04d' "$f")_${w}.png"
done
python3 tools/sheets.py "$OUT"

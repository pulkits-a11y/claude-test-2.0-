#!/usr/bin/env bash
# Download every B-roll clip listed in the Master Edit Plan ("B-roll sources by beat").
# Run on your own Mac/PC (YouTube blocks downloads from the cloud container).
# Needs: yt-dlp (brew install yt-dlp) and ffmpeg (brew install ffmpeg).
# Usage, from the RC_GTA-Origin folder:   bash 04_Broll/download_broll.sh            (primary clips only)
#                                         bash 04_Broll/download_broll.sh --all      (also alternates/optional)
# Files land in 04_Broll/Bxx/ named "<R-ID>__<title> [<youtube id>].mp4" (the R-ID prefix is what the build reads).
# Highest resolution up to 1080p, preferring 60 fps (the plan: "1080p or above, 60 fps where offered").
set -u
cd "$(dirname "$0")/.." || exit 1
ALL=0; [ "${1:-}" = "--all" ] && ALL=1
dl() { # rid folder url role
  local rid="$1" dir="$2" url="$3" role="$4"
  if [ "$role" != "primary" ] && [ $ALL -eq 0 ]; then return; fi
  mkdir -p "$dir"
  if ls "$dir/${rid}__"* >/dev/null 2>&1; then echo "skip $rid (already downloaded)"; return; fi
  echo "== $rid ($role) $url"
  yt-dlp -S "res:1080,fps" -f "bv*+ba/b" --merge-output-format mp4 --no-playlist \
    -o "$dir/${rid}__%(title).70s [%(id)s].%(ext)s" "$url" || echo "!! FAILED $rid $url" | tee -a 04_Broll/download_failures.txt
}
dl "R1.1" "04_Broll/B01" "https://www.youtube.com/watch?v=X5NSyXi21sQ" "alternate"   # GTA 6 police chase (unofficial, likely cut from trailers; avoid for th
dl "R1.2" "04_Broll/B01" "https://www.youtube.com/watch?v=8L0CzL2V72c" "primary"   # GTA 6 features trailer (official, PlayStation)
dl "R1.3" "04_Broll/B01" "https://www.youtube.com/watch?v=NcTdBgA3Bkg" "primary"   # GTA 5 five-star police chase
dl "R1.4" "04_Broll/B01" "https://www.youtube.com/watch?v=4-iEGt3pFT0" "alternate"   # Evolution of police chases in GTA
dl "R1.5" "04_Broll/B01" "https://www.youtube.com/watch?v=nTL0QWjllf8" "primary"   # Wanted levels, GTA 1 to GTA 6
dl "R1.6" "04_Broll/B01" "https://www.youtube.com/watch?v=flgIZbQHwN8" "primary"   # San Andreas police chase
dl "R1.7" "04_Broll/B01" "https://www.youtube.com/watch?v=s2KJsYEngS8" "primary"   # Vice City police chase
dl "R2.1" "04_Broll/B02" "https://www.youtube.com/watch?v=eoCl4i35dQ8" "alternate"   # "Race 'N' Chase: the glitch that started GTA"
dl "R2.2" "04_Broll/B02" "https://www.youtube.com/watch?v=STS61t1Pz3I" "alternate"   # "How a glitch created GTA"
dl "R2.3" "04_Broll/B02" "https://www.youtube.com/watch?v=7Xk4AP3eEws" "optional"   # Glitch overlay, green screen
dl "R2.4" "04_Broll/B02" "https://www.youtube.com/watch?v=NRY-9Eel2n0" "reference"   # Windows 95 error (reference for the error box)
dl "R3.1" "04_Broll/B03" "https://www.youtube.com/watch?v=n7QORDefzIE" "primary"   # Old Dundee in colour
dl "R3.2" "04_Broll/B03" "https://www.youtube.com/watch?v=dK3etIXpUQE" "alternate"   # Dundee station, 1990
dl "R3.3" "04_Broll/B03" "https://www.youtube.com/watch?v=Ev7FqNa5rD0" "primary"   # /noclip documentary on DMA Design
dl "R3.4" "04_Broll/B03" "https://www.youtube.com/watch?v=7IF_dh0Mcio" "alternate"   # Nostalgia Nerd, "From DMA to GTA"
dl "R3.5" "04_Broll/B03" "https://www.youtube.com/watch?v=JJ9CS0KUZvY" "primary"   # Lemmings PC gameplay
dl "R3.6" "04_Broll/B03" "https://www.youtube.com/watch?v=xSKod9Xmrgo" "alternate"   # Lemmings Amiga intro
dl "R3.7" "04_Broll/B03" "https://www.youtube.com/watch?v=7vWSi44ZTSw" "primary"   # BBC Archive, GTA making-of from 1996 (real footage of the team; the st
dl "R3.8" "04_Broll/B03" "https://www.youtube.com/watch?v=f14k2j9V33Q" "primary"   # DMA Design office tour, uploaded by Mike Dailly
dl "R3.9" "04_Broll/B02" "https://www.youtube.com/watch?v=u3TFcEyRyYc" "primary"   # 1990s PC with a CRT monitor (the CRT plate for B2)
dl "R4.1" "04_Broll/B04" "https://www.youtube.com/watch?v=w15vYQIuvSE" "optional"   # Race'n'Chase prototype gameplay (from 2:30)
dl "R4.2" "04_Broll/B04" "https://www.youtube.com/watch?v=o_aIF5RyoO4" "alternate"   # History of GTA from Race'n'Chase
dl "R4.3" "04_Broll/B04" "https://www.youtube.com/watch?v=XsF4GnPQrvo" "alternate"   # "GTA Prototype 1 – How it works", uploaded by Mike Dailly
dl "R4.4" "04_Broll/B04" "https://www.youtube.com/watch?v=80yeR0W7G6E" "alternate"   # Calendar flipping
dl "R5.1" "04_Broll/B05" "https://www.youtube.com/watch?v=wy95d3TrAIQ" "primary"   # San Andreas vigilante missions
dl "R5.2" "04_Broll/B05" "https://www.youtube.com/watch?v=5TAB4i9P1eI" "alternate"   # GTA 5 playing as a police officer, 4K
dl "R5.3" "04_Broll/B05" "https://www.youtube.com/watch?v=b-yTeXuc77M" "alternate"   # LCPDFR police mod, GTA 4
dl "R5.4" "04_Broll/B05" "https://www.youtube.com/watch?v=PV1NfLjkbWg" "primary"   # LSPDFR police patrol, GTA 5
dl "R6.1" "04_Broll/B06" "https://www.youtube.com/watch?v=QAi3KZxBPI8" "primary"   # Gary Penn, BAFTA Games Mini Masterclass (his face for the cut-out)
dl "R6.2" "04_Broll/B06" "https://www.youtube.com/watch?v=o8wl1q9UUd4" "primary"   # Gary Penn on The Retro Hour
dl "R6.3" "04_Broll/B06" "https://www.youtube.com/watch?v=V2Y8JCATGWE" "alternate"   # "GTA: the game that was almost cancelled"
dl "R6.4" "04_Broll/B06" "https://www.youtube.com/watch?v=Fh4TPvNjUjM" "alternate"   # Person gaming at a PC (stock)
dl "R6.5" "04_Broll/B06" "https://www.youtube.com/watch?v=uzzaL0WcpHw" "optional"   # 65 Windows 95 games in 3 minutes
dl "R7.1" "04_Broll/B07" "https://www.youtube.com/watch?v=HtJSL-bGo_Y" "primary"   # Early-1990s office workers (archival)
dl "R7.2" "04_Broll/B07" "https://www.youtube.com/watch?v=4hFa7Rz9rPE" "optional"   # CANCELLED stamp, green screen
dl "R7.3" "04_Broll/B07" "https://www.youtube.com/watch?v=iSoYy4Go_sg" "primary"   # DMA Design office tour, 1990
dl "R9.1" "04_Broll/B02" "https://www.youtube.com/watch?v=HX8infRFBTc" "primary"   # GTA 1 police chase
dl "R9.2" "04_Broll/B09" "https://www.youtube.com/watch?v=ezl7oXtmIPs" "primary"   # GTA 1 full game (scrub to the chases)
dl "R9.3" "04_Broll/B09" "https://www.youtube.com/watch?v=LNqEGdO9HDI" "primary"   # GTA 2 five-star gameplay
dl "R9.4" "04_Broll/B09" "https://www.youtube.com/watch?v=AvVqj-YCHi8" "alternate"   # GTA 1 in 4K
dl "R9.5" "04_Broll/B09" "https://www.youtube.com/watch?v=3f0Zmrg9NUk" "primary"   # GTA London 1969 rampage
dl "R10.1" "04_Broll/B10" "https://www.youtube.com/watch?v=-3NOxHFcNaM" "primary"   # GTA 1 kill frenzy
dl "R10.2" "04_Broll/B10" "https://www.youtube.com/watch?v=NlU1nY7iQWM" "primary"   # GTA 1 Liberty City gameplay
dl "R11.1" "04_Broll/B11" "https://www.youtube.com/watch?v=pvSspZWkEXU" "alternate"   # GTA 1 menu and character select, 4K
dl "R12.1" "04_Broll/B12" "https://www.youtube.com/watch?v=6vsvcHxkRZk" "optional"   # Clock time-lapse
dl "R12.2" "04_Broll/B12" "https://www.youtube.com/watch?v=1pERRhV5AAA" "alternate"   # Calendar spinning
dl "R13.1" "04_Broll/B13" "https://www.youtube.com/watch?v=m2CHL4ACCEs" "primary"   # GTA 1 intro, 1997
dl "R13.2" "04_Broll/B13" "https://www.youtube.com/watch?v=BcnDNeEggls" "primary"   # GTA 1 PC big-box unboxing
dl "R13.3" "04_Broll/B13" "https://www.youtube.com/watch?v=MdlhjRlNyA8" "alternate"   # GTA 1 trailer
dl "R13.4" "04_Broll/B13" "https://www.youtube.com/watch?v=E5ygyxyuDHs" "alternate"   # GTA 1 commercial
dl "R13.5" "04_Broll/B13" "https://www.youtube.com/watch?v=EhxJPrDlrtI" "alternate"   # CBS "Eye to Eye: Grand Theft Auto"
dl "R13.6" "04_Broll/B13" "https://www.youtube.com/watch?v=wH5FwaRz6hE" "alternate"   # BBC's first GTA feature, 1996
dl "R14.1" "04_Broll/B01" "https://www.youtube.com/watch?v=6lSy09Uruz0" "primary"   # GTA 3 six-star chase
dl "R14.2" "04_Broll/B14" "https://www.youtube.com/watch?v=X4mB41ybSN4" "primary"   # Vice City helicopter chase
dl "R14.3" "04_Broll/B14" "https://www.youtube.com/watch?v=obxIhv9YhKY" "primary"   # San Andreas six-star escape
dl "R14.4" "04_Broll/B01" "https://www.youtube.com/watch?v=WNZMK7KPZWs" "primary"   # GTA 4 "Deadly Pursuit"
dl "R14.5" "04_Broll/B14" "https://www.youtube.com/watch?v=vUndgwBLKeY" "primary"   # GTA 5 "Lose the cops" cinematic
dl "R14.6" "04_Broll/B14" "https://www.youtube.com/watch?v=zCMMcsVan-E" "alternate"   # Evolution of six-star chases
dl "R14.7" "04_Broll/B14" "https://www.youtube.com/watch?v=sjjG44YMF6w" "alternate"   # Busted screens from every GTA
dl "R15.1" "04_Broll/B15" "https://www.youtube.com/watch?v=xGN6cKeZdN8" "primary"   # Race and Chase arcade gameplay (the proof shot)
dl "R15.2" "04_Broll/B15" "https://www.youtube.com/watch?v=5MJ8YgO7wUw" "reference"   # Race and Chase arcade music
dl "R15.3" "04_Broll/B15" "https://www.youtube.com/watch?v=E0TK4V7YjFo" "primary"   # GTA Online arcade business guide
dl "R15.4" "04_Broll/B15" "https://www.youtube.com/watch?v=rNsFHOtsZzw" "alternate"   # All GTA Online arcade games
dl "R17.1" "04_Broll/B01" "https://www.youtube.com/watch?v=QdBZY2fkU-0" "primary"   # GTA 6 Trailer 1 (official; Lucia in custody in the opening seconds)
dl "R17.2" "04_Broll/B17" "https://www.youtube.com/watch?v=uphThaa97ig" "alternate"   # GTA 6 "An Extended Look" (official, Netflix)
dl "R17.3" "04_Broll/B01" "https://www.youtube.com/watch?v=VQRLujxTm3c" "primary"   # GTA 6 Trailer 2 (official)
dl "R17.4" "04_Broll/B17" "https://www.youtube.com/watch?v=rz1B4B2yBZY" "primary"   # GTA 6 launch trailer (official Rockstar; logo end card)
dl "R17.6" "04_Broll/B17" "https://www.youtube.com/watch?v=_yl5ELcmugI" "alternate"   # "Pre-Load Now" (official Rockstar)
dl "RT1" "04_Broll/B16" "https://www.youtube.com/watch?v=QV4F0CygC3U" "primary"   # VHS glitch transitions, 4K
dl "RT2" "04_Broll/B02" "https://www.youtube.com/watch?v=gD9fXTRkfFE" "optional"   # CRT TV static
dl "RT3" "04_Broll/B14" "https://www.youtube.com/watch?v=wwSOHveejI0" "primary"   # Police lights flashing
dl "RT6" "04_Broll/B16" "https://www.youtube.com/watch?v=b-jt77qrRoA" "primary"   # Light leaks, 4K (for X7)
dl "RT7" "04_Broll/B01" "https://www.youtube.com/watch?v=dcLJnWyUAHg" "optional"   # GTA 5 wanted stars, green screen (for M1)
dl "RT8" "04_Broll/Textures" "https://www.youtube.com/watch?v=RePuC-WB6Xg" "optional"   # 35 mm film grain overlay
echo
echo "Done. R4.5 (design-document scans) is fetched from the web by the build; R17.5 and R1.1 are unofficial and skipped."
echo "Next: upload the whole 04_Broll folder to Google Drive, share it as 'Anyone with the link', and send the link back."

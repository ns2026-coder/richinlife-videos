# Rich in Life: highlighter style (approved by Norman, 19 Nov 2026)

Short text-only videos: grainy paper with dark edges, serif text that appears word by word while a yellow marker wipes behind it, quick cuts to one bold idea at a time (a punch card on white, a Spending/Saving toggle, a ticking clock), then a "Lessons every day / RICH IN LIFE" outro. 1080x1920, 30 fps, under 20 seconds.

No voiceover, so it costs no ElevenLabs credits. Music only: add a royalty-free track after rendering (TikTok sounds can't be added through Metricool).

## Schedule
- Posts in the 18:00 slot, one a day, uncut version (swearing allowed).
- 10:00 and 12:00 stay normal voiced videos.

## Swearing rules
- Swear in the video only. Never in the caption, title, hashtags or thumbnail.
- Swear on the punchlines, not every line (one or two words per video).
- No swearing aimed at a person or group.

## Make one
1. Copy `example_uncut.json` and write new lines. Scene types: `paper` (lines), `punch` (bold text, use \n), `toggles` (off/on labels), `clock` (question), `outro`.
2. `python3 make.py my_script.json out_dir` → `out_dir/final.mp4` (silent). Needs Python 3, Pillow, numpy and ffmpeg.
3. Add music: `ffmpeg -i out_dir/final.mp4 -i track.mp3 -map 0:v -map 1:a -c:v copy -shortest final_music.mp4`.

The script writes "For education only. Not financial advice." along the bottom of every frame.

Fonts are bundled in `fonts/` (Anton: SIL OFL; FreeSerif: GPL with font exception; DejaVu Sans: free licence).

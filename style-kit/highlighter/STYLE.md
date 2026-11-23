# Rich in Life: highlighter style (approved by Norman, 19 Nov 2026)

Short text-only videos: grainy paper with dark edges, serif text that appears word by word while a yellow marker wipes behind it, quick cuts to one bold idea at a time (a punch card on white, a Spending/Saving toggle, a ticking clock), then a "Lessons every day / RICH IN LIFE" outro. 1080x1920, 30 fps, under 20 seconds.

No voiceover, so it costs no ElevenLabs credits. Music: `highlighter_bed.mp3` is an original track made in code for this channel (no licence issues), added automatically. TikTok sounds can't be added through Metricool.

## Schedule
- Posts in the 18:00 slot, one a day, uncut version (swearing allowed).
- 10:00 and 12:00 stay normal voiced videos.

## Swearing rules
- Swear in the video only. Never in the caption, title, hashtags or thumbnail.
- Swear on the punchlines, not every line (one or two words per video).
- No swearing aimed at a person or group.

## Make one
1. Copy `example_uncut.json` and write new lines. Scene types: `paper` (lines), `punch` (bold text, use \n), `toggles` (off/on labels), `clock` (question), `outro`.
2. `python3 make.py my_script.json out_dir` → `out_dir/final_music.mp4` (post this one; `final.mp4` is the silent copy). Needs Python 3, Pillow, numpy and ffmpeg.
3. Look at a few frames before scheduling.

The script writes "For education only. Not financial advice." along the bottom of every frame.

Fonts are bundled in `fonts/` (Anton: SIL OFL; FreeSerif: GPL with font exception; DejaVu Sans: free licence).

## Writing the lines
- One idea per video, about money discipline or life discipline. Short lines, max 5 words each.
- 4-6 scenes, 15-20 seconds total. Always end with the `outro` scene.
- No named investments, no promised returns, no personal advice (Compliance.md still applies).
- Caption: one plain line plus "Not financial advice." and 3-5 hashtags. No swearing in the caption.

## Motivational videos (added 23 Nov 2026)
Norman wants more motivational videos in this look, with pictures. On motivational days (even dates):
- **10:00 short:** text + music only, 15-25 s, made with `make.py` like the 18:00 one but clean (no swearing). Motivation theme, e.g. toggles off "Motivation" / on "Discipline".
- **12:00 long:** `voiced.py`: same look timed to the ElevenLabs voice "Dan - Energetic, Young and UK-based", music bed under it, spoken sign-off added, 61-70 s. Spec scenes need a `say` line each. Example: `examples/M01.json` in the PC project's specs/ (specs/M01.json).
  `python3 voiced.py specs/M01.json voice.mp3 signoff.mp3 work/M01` -> `work/M01/final.mp4` (kept under ~9.5 MB for the web upload) and `thumb.jpg`.
- **Pictures:** scene type `picture` with `pic` = `arms` (figure arms raised), `summit` (figure on a peak), `stairs` (figure climbing), `road` (figure on a road), plus bold `text` ("LINE\nLINE"). All drawn in code: no stock photos, no brand logos or slogans (never "Just do it" or other brands' lines).
- Use 3-5 picture scenes per long video, 1-2 in a short one.

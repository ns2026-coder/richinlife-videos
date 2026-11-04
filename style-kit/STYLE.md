# Rich in Life: new video style (approved by Norman, 4 Nov 2026)

Reference: `reference_fee_sample.mp4`. Source: `reference_fee_scenes.html` (canvas, `draw(t)`), `render.js` (one mp4 per scene, joined with concat), `sfx.py` (voice + pops/ticks).

Keep the brand: navy background, green/gold/red, Poppins, "RICH IN LIFE" header, gold-highlighted word captions at about y 1395, 1080x1920, 30 fps, 61-70 s.

Rules for every new video:
- Something on screen changes every 2-4 seconds. No long held text.
- Write scenes for THIS script; do not reuse the fee scenes. Build the idea visually: objects that move, counters that count, charts that race, cards that fill.
- At least 2 "interaction" moments: a finger tapping or dragging a control, ticking a checklist, picking a poll option.
- Hook: big kinetic opener in the first 2 seconds that acts out the first line.
- Comment prompt: a poll or question card that leads into "Comment below". Never show invented poll results.
- End card: finger taps FOLLOW, it becomes "Following", then "Lessons every day" and the sign-off appear line by line.
- Moving background, progress bar along the top, quiet sound effects on actions, always under the voice.
- Charts drawn to real numbers, computed in code. Anything illustrative stays labelled.
- Keep the on-screen disclaimer for the whole video up to the end card, at the size in the reference.
- Compliance rules in AUTOMATION.md still apply.

Timing: get sentence times from pauses in the voice audio (ffmpeg silencedetect), spread words within a sentence by length, and check caption frames against the audio timings.
Before the full render, look at full-size frames at the busiest moments and fix overlaps.

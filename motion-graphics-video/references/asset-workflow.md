# Asset workflow

A promo needs images, a voice, and usually a music bed. This file covers
where each one comes from and what to do when you do not have it.

The rule the user set: **create assets when you can, and when you cannot,
write the exact prompt and ask.** Both paths are mandatory. The
placeholder system exists so that asking never blocks a render - it does
not exist so that you can skip asking.

## The order of operations

1. Write the storyboard, including every asset slot in `assets_needed`.
2. Run `make_placeholders.py` - it writes placeholders and
   `ASSETS_REQUEST.md`.
3. **Generate the assets you can generate.** Replace the placeholders.
4. **Ask the user for the rest.** Point at `ASSETS_REQUEST.md` by name.
5. Re-run the build.
6. Say which assets are still placeholders when you deliver.

Step 6 is not optional. A video that ships with grey boxes in it and no
admission is a bad delivery, even if every other frame is perfect.

## Images

### What an image needs to be

Generated images almost always fail for one of four reasons, and all four
are fixable in the prompt:

- **Wrong aspect ratio.** The prompt must state the exact pixel size. The
  renderer fits with `cover` (fill and crop) or `contain` (fit inside).
- **Something in the middle.** A hero image with a subject dead-centre
  will be covered by your headline. Say what must stay clear.
- **Wrong mood.** "3D render, navy and azure, soft rim light, shallow
  depth of field" is worth more than "nice picture of a laptop".
- **Text in the image.** Generated images put garbled text in them.
  Always say "no text, no watermark, no logos" and never rely on the
  model to spell anything.

### The prompt shape

`make_placeholders.py` writes prompts in this shape. Use it as the
template for your own:

```
Subject: <what it is>.
Format: <width>x<height> (<ratio>).
Style: <medium, lighting, palette, depth of field>.
Purpose in the edit: <the shot it serves>.
Composition constraint: <what must stay clear, or "none">.
No text, no watermark, no borders.
```

### What to generate versus what to ask for

**Generate these yourself** - they are abstract, stylised, and easy to
get right:

- Gradient plates and glow fields.
- Abstract 3D shapes, glass panels, floating cards.
- Abstract circuit or grid textures.
- A pure white or pure black frame for a transition.
- Generic UI mockups (a dashboard with meaningless charts).

**Ask the user for these** - they are specific to their product or
brand, and a generated stand-in will be visibly wrong:

- Their product, their logo, their app screens.
- Their actual results (before/after edits, student work).
- Their team, their office, their face.
- Brand assets: logo, brand colours, typefaces.

A screenshot of their real software is worth more than any generated
image you can make. Always ask for it.

### Photographic sources

If the user has a source video, frames can be lifted from it. This is
almost always better than generating: it is their actual footage.

```bash
ffmpeg -ss 12.5 -i raw.mp4 -frames:v 1 -q:v 2 assets/still_12s.jpg
```

Lift a still at the moment the person says the thing the still is about.
Check the frame - a still that catches a blink ruins a card.

## Audio

### The voice

**The best voice is the one already recorded.** If the user gave you a
talking-head video, that audio is the spine of the piece. Do not replace
it with TTS.

To use it as a clean narration track:

```bash
ffmpeg -i raw.mp4 -vn -ac 1 -ar 48000 -c:a pcm_s16le voice.wav
```

Cut it to the parts you actually use:

```bash
ffmpeg -ss 0.0 -t 22.5 -i voice.wav -ac 1 -ar 48000 voice_cut.wav
```

**If there is no voice and no TTS**, you have three options, in order of
preference:

1. Ask the user to record the script. It is a 60-second job for them
   and it will always beat a synthetic voice.
2. Use the agent's TTS if it has one. Be honest in the delivery that the
   voice is synthetic.
3. Deliver the video without narration, built as a music-driven promo
   with the text carrying the message. This is a legitimate format -
   many high-performing social promos are silent - but say that is what
   you did.

**Never ship a synthetic voice without saying so**, and never ship a
misheard transcript as if it were the user's words.

### Music

A promo needs a bed. The reference film runs a constant tonal bed under
continuous speech, and its mix window is about 1 dB - the music is
*under* the voice, not ducking around it.

Default mix: music at **-13 dB**, no ducking. Use `--duck` when the
voice is quiet or the music has a loud transient (drums) that needs to
give way.

```bash
python scripts/build_video.py sb.json -o out.mp4 \
    --music music.mp3 --music-gain -13 --duck
```

If the user has no music, ask for it - or pick a royalty-free bed
they can license, and tell them which track and where it came from.

### Levels

Measured from the reference film, and a good target for any promo:

| Metric | Reference | Target |
|---|---|---|
| Integrated loudness | ~-16 LUFS | -16 LUFS |
| True peak | -6.1 dB | -1.0 dBTP |
| Median RMS | -18.9 dB | -18 to -16 dB |
| Music relative to voice | ~1 dB window | -13 dB bed, no duck |

Normalise before you mix:

```bash
ffmpeg -i voice.wav -af loudnorm=I=-16:TP=-1.0:LRA=11 voice_norm.wav
```

## Sound effects

The reference film has **none**. Not one SFX across 141 seconds. Every
impact is visual - the white blowout, the arc iris, the number slamming
in. This is a real design decision, not an oversight: the visuals carry
the punctuation so the mix stays clean.

If you add SFX, you are departing from the model. That is allowed if the
user wants it, but:

- Use at most two or three across the whole video.
- Place them on the visual impacts, not on every beat.
- Keep them 12-18 dB below the voice.
- Never use a generic "whoosh" on every transition.

## The request file

`ASSETS_REQUEST.md` is the handoff. It should be readable by someone who
has never seen the project, and it should be answerable without asking
you a follow-up question. Each entry has:

- **Save to** - the exact path, so the file lands where the storyboard
  expects it.
- **Size** - the exact pixel dimensions.
- **Kind** - what it is used as.
- **Prompt** - a complete, copy-pasteable generation prompt.

Keep the "Save to" paths relative to the storyboard. The renderer
resolves them relative to the storyboard file, so the project stays
portable.

## The placeholder

The placeholder is not a grey box. `make_placeholders.py` writes a
designed stand-in in the film's own visual language - the correct
palette, a soft bokeh wash, a diagonal hatch, and the asset's name - so
the layout reads correctly and only the artwork is missing.

That matters for review: a designer can approve the composition, the
type sizes and the timing from the placeholder version, and swap the art
in later without re-rendering the layout.

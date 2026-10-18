---
name: motion-graphics-video
description: >-
  Turn a raw talking-head video, a raw script, a voice recording, or a product
  idea into a finished motion-graphics promo video, rendered entirely from
  code with Pillow + ffmpeg. Use this whenever the user mentions a talking
  head, a raw clip, a script for a video, a promo, an explainer, a reel, a
  YouTube video, a course ad, "make it look like a pro edit", "add motion
  graphics", "kinetic typography", "animated text video", "explainer video",
  "social promo", or hands over an .mp4 of them talking and expects a polished
  edit back - even if they never say the words "motion graphics" or "storyboard".
  Also use it when they ask to make a video look premium, expensive, or
  broadcast-quality, or want captions, lower thirds, animated titles, number
  callouts, or product reveals added to existing footage.
license: MIT
metadata:
  version: "1.0.0"
  renderer: "python + Pillow + numpy + ffmpeg"
---

# Motion-graphics video from code

This skill renders a finished, broadcast-looking promo video from a
storyboard JSON. No After Effects, no GUI, no daemon - just Python drawing
into frames and ffmpeg muxing them.

The renderer was reverse-engineered from a real 2:21 Bengali promo
(2560x1440, AV1, 78 detected segments) and every number in the design
system - the palette, the type scale, the eight reusable graphic
components, the motion timings, the shot rhythm - was measured from that
film rather than invented. `references/design-system.md` has the numbers;
`references/storytelling.md` has the argument structure.

## The one rule

**A video is an argument, not a pile of animations.** Every shot must
state what it is doing for the argument. The validator refuses to render a
storyboard where a shot has no stated purpose, where the hook is late, or
where the video never asks for anything. That check is the point of this
skill - without it, "make it look good" quietly produces 90 seconds of
motion that says nothing.

## Workflow

Work through these in order. Do not skip step 3 - the storyboard is the
design, and the render is a consequence of it.

### 1. Understand the input

Two entry points, and they need different first moves.

**A raw talking-head video.** First find out what is actually in it:

```bash
python scripts/analyze_input.py raw_talking_head.mp4 -o input.json
```

This reports duration, resolution, loudness, speech regions and a
motion-energy timeline. Read it before you write a word of the script. If
the audio has no speech (or only a music bed), you are making a
music-driven promo, not a narrated one - say so and adapt.

**A script.** You have the words. You do not need ASR at all. But you do
need to know how long the read takes, because a script's length sets the
edit's length:

```bash
python scripts/transcribe.py --script script.txt --media 60s.wav -o beats.json
```

Use `--media` with a silent track of the expected length to get the beat
timings, or omit it and the script is timed from a 2.4 words/second promo
read rate.

**Either way**, before writing the storyboard, produce a one-paragraph
brief for yourself: who is this for, what do they currently believe, what
must they believe at the end, and what single action should they take?
Every shot you write is judged against that paragraph.

### 2. Write the script or extract it

If the user gave a raw video, transcribe it:

```bash
python scripts/transcribe.py raw_talking_head.mp4 -o transcript.json
```

ASR is a first draft, not a script. Read it, fix the mistakes, and *cut
it*. A promo read is 1.7-3.3 words per second (measured). If the
transcript is longer than that allows, it is a conversation, not a promo.

If ASR is unavailable or unreliable (it often is on noisy, accented, or
non-English audio - check the output, do not trust it), use a
whisper.cpp build with a large-v3-turbo model, or simply ask the user for
the script. Asking is better than shipping a video with a misheard
sentence burned into it.

### 3. Write the storyboard

This is the design. Copy the template and edit it:

```bash
cp assets/storyboard.template.json my_video.json
```

The storyboard carries three things the renderer needs and two things the
validator needs:

- `acts` - the beats of the argument. Use the four-beat arc from
  `references/storytelling.md`: **Hook, Problem, Credibility, Offer**.
- `shots` - each with a `duration`, a `purpose` (a sentence on what this
  shot does for the argument), a `voice` line (the words said over it),
  and a stack of `layers`.
- `assets_needed` - every image the film wants, with a generation prompt.

Read `references/storytelling.md` before you write the acts. Read
`references/design-system.md` before you pick colours. Read
`references/motion-recipes.md` before you animate anything.

### 4. Resolve the assets

```bash
python scripts/make_placeholders.py my_video.json --outdir assets/ \
    --requests ASSETS_REQUEST.md
```

This writes a designed placeholder for every missing asset so the render
never blocks, and writes `ASSETS_REQUEST.md` with a ready-to-paste
generation prompt for each one.

**Then do one of these, and do not skip it:**

- **If you can generate images**, generate them. Paste the prompt into
  your image model, save the output at the exact path in the request file,
  and re-run the build. A generated hero image is worth ten placeholder
  rectangles.
- **If you cannot**, hand `ASSETS_REQUEST.md` to the user and ask them to
  supply the files at the listed paths. Say plainly which assets are
  placeholders so nobody is surprised at delivery.

Never silently ship placeholders as if they were finished art.

### 5. Validate, then render

```bash
python scripts/validate_storyboard.py my_video.json --timeline
python scripts/build_video.py my_video.json -o out.mp4
```

The build refuses to run if validation reports errors. That is deliberate.
Fix the story, not the validator. (`--force` exists for when you are
iterating on the look, not the argument.)

Output is H.264 in MP4 with `+faststart` so it plays in a browser and in
the in-app preview.

## Audio

The soundtrack is half the video. Rules of thumb, all measured from the
reference film:

- **The voice is the spine.** A talking-head recording is already a
  finished performance. Build the edit around its natural pauses, not
  against them.
- **Music sits under, it does not compete.** The reference film's mix
  window between voice and bed is about 1 dB. Default the music to -13 dB
  and use `--duck` if the voice needs more room.
- **Normalise the voice to about -16 LUFS and -1 dBTP.** The reference
  film measures -16/-17 dBFS RMS with a -6.1 dB peak.
- **There is no SFX layer in the reference film.** Not one. Every impact
  is visual. If you add sound effects you are departing from the model -
  which is fine if you want to, but the visual punch carries it.

If the user has no music, say so and deliver the voice-only cut. If the
user has no voice and gave you a script, you need text-to-speech - use
whatever the agent has, or ask.

## Components

The renderer ships a kit of reusable pieces so the whole film reads as one
hand made it: gradient pill, speech bubble, glass card with corner
brackets, avatar badge, label pill with a pointer, cursor, monitor on a
stand, circuit plate, plus hero numerals, sparkles, rising graph, app
icons and a phone mockup.

Reach for a component before you reach for a custom shape. A pill that
means "success" is green in every shot of the film; a red pill means
"wrong" in every shot. Consistency is most of what makes motion graphics
look expensive.

## Troubleshooting

**Text renders as empty boxes** - the script font is missing. Run
`python scripts/fetch_fonts.py --all-scripts` and set `meta.language` in
the storyboard (`bn`, `hi`, `ar`, `zh`...). Pillow with Raqm does the
shaping, so Bengali and Arabic conjuncts come out right.

**The background looks grey, not navy** - the bokeh is too strong. Lower
`alpha` on the `bg` layer (32 is a good default) and use `NAVY` and
`ELECTRIC` in `colors` rather than `SKY`.

**The render is slow** - 1080p at 30 fps runs roughly 4-6x realtime on a
small CPU. Use `--preview N` to dump stills while iterating, and render
at 1280x720 while you are still changing things.

**ffmpeg is not found** - `pip install imageio-ffmpeg`, or install ffmpeg
system-wide. The renderer looks in `PATH`, then at imageio-ffmpeg, then
at `bin/ffmpeg` inside the skill.

## Files

```
scripts/build_video.py       render a storyboard to mp4
scripts/validate_storyboard.py  check a storyboard for narrative and technical faults
scripts/analyze_input.py     probe a raw video: loudness, speech, motion energy
scripts/transcribe.py        ASR, or align a known script to a recording
scripts/make_placeholders.py  resolve missing assets; write ASSETS_REQUEST.md
scripts/fetch_fonts.py       download the typefaces
scripts/selftest.py          smoke-test the renderer before a long render
scripts/mgv/                 the renderer (theme, draw, components, layers, render)
references/design-system.md  measured palette, type scale, component kit
references/storytelling.md   the four-beat arc, hook and CTA patterns
references/motion-recipes.md the animation vocabulary, copy-pasteable
references/asset-workflow.md how to get images, music and voice
assets/storyboard.template.json  the schema, with a worked example
assets/samples/              a runnable sample storyboard and its output
```

# motion-graphics-video

A reusable skill that turns a raw talking-head video **or** a raw script
into a finished, broadcast-looking motion-graphics promo - rendered
entirely from code.

No After Effects. No GUI. No daemon. Python draws into frames, ffmpeg
muxes them, and a validator refuses to render a video that does not tell
a story.

## What it produces

H.264 MP4, `+faststart`, 1080p at 30 fps by default. The look is
reverse-engineered from a real 2:21 Bengali promo (2560x1440, AV1, 78
detected segments) - the palette, the type scale, the eight reusable
graphic components, the motion timings, the shot rhythm and the audio
mix were all measured from that film rather than invented.

## Quick start

```bash
pip install -r requirements.txt
python scripts/fetch_fonts.py --all-scripts

# 1. look at what you were given
python scripts/analyze_input.py raw_talking_head.mp4 -o input.json

# 2. write the storyboard (this is the design)
cp assets/storyboard.template.json my_video.json && $EDITOR my_video.json

# 3. resolve the images
python scripts/make_placeholders.py my_video.json --requests ASSETS_REQUEST.md

# 4. check it, then render
python scripts/validate_storyboard.py my_video.json --timeline
python scripts/build_video.py my_video.json -o out.mp4
```

A runnable sample lives in `assets/samples/demo.storyboard.json`, and
`assets/samples/demo_output.mp4` is what it produces:

```bash
python scripts/selftest.py          # ~10s smoke test
python scripts/build_video.py assets/samples/demo.storyboard.json \
    -o demo.mp4 --width 1920 --height 1080
```

## The design

```
SKILL.md                     the workflow, and the one rule
references/
  storytelling.md             the 4-beat arc, hook and CTA patterns, the validator's rules
  design-system.md            measured palette, type scale, the component kit, the light model
  motion-recipes.md           the animation vocabulary, copy-pasteable
  asset-workflow.md           images, voice, music, and the ask-the-user protocol
scripts/
  build_video.py              storyboard -> mp4
  validate_storyboard.py      narrative + technical checks
  analyze_input.py            probe a raw video
  transcribe.py               ASR, or align a known script
  make_placeholders.py        resolve assets; write ASSETS_REQUEST.md
  fetch_fonts.py              download the typefaces
  selftest.py                 smoke-test the renderer
  mgv/                        the renderer
    theme.py                  palette, gradients, type scale
    draw.py                   gradients, glow, shadows, type
    components.py             the eight reusable assets
    layers.py                 layer renderers + the animation system
    render.py                 the frame loop and the ffmpeg pipe
    easing.py                 the curves
    fonts.py                  typeface resolution and variable-font weights
assets/
  storyboard.template.json    the schema, with a worked example
  samples/                    a runnable sample storyboard
  fonts/                      fetched typefaces
evals/evals.json              six evaluation prompts
```

## Requirements

- Python 3.10+
- Pillow with **Raqm** (for Bengali/Arabic/Devanagari shaping) and numpy
- ffmpeg - on `PATH`, or `pip install imageio-ffmpeg`

Check the shaping support:

```bash
python -c "from PIL import features; print('raqm:', features.check('raqm'))"
```

`True` is what you want. If it is `False`, Bengali will render as empty
boxes.

## Licence

MIT.

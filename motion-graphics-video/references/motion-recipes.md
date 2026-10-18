# Motion recipes

Copy-pasteable animation specs. Every one of these is implemented by the
renderer's `in` / `out` fields.

## The animation vocabulary

A layer's `in` describes how it arrives; its `out` describes how it
leaves. Both are optional.

```json
"in":  { "type": "pop", "dur": 0.4, "delay": 0.2, "ease": "back" }
"out": { "type": "fade", "dur": 0.25, "ease": "ease_in" }
```

`dur` is in seconds. `delay` is the wait before the animation starts -
this is how you stagger several elements without writing separate shots.
`ease` is one of the curves below.

### Curves

| `ease` | Behaviour | Use for |
|---|---|---|
| `linear` | constant speed | mechanical moves, marquees |
| `ease_out` | fast then slow | **the default entrance** |
| `ease_in` | slow then fast | exits, things falling away |
| `ease_in_out` | slow-fast-slow | moves that start and end on screen |
| `back` | overshoots and settles | pills, icons, pops |
| `elastic` | wobbles into place | hero numerals, celebrations |
| `bounce` | bounces | playful, rare - use once per video |
| `smooth` | smoothstep | masks, wipes, anything subtle |
| `expo` | very fast then very slow | light streaks, fast reveals |

An unknown name falls back to `ease_out` rather than crashing, so a typo
degrades to something reasonable instead of killing a long render.

### Types

| `type` | What it does | Extra keys |
|---|---|---|
| `fade` | alpha 0 to 1 | - |
| `slide` | moves in from an offset | `from: [dx, dy]` as fractions of the frame |
| `rise` | comes up from below, with a fade | `from: 0.12` (fraction of height) |
| `pop` | scales up with an overshoot | `from: 0.6` (starting scale) |
| `scale` | scales, no overshoot | `from: 0.8` |
| `spin` | rotates in | `from: 90` (degrees) |
| `whip` | fast diagonal pass | `from: [-1.4, 0.35]` |
| `wipe_iris` | circular reveal, expanding | - |
| `wipe_bars` | vertical bars, left to right | `bars: 12` |
| `wipe_diagonal` | angled band wipe | `band: 0.35` |
| `type_on` | horizontal wipe, for type | - |
| `blur_in` | resolves from a blur | `from: 14` (blur radius) |

## The reference film, measured

From the 78-segment analysis of `push.mp4`:

- Mean shot length **1.81 s**, median **1.56 s**.
- 11 segments under 5 motion units (essentially still), 5 over 20.
- The busiest segment scored 47.6; the stillest 0.0.
- Motion-energy peaks at 3 s, 16 s, 23 s, 54 s, 56 s, 80 s, 95 s.
- Dead zones at 9-10 s, 15 s, 40-41 s, 49 s, 114-115 s, 130-133 s.
- 23 hard cuts, at 2.00, 3.88, 4.80, 6.40, 11.76, 18.08, 26.28, 45.00,
  54.04, 54.20, 56.12, 61.04, 63.52, 64.28, 70.60, 78.00, 80.44, 95.04,
  95.80, 109.76, 121.88, 134.92, 138.72 s.
- 29 I-frames at exactly 0, 5, 10 ... 140 s - a 5-second GOP.
- The picture cuts to black at 138.72 s, 0.13 s before the music stops.

Transitions, in order of how often they appear:

1. **White arc iris** (4x) - a white circle expands from the subject.
2. **Full-frame white blowout** - one frame of pure white.
3. **Radial zoom** - the frame rushes toward the viewer.
4. **Diagonal band** - a white bar sweeps across at an angle.
5. **Light streak** - a horizontal flare.
6. **Push-in** - a slow scale on a still.

The white arc iris and the white blowout are the film's signature. They
are cheap to reproduce and they read as expensive because the white is
genuinely 255,255,255 and the shape is a clean circle.

## Recipes

### Hook: a headline that lands

```json
{
  "type": "text", "text": "MOST PEOPLE EDIT.",
  "lines": ["MOST PEOPLE EDIT.", "VERY FEW GET HIRED."],
  "x": 0.5, "y": 0.44, "anchor": "mm",
  "size": 0.072, "weight": "black", "color": "#EEF2F4",
  "line_spacing": 1.18, "letter_spacing": 2.0,
  "in": { "type": "wipe_bars", "dur": 0.45, "ease": "ease_out" }
}
```

`wipe_bars` on the headline, then a `pop` on the pill below it, 0.4 s
later. That is a complete hook in one shot.

### The hero numeral

```json
{
  "type": "numeral", "text": "1500+", "gradient": "green_lime",
  "x": 0.5, "y": 0.46, "w": 0.62, "h": 0.40, "rays": true,
  "in": { "type": "pop", "dur": 0.55, "ease": "elastic" }
}
```

`elastic` on the number, then a `slide` on the label 0.5 s later. Green
because it means success.

### A pill that names a thing

```json
{
  "type": "pill", "text": "STUDENTS TRAINED", "gradient": "green_black",
  "x": 0.5, "y": 0.76, "w": 0.34, "h": 0.07, "bullet": false,
  "in": { "type": "slide", "from": [0, 0.12], "dur": 0.4, "delay": 0.5 }
}
```

### A talking head with a bubble

```json
{
  "type": "video", "src": "raw.mp4", "src_in": 12.0, "src_dur": 3.5,
  "x": 0.5, "y": 0.5, "w": 1.0, "h": 1.0, "fit": "cover"
},
{
  "type": "bubble", "text": "Software is not craft.", "tail": "down",
  "fill": "#EEF2F4", "text_color": "#070E1E",
  "x": 0.5, "y": 0.17, "w": 0.44, "h": 0.17,
  "in": { "type": "pop", "dur": 0.4, "delay": 0.5, "ease": "back" }
}
```

The bubble enters on `back` - it overshoots slightly and settles, which
is what makes it feel like a physical object.

### A before/after comparison

Two `card` layers sliding in from opposite sides, then two `label` layers
fading in underneath:

```json
{ "type": "card", "x": 0.30, "y": 0.46, "w": 0.38, "h": 0.56,
  "fill": "#072B6D", "alpha": 240, "brackets": true, "border": true,
  "src": "assets/before.png",
  "in": { "type": "slide", "from": [-0.18, 0], "dur": 0.4 } },
{ "type": "card", "x": 0.70, "y": 0.46, "w": 0.38, "h": 0.56,
  "fill": "#0C4DC6", "alpha": 240, "brackets": true, "border": true,
  "src": "assets/after.png",
  "in": { "type": "slide", "from": [0.18, 0], "dur": 0.4, "delay": 0.12 } }
```

`delay: 0.12` is the stagger. Do not exceed 0.15 s or the second element
feels late rather than choreographed.

### The CTA

```json
{ "type": "pill", "text": "ENROL NOW", "gradient": "azure_cyan",
  "x": 0.5, "y": 0.74, "w": 0.30, "h": 0.095, "bullet": false, "glow": 1.2,
  "in": { "type": "pop", "dur": 0.4, "delay": 0.55, "ease": "back" } },
{ "type": "cursor", "x": 0.70, "y": 0.80, "w": 0.06, "h": 0.10,
  "in": { "type": "whip", "from": [-0.6, -0.2], "dur": 0.45, "delay": 0.9 } }
```

The cursor arrives 0.35 s after the button and whips in from off-frame.
`glow: 1.2` on the button makes it the brightest thing on screen, which
is how you tell the eye where to go.

## Timing rules of thumb

- **Entrances: 0.3-0.55 s.** Faster than 0.25 s reads as a jump cut;
  slower than 0.7 s reads as a wait.
- **Exits: 0.2-0.3 s.** Exits should be quicker than entrances.
- **Stagger: 0.1-0.15 s** between related elements.
- **Delay the second beat:** the first element arrives, the supporting
  element lands 0.3-0.5 s later. This is the "punch then rest" pattern
  inside a single shot.
- **Nothing animates for longer than 0.6 s.** A 2-second animation is a
  mistake; make the element arrive and then hold.

## Layer order

Layers render bottom to top, in the order they appear in the array.
Typical order:

1. `bg` - the plate
2. `video` / `image` - the footage or the artwork
3. `circuit` - an overlay plate, if used
4. `card`, `monitor`, `phone` - the frames
5. `pill`, `label`, `bubble`, `numeral`, `icon` - the graphic elements
6. `text` - the type, always on top
7. `sparkles`, `cursor` - the accents, always last

## The white transitions

The reference film's signature is a hard white. To reproduce one, add a
layer that is white and covers the frame, with a `wipe_iris` in and a
`fade` out:

```json
{ "type": "image", "src": "assets/white.png", "w": 1.0, "h": 1.0,
  "fit": "contain", "shadow": false,
  "in":  { "type": "wipe_iris", "dur": 0.25, "ease": "ease_out" },
  "out": { "type": "fade", "dur": 0.2 } }
```

Generate `assets/white.png` as a pure 1920x1080 white frame, or as a
`bg` layer with `style: "solid"` and `color: "#FFFFFF"` - the renderer
will happily draw a solid white layer, but the `bg` layer is opaque and
would cover the shot underneath, so put it in its own shot.

Cleanest: make the transition its own shot with a 0.3 s duration and a
solid white background, and cut to the next shot right after it. That
is exactly what the reference film does - 23 hard cuts, several of which
are a single white frame between two shots.

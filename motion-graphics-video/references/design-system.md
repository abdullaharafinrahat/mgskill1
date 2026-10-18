# Design system

Every value here was measured from the reference promo (2560x1440, 25 fps,
2:21, 3,526 decoded frames, 78 segments) rather than chosen by taste. That
matters: it means the numbers below are the ones that make flat vector
graphics read as expensive on a phone screen.

## The core insight: bottom-heavy in value

The reference film's global colour histogram:

| Colour | Share | Role |
|---|---|---|
| `#070E1E` void navy | 29.4% | the base, the dark |
| `#072B6D` royal ultramarine | 14.2% | panels, chrome, the tech plate |
| `#494142` warm charcoal | 12.2% | the presenter, the 3D rooms |
| `#EEF2F4` paper white | 10.6% | type, clean surfaces |
| `#918377` warm sand | 10.6% | skin, beige walls, soft type |
| `#0C4DC6` electric azure | 8.6% | **the accent** |
| `#BEBEB5` neutral steel | 8.4% | grey-green neutrals |
| `#60A2F0` sky blue | 6.0% | gradient midpoints, glass edges |

Luminance distribution: 21.9% near-black, 29.9% shadow, 17.4% midtone,
15.6% bright, 15.2% highlight.

Read that again: **over half the frame is below 0.25 luma.** The film is
dark, and the only saturated colour is the accent. This is the single
biggest difference between flat vector graphics that look cheap and flat
vector graphics that look expensive - cheap ones use a bright background
and colour the type. Expensive ones use a dark background and colour the
*shape*.

Hue distribution: azure 75.3%, red 8.4%, cyan 5.8%, orange 5.1%, green
2.0%, lime 0.9%, blue 0.9%, teal 0.7%, magenta 0.4%, yellow 0.4%.

## The palette

```
VOID       #070E1E   base background, the void
NAVY       #072B6D   glass panels, the circuit plate
CHARCOAL   #494142   presenter, 3D interiors
PAPER      #EEF2F4   type, clean surfaces
TAUPE      #918377   skin, soft secondary type
ELECTRIC   #0C4DC6   the accent
SKY        #60A2F0   gradient midpoints, glass edges
STEEL      #BEBEB5   neutral greys

GREEN      #1FBF5A   money, proof, success
LIME       #C6F23C   a service tier, a module
CRIMSON    #E03A4E   the wrong path, a warning
PINK       #C44BC8   the second-tier option
PERIWINKLE #7C8CE8   colour grading, a service category
TEAL       #2E6E63   storytelling
VIOLET     #7A3CFF   title-card sheen
PURPLE     #B98CFF   the cursor
```

Semantic use is in `references/storytelling.md`. The rule is that colour
*means* something, and it means the same thing in every shot.

## Gradients

All linear, all lit from the left. Never mesh, never multi-stop
rainbow - the reference film's gradients are two-stop and read as a light
source behind a glass surface.

| Name | From | To | Use |
|---|---|---|---|
| `azure_ramp` | `#001F5F` | `#003FBF` | the deep brand ramp |
| `azure_cyan` | `#0C4DC6` | `#60A2F0` | the default pill |
| `magenta_blue` | `#C44BC8` | `#3A6FD8` | the second-tier option |
| `teal_lime` | `#2E6E63` | `#C6F23C` | premium tier |
| `blue_lime` | `#4FA8E8` | `#9BE84A` | a service label |
| `green_lime` | `#1FBF5A` | `#C6F23C` | earnings, growth, the hero numeral |
| `azure_black` | `#1A5FB4` | `#05070E` | the wrong path, fading out |
| `green_black` | `#1FBF5A` | `#03150A` | a proof pill that sits on dark |
| `violet_black` | `#7A3CFF` | `#0A0714` | title cards |
| `paper_sky` | `#EEF2F4` | `#60A2F0` | a light gradient, used sparingly |

Override any of them per project in the storyboard's `theme` block.

## Type

One family, heavy weights, generous tracking on display type.

| Role | Size (fraction of frame height) | Weight | Use |
|---|---|---|---|
| `hero` | 0.235 | black | the giant numerals |
| `display` | 0.105 | black | section headlines |
| `headline` | 0.072 | black | the main on-screen line |
| `subhead` | 0.052 | semibold | the supporting line |
| `pill` | 0.038 | bold | a label inside a pill |
| `body` | 0.030 | medium | chat bubbles, captions |
| `micro` | 0.022 | bold | badges, corner labels |
| `caption` | 0.042 | medium | burned-in subtitles |

Two rules that do most of the work:

- **Track out your display type.** 1.5-3 px of letter spacing on caps is
  the difference between "someone set this in a font" and "someone
  designed this". The renderer supports `letter_spacing` on text layers.
- **One family, two weights.** The reference film uses a single
  geometric sans at black and bold. Contrast comes from size and colour,
  not from mixing typefaces.

Letter spacing is applied per glyph, so it is Latin-only by design -
shaping a complex script letter by letter would break the conjuncts.
Bengali and Arabic render as a single shaped run.

## The component kit

Eight repeating components account for essentially all of the reference
film's graphic elements. The gradient pill alone appears 19 times.

| Component | Layer type | What it is |
|---|---|---|
| Gradient pill | `pill` | rounded bar, two-stop gradient, white bold type, optional white bullet dot, neon outer glow |
| Speech bubble | `bubble` | rounded white balloon with a triangular tail, text wrapped and auto-fitted |
| Glass card | `card` | navy panel, optional image, corner brackets, thin sky-blue border |
| Avatar badge | `avatar` | circular portrait inside a coloured ring |
| Label pill | `label` | small pill with a pointer that names what it points at |
| Cursor | `cursor` | purple triangular pointer with a white outline and a glow |
| Monitor | `monitor` | flat panel on a thin stand, with screen content |
| Circuit plate | `circuit` | blue PCB-style trace background |

Plus: `numeral` (hero number with radiating rays and a gradient fill),
`sparkles`, `graph` (rising line with an arrow), `icon` (3D app tile),
`phone` (device mockup), `bg` (six background styles).

### The gradient pill in detail

It is the most-used element in the film, so it is worth getting right:

- Fully rounded ends (radius = half the height).
- Two-stop horizontal gradient, light on the left.
- White bold type, tracked out ~1 px.
- An optional white bullet dot on the left - a 0.075-radius circle.
- A coloured outer glow: the pill's own colour, blurred, screen-blended
  onto the backdrop. The glow is what makes it look lit rather than
  pasted. Screen blending, not alpha blending - a glow *adds* light.
- A soft drop shadow below.

Colour carries the meaning. Green = success, red = the mistake, lime = a
tier, azure = the default.

## Backgrounds

Six styles, all available as `bg` layers:

| `style` | What it is | When |
|---|---|---|
| `bokeh` | deep navy with soft coloured discs | the default; hides banding, adds depth |
| `radial` | radial gradient from an inner to an outer colour | behind a talking head |
| `gradient` | linear two-stop gradient | a section change |
| `circuit` | PCB trace plate on navy | technology, tools, software |
| `solid` | a flat colour | a hold before a transition |

Bokeh settings that work: `count` 50-70, `alpha` 28-36, `max_r` 0.12-0.15,
colours `["NAVY", "ELECTRIC"]` with `SKY` used sparingly. If the plate
reads grey rather than navy, the discs are too bright or too many.

Every background gets a vignette by default (`vignette: true`,
`vignette_strength: 0.5`). The reference film crushes its edges to the
void colour, and the vignette is what stops a flat gradient from looking
like a flat gradient.

## The light model

Three rules, and they are the difference between "graphics" and
"motion graphics":

1. **Glows are additive.** A glow is rendered as a blurred alpha mask
   and *screen*-blended onto the backdrop, so it adds light instead of
   replacing what is under it.
2. **Shadows fall behind.** A shadow is composited *under* the element
   that casts it. Compositing it on top darkens the element itself and
   is the single most common bug in this kind of renderer.
3. **Edges are supersampled.** Everything is drawn at 2x and downscaled
   with Lanczos. That is why the curves are clean without a GPU.

## Motion

The reference film's measured motion grammar - all of it is in
`references/motion-recipes.md`:

- Entrances decelerate hard (cubic ease-out). Exits accelerate away.
- Elements overshoot and settle (`back`, 1.70 overshoot).
- Mean shot length 1.81 s, median 1.56 s.
- 23 hard cuts in 141 s, clustered at change of act.
- Six transition types: white arc iris (4x), full-frame white blowout,
  radial zoom, diagonal band, light streak, push-in.
- No SFX anywhere. Every impact is visual.

## Spacing and layout

- 5% of frame width is the minimum margin.
- Optical centring: type sits slightly above true centre, at y = 0.44
  rather than 0.50, because the descender pulls the visual centre up.
- A `max_width` on a text layer auto-shrinks the type so two headlines
  never collide. Use it whenever two pieces of type sit side by side.
- The reference film uses a 16:9 master at 2560x1440. Render at
  1920x1080 for delivery; the vertical 9:16 cut is a separate storyboard
  with its own layout, not a crop.

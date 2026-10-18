# Storytelling

The renderer's job is to draw frames. The storyboard's job is to make
someone care. This file is the argument structure; `references/design-system.md`
is the look.

Everything here was measured against a real 2:21 Bengali promo for an
online video-editing course. Its voiceover runs a four-beat persuasion
arc over 141 seconds, and its edit punctuates that arc with a measured
rhythm of 78 segments averaging 1.81 s. The numbers below are what makes
the difference between a video that persuades and one that just moves.

## The four-beat arc

A promo is not a documentary. It is four moves, and if you skip one the
video feels incomplete even when every shot looks good.

| Act | Job | Length | What the viewer should feel |
|---|---|---|---|
| **Hook** | Stop the scroll | 0-6 s | "That is about me" |
| **Problem** | Name the cost | 6-22 s | "That is my problem" |
| **Credibility** | Earn the right | 22-45 s | "They know what they are talking about" |
| **Offer** | Make the ask | 45-60 s | "This is what I do next" |

Declare them in `acts`, assign every shot to one, and let the validator
check you. The reference film's arc, in its own words:

1. **Market fact** (0:00-0:30) - video editing has the highest demand,
   thousands of pieces of content go out daily.
2. **The mistake** (0:30-1:03) - learning the tools instead of the skill.
   "একটা ভুল করেছেন" - *you have made one mistake* - on a red pill.
3. **Credibility** (1:03-1:32) - who is talking, and the evidence:
   a name, money, national-to-international reach, a specific student
   count, and a line about never having learned the tools themselves.
4. **The offer** (1:32-2:21) - what is included, what it costs in time,
   and the single action: **Enroll**.

### Act timing, adjusted for runtime

The percentages matter more than the seconds. For a 60-second video the
hook gets 6 s, the problem 16 s, credibility 23 s, offer 15 s. For a
15-second vertical cut, the hook gets 1.5 s, the problem 4 s, credibility
6 s, offer 3.5 s. The offer never gets less than 10% of the runtime - if
you do not leave room for the ask, you have made a commercial, not a
promo.

A 15-second cut cannot carry four acts properly. Say that to the user and
cut to three: hook, proof, offer. Better to do three honestly than four
badly.

## Every shot states its purpose

Each shot in the storyboard has a `purpose` field, and the validator
fails the build if it is empty. Write it as a sentence about the
argument, not about the animation.

Good: "Open on a hard claim about the viewer's problem so they stay."
Bad: "Show the text with a nice animation."

If you cannot write the purpose, you do not understand the shot yet, and
the shot probably should not exist. This one rule removes more filler
than any other editing technique.

## Hook patterns

The first three seconds decide whether there is a video at all. The
reference film does not open with a logo, an intro animation, or the
presenter saying hello. It opens on the claim.

Patterns that work:

- **The number.** A hard statistic as the hero numeral. "1500+ students"
  on a green gradient with rays behind it.
- **The false belief.** State what the viewer assumes, then undercut it.
  "MOST PEOPLE EDIT. VERY FEW GET HIRED."
- **The unfinished promise.** Show the result, then delay explaining how
  it is made.
- **The cost.** Open on what the problem is costing them, in their own
  words.

What does not work: logo stings, "hey guys welcome back", a slow fade
from black, or an establishing shot of the presenter that says nothing.
The reference film's first shot lands its claim in under two seconds.

Whatever the pattern, the hook has to be **complete** before 3 seconds -
not just started.

## Rhythm: punch, then rest

The single most measurable quality of the reference edit is that it
breathes. Its motion-energy timeline has clear dead zones (9-10 s, 15 s,
40-41 s, 49 s, 114-115 s, 130-133 s) between bursts of high energy
(3 s, 16 s, 23 s, 54 s, 56 s, 80 s, 95 s). The busiest segment scores
47.6 on the motion scale; the stillest scores 0.0 - a locked-off
photoreal living room shot. The film swings between those extremes on
purpose.

So: **a punch is followed by a rest.** A punch is a dense moment -
several elements arriving at once, a transition, a big number, a reveal.
A rest is a held frame, a talking head, a slow push. If a punch is
followed immediately by another punch, the audience stops registering
either one. This is why the validator warns when no rest follows a
punch within three shots.

Practical targets:

- A punch at least every 25-35 seconds.
- A rest within 10 seconds after each punch.
- No shot longer than 6 seconds on a single idea.
- Average shot length 1.5-2.5 seconds. The reference film averages 1.81 s.

## The talk:graphics ratio

Pure talking head is a podcast. Pure graphics with no face is a
corporate deck. The reference film is about 60% graphics, and the
talking head appears exactly where a person is needed: to make a point
land on a human being.

The validator warns below 25% graphics. In practice:

- **Graphics carry facts.** Numbers, comparisons, lists, features,
  before-and-afters, product UI.
- **The face carries emotion.** The problem statement, the personal
  credibility, the invitation.

A rule of thumb for a 60-second video: at least three graphics shots
carry a *number*, and the face is on screen for the problem and the ask.

## Closing: one ask, said out loud

The reference film ends with a title card, a URL, and the word
**Enroll** - and the voiceover says it too. On screen and in the audio.

Decide before you write the storyboard: what is the one thing the viewer
should do? Not three. One. Then:

- Put it on screen in the last 15% of the runtime (`"cta": true`).
- Say it in the voiceover.
- Give the friction-reducer next to it: a deadline, a guarantee, a
  "no card needed", a start time.
- Show where to go: a URL bar, a handle, a phone number.

If the video ends without an ask, it is a brand film and will not sell
anything. If it ends with three asks, the viewer will do none of them.

## Colour as meaning

The reference film uses colour semantically, and the audience absorbs it
without being told:

| Colour | Means | Used for |
|---|---|---|
| Azure / electric blue | the positive path | the thing being sold |
| Green | money, proof, success | earnings, student counts, growth |
| Lime | a service tier, a module | what is included |
| Red | the anti-pattern | the mistake, the wrong tool |
| Magenta | the second option | a lesser package |
| Periwinkle | colour grading | a service category |
| Navy glass | the product | UI frames, panels |
| White | honesty, cleanliness | type, clean claims |

Keep this consistent for the whole film. A green pill that means
"success" in the hook and "the wrong choice" in the offer destroys the
audience's trust in the colour, and therefore in the argument.

## The validator's rules

These are enforced in `scripts/validate_storyboard.py` and will refuse the
build. Read them as a spec, not as bureaucracy.

**Errors (build refused):**

- A shot with no `purpose`.
- The first shot longer than 3 s (the hook must land).
- Fewer than 3 declared acts, or a shot referencing an undeclared act.
- A layer with an unknown type, or an asset file that does not exist.
- A shot with a non-positive duration.

**Warnings (build allowed, read them):**

- More than 3 consecutive shots of the same visual mode.
- Fewer than 25% graphics shots.
- No `punch` marked in a video longer than 40 s.
- A punch with no rest after it.
- No `cta` in the closing stretch.
- Speech outside 1.7-3.3 words per second.
- A shot longer than 6 s.

Warnings are where the video is about to become forgettable rather than
broken. Fix the ones that matter for this particular video; ignore the
ones that do not apply.

## A worked example

The reference film's first thirty seconds, reconstructed as a storyboard
shape:

```
act hook      0.0-6.0   "Video editing has the highest demand right now."
                          s01 graphics  number/counter, rays, punch
                          s02 b-roll    the volume of content, fast montage
act problem  6.0-22.0   "Here is the mistake most people make."
                          s03 talking-head   the presenter names it
                          s04 graphics       red pill: the wrong path
                          s05 graphics       what that costs them
act proof    22.0-45.0  "I trained more than 1500 people."
                          s06 talking-head   name and background
                          s07 graphics       1500+ hero numeral, green
                          s08 graphics       money, reach, colour grading
act offer    45.0-60.0  "22 classes, 24 hours of support, a mentor."
                          s09 graphics       the offer, three facts
                          s10 graphics       enrol, URL, title card, cta
```

Ten shots, four acts, one idea per shot, one ask at the end.

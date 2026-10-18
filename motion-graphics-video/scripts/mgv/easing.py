"""Easing functions.

Every animation in the storyboard is driven by a normalised progress value
0..1. These curves are what separate a "slide" from a "slide that feels
expensive": a linear move reads as mechanical, a decelerating move reads as
physical. The defaults here are chosen to match the motion grammar measured
in the reference film, where entrances decelerate hard and exits accelerate
away.
"""
import math


def linear(t):
    return t


def ease_out(t):
    """Decelerate fast -> slow. The default for entrances."""
    return 1.0 - (1.0 - t) ** 3


def ease_in(t):
    """Accelerate slow -> fast. The default for exits."""
    return t ** 3


def ease_in_out(t):
    return 4 * t ** 3 if t < 0.5 else 1 - ((-2 * t + 2) ** 3) / 2


def ease_out_back(t, overshoot=1.70158):
    """Overshoot past the target and settle back. Used for 'pop' entrances."""
    c3 = overshoot + 1
    return 1 + c3 * (t - 1) ** 3 + overshoot * (t - 1) ** 2


def ease_out_elastic(t, period=0.36):
    if t <= 0:
        return 0.0
    if t >= 1:
        return 1.0
    c4 = 2 * math.pi / period
    return 2 ** (-9 * t) * math.sin((t * 10 - 0.75) * c4) + 1


def ease_out_bounce(t):
    n1, d1 = 7.5625, 2.75
    if t < 1 / d1:
        return n1 * t * t
    if t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    if t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    t -= 2.625 / d1
    return n1 * t * t + 0.984375


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def expo_out(t):
    return 1.0 if t >= 1 else 1 - 2 ** (-10 * t)


EASINGS = {
    "linear": linear,
    "ease": ease_in_out,
    "ease_out": ease_out,
    "ease_in": ease_in,
    "ease_in_out": ease_in_out,
    "back": ease_out_back,
    "elastic": ease_out_elastic,
    "bounce": ease_out_bounce,
    "smooth": smoothstep,
    "expo": expo_out,
}


def get(name):
    """Resolve an easing name; unknown names fall back to ease_out so a typo
    degrades to something reasonable instead of crashing a long render."""
    return EASINGS.get(name, ease_out)

#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import time
from enum import IntEnum
from pathlib import Path
from typing import List, Tuple, Type

import PIL.Image  # type: ignore
import PIL.ImageDraw  # type: ignore
import PIL.ImageFont  # type: ignore
from app import HEART_RATE_PATH

MONO_FONT = PIL.ImageFont.truetype(
    'SourceCodePro-Medium.ttf', 96, encoding="unic")

FONT_STROKE_W = 2

FONT_SIZES = [
    MONO_FONT.getsize('0', stroke_width=FONT_STROKE_W),
    MONO_FONT.getsize('00', stroke_width=FONT_STROKE_W),
    MONO_FONT.getsize('000', stroke_width=FONT_STROKE_W),
]

CURRENT_SCALE_PATH = Path('current_scale.txt')

STATE_VAL_TO_ANGLE_RANGE: List[Tuple[int, int]] = [
    (-120, -105),  # 0
    (-105, -60),  # 1
    (-60, -15),  # 2
    (-15, 30),  # 3
    (30, 75),  # 4
    (75, 120),  # 5
    (-135, -120),  # -1
]


class ScaleState(IntEnum):
    Unknown = -1
    Relaxed = 0
    WarmUp = 1
    Intensive = 2
    Aerobic = 3
    Anaerobic = 4
    MaxVO2 = 5


def read_rate() -> Tuple[int, float]:
    if not HEART_RATE_PATH.exists():
        return 0, 1024.0
    rate = 0
    age = 1024.0
    while True:
        try:
            rate = int(HEART_RATE_PATH.read_text('utf-8'))
            age = max(0.0, time.time() -
                      HEART_RATE_PATH.stat(follow_symlinks=True).st_mtime)
            break
        except Exception:
            time.sleep(0.1)
    return rate, age


class ScaleAbstract:
    def __init__(self, hr: int, ma: float) -> None:
        self.hr = hr
        self.ma = ma

    RANK_DEFS: List[Tuple[int, int, ScaleState]] = []

    def rank(self) -> Tuple[ScaleState, float]:
        if self.ma > 15:
            return ScaleState.Unknown, 0.0
        s = self.hr
        e = s + 1
        r = ScaleState.Unknown
        c = -1
        for s, e, r in type(self).RANK_DEFS:
            c += 1
            if self.hr >= s and self.hr < e:
                break
        return r, c + max(0.0, min(0.99999, (self.hr - s) / (e - s)))


class ScaleRelax(ScaleAbstract):
    RANK_DEFS = [(0, 40, ScaleState.Unknown),
                 (40, 55, ScaleState.Relaxed),
                 (55, 70, ScaleState.WarmUp),
                 (70, 85, ScaleState.Intensive),
                 (85, 100, ScaleState.Aerobic),
                 (100, 115, ScaleState.Anaerobic),
                 (115, 130, ScaleState.MaxVO2),
                 ]


class ScaleIntensive(ScaleAbstract):

    RANK_DEFS = [(0, 40, ScaleState.Unknown),
                 (40, 97, ScaleState.Relaxed),
                 (97, 117, ScaleState.WarmUp),
                 (117, 136, ScaleState.Intensive),
                 (136, 156, ScaleState.Aerobic),
                 (156, 175, ScaleState.Anaerobic),
                 (175, 195, ScaleState.MaxVO2),
                 ]


def set_profile(tp: Type[ScaleAbstract]) -> str:
    nm = tp.__name__
    while True:
        try:
            CURRENT_SCALE_PATH.write_text(nm, 'utf-8')
            break
        except Exception:
            time.sleep(0.1)
    return nm


def get_profile() -> Type[ScaleAbstract]:
    if not CURRENT_SCALE_PATH.exists():
        set_profile(ScaleIntensive)
    while True:
        try:
            return globals()[CURRENT_SCALE_PATH.read_text('utf-8')]
        except Exception:
            time.sleep(0.1)


def update_chart(profile: ScaleAbstract):
    rank, vumeter = profile.rank()
    sdeg, edeg = STATE_VAL_TO_ANGLE_RANGE[rank.value]
    rdeg = -(((edeg - sdeg) * (vumeter % 1)) + sdeg)
    canvas = PIL.Image.open('vuMeter_empty.png')
    bkg0 = PIL.Image.open('vuMeter_zones.png')
    bkg1 = PIL.Image.open(f'vuMeter_emph{rank.value}.png')
    spr0 = PIL.Image.open('vuMeter_nail.png')
    ovr0 = PIL.Image.open('vuMeter_heart.png')
    sprr = spr0.rotate(rdeg)
    canvas.paste(bkg0, (0, 0), bkg0)
    canvas.paste(bkg1, (0, 0), bkg1)
    canvas.paste(sprr, (0, 0), sprr)
    draw = PIL.ImageDraw.Draw(canvas)
    font_box = FONT_SIZES[len(str(profile.hr)) - 1]
    text_box = (
        int(canvas.size[0] / 2 - font_box[0] / 2),
        int(canvas.size[1] - font_box[1] - canvas.size[1] * .1),
    )
    draw.text(text_box, f'{profile.hr}', (0, 0, 0), MONO_FONT,
              stroke_width=FONT_STROKE_W, stroke_fill=(255, 255, 255))
    canvas.paste(ovr0, (0, 0), ovr0)
    canvas.save('vuMeter_rendered-png', 'png', optimize=True, compress_level=0)
    while True:
        try:
            Path('vuMeter_rendered.png').write_bytes(
                Path('vuMeter_rendered-png').read_bytes())
            break
        except Exception:
            time.sleep(0.1)
    Path('vuMeter_rendered-png').unlink()
    print(rank, vumeter, profile.hr, profile.ma)


def main():
    last_age: float = 1 << 31
    while 1:
        profile = get_profile()(*read_rate())
        if last_age > profile.ma:
            update_chart(profile)
        last_age = profile.ma
        time.sleep(0.2)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import time
from pathlib import Path

from flask import Flask, request

HEART_RATE_PATH = Path('heart_rate.txt')
if not HEART_RATE_PATH.exists():
    HEART_RATE_PATH.write_text('0', 'utf-8')

app = Flask(__name__)


def int_or(v, d: int) -> int:
    try:
        return int(v)
    except Exception:
        return d


@app.route('/hr', methods=['HEAD', 'OPTIONS', 'GET', 'POST'])
def heart_rate():
    raw_rate = (request.form
                if request.method == 'POST' else
                request.args
                ).get('rate', '').strip()
    rate = int_or(raw_rate, 0)
    if 0 < rate <= 999:
        while True:
            try:
                HEART_RATE_PATH.write_text(f'{rate:3}', 'utf-8')
                break
            except Exception:
                time.sleep(0.1)
    print(
        f'Received {request.method} with {rate=} and {raw_rate=} ' +
        f'at {time.time()}')
    return ''

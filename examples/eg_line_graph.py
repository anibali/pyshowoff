#!/usr/bin/env python3

import pyshowoff
from examples.helpers import get_showoff_credentials

from time import sleep
import random


url, key_id, secret_key = get_showoff_credentials()

client = pyshowoff.Client(url, key_id, secret_key)

notebook = client.add_notebook('Example: Line graph').result()
notebook.add_tag('example').result()

frame = notebook.add_frame('Time-varying graph').result()

xs = []
y1s = []
y2s = []

random.seed(12345)
for i in range(50):
    sleep(1)
    xs.append(i)
    y1s.append(random.gauss(0.0, 1.0))
    y2s.append(random.gauss(0.5, 1.0))
    frame.line_graph(
        xs, [y1s, y2s],
        series_names=['y1', 'y2'],
        x_title='Time (seconds)',
        y_title='Value',
    )

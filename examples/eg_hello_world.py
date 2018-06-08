#!/usr/bin/env python3

import pyshowoff
from examples.helpers import get_showoff_credentials


url, key_id, secret_key = get_showoff_credentials()

client = pyshowoff.Client(url, key_id, secret_key)

notebook = client.add_notebook('Example: Hello world').result()
notebook.add_tag('example').result()

frame = notebook.add_frame('My frame').result()
frame.text('Hello world!')

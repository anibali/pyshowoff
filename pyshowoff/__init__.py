import requests
import json
from requests_futures.sessions import FuturesSession

from .promise import Promise


class Client:
    def __init__(self, base_url, disable_async=False):
        self.base_url = base_url
        if disable_async:
            self.session = requests.Session()
        else:
            self.session = FuturesSession()
        self.session.headers.update({
            'content-type': 'application/json'
        })

    def request(self, method, path, data=None):
        if data is not None:
            data = json.dumps(data)
        res = self.session.request(method, self.base_url + path, data=data)
        return Promise.resolve(res)

    def add_notebook(self, title):
        data = {
            'data': {
                'type': 'notebooks',
                'attributes': {'title': title},
            },
        }
        promise = self.request('post', '/api/v2/notebooks', data)
        return promise.then(lambda res: Notebook(self, res.json()['data']['id']))


class Notebook:
    def __init__(self, client, notebook_id):
        self.client = client
        self.id = notebook_id

    def update(self, title=None, pinned=None, progress=None):
        """Updates the attributes of this notebook.

        Args:
            title (str): Notebook title
            pinned (bool): Set to True to protect notebook against deletion
            progress (float): Notebook progress (from 0.0 to 1.0)
        """

        attrs = {}
        if title is not None:
            attrs['title'] = title
        if pinned is not None:
            attrs['pinned'] = pinned
        if progress is not None:
            attrs['progress'] = progress
        data = {
            'data': {
                'id': self.id,
                'type': 'notebooks',
                'attributes': attrs,
            },
        }
        self.client.request('patch', '/api/v2/notebooks/' + self.id, data)

    def set_title(self, title):
        self.update(title=title)

    def set_pinned(self, pinned):
        self.update(pinned=pinned)

    def set_progress(self, progress):
        self.update(progress=progress)

    def add_tag(self, name):
        data = {
            'data': {
                'type': 'tags',
                'attributes': {'name': name},
                'relationships': {
                    'notebook': {
                        'data': {'type': 'notebooks', 'id': self.id},
                    },
                },
            },
        }
        promise = self.client.request('post', '/api/v2/tags', data)
        return promise.then(lambda res: Tag(self, res.json()['data']['id']))

    def add_frame(self, title, bounds=None):
        data = {
            'data': {
                'type': 'frames',
                'attributes': {'title': title},
                'relationships': {
                    'notebook': {
                        'data': {'type': 'notebooks', 'id': self.id},
                    },
                },
            },
        }
        if bounds is not None:
            data['data']['attributes'].update(bounds)
        promise = self.client.request('post', '/api/v2/frames', data)
        return promise.then(lambda res: Frame(self, res.json()['data']['id']))


class Tag:
    def __init__(self, client, tag_id):
        self.client = client
        self.id = tag_id


class Frame:
    def __init__(self, client, frame_id):
        self.client = client
        self.id = frame_id

    def update(self, title=None, type=None, content_body=None):
        attrs = {}
        if title is not None:
            attrs['title'] = title
        if type is not None:
            attrs['type'] = type
        if content_body is not None:
            attrs['content'] = {'body': content_body}
        data = {
            'data': {
                'id': self.id,
                'type': 'frames',
                'attributes': attrs,
            },
        }
        self.client.request('patch', '/api/v2/frames/' + self.id, data)

    def set_title(self, title):
        self.update(title=title)

    def set_content(self, type, content_body):
        self.update(type=type, content_body=content_body)

    def vega(self, spec):
        self.set_content('vega', spec)

    def vegalite(self, spec):
        self.set_content('vegalite', spec)

    def text(self, message):
        self.set_content('text', message)

    def html(self, html):
        self.set_content('html', html)

    def progress(self, current_value, max_value):
        percentage = min(100 * current_value / max_value, 100)
        html = """<div class="progress">
            <div class="progress-bar" role="progressbar"
             aria-valuenow="{percentage:0.2f}" aria-valuemin="0" aria-valuemax="100"
             style="width: {percentage:0.2f}%; min-width: 40px;"
            >
                {percentage:0.2f}%
            </div>
        </div>""".format(percentage=percentage)
        self.html(html)

    def line_graph(self, xss, yss, series_names=None, x_title=None, y_title=None,
                   y_axis_min=None, y_axis_max=None):
        if not isinstance(xss[0], list):
            xss = [xss] * len(yss)

        show_legend = True
        if series_names is None:
            show_legend = False
            series_names = ['series_{:03d}'.format(i) for i in range(len(xss))]

        min_x = float('inf')
        max_x = -float('inf')
        min_y = float('inf')
        max_y = -float('inf')
        tables = []
        marks = []
        for i, xs in enumerate(xss):
            marks.append({
                'type': 'line',
                'from': {'data': 'table_{:03d}'.format(i)},
                'properties': {
                    'enter': {
                        'x': {'scale': 'x', 'field': 'x'},
                        'y': {'scale': 'y', 'field': 'y'},
                        'stroke': {'scale': 'c', 'value': series_names[i]},
                    }
                },
            })

            points = []
            for j, x in enumerate(xs):
                y = yss[i][j]
                min_x = min(x, min_x)
                max_x = max(x, max_x)
                min_y = min(y, min_y)
                max_y = max(y, max_y)
                points.append({'x': x, 'y': y})
            tables.append(points)

        data = []
        for i, table in enumerate(tables):
            data.append({
                'name': 'table_{:03d}'.format(i),
                'values': table
            })

        spec = {
            'width': 370,
            'height': 250,
            'data': data,
            'scales': [
                {
                    'name': 'x',
                    'type': 'linear',
                    'range': 'width',
                    'domainMin': min_x,
                    'domainMax': max_x,
                    'nice': True,
                    'zero': False,
                }, {
                    'name': 'y',
                    'type': 'linear',
                    'range': 'height',
                    'domainMin': y_axis_min or min_y,
                    'domainMax': y_axis_max or max_y,
                    'nice': True,
                    'zero': False,
                }, {
                    'name': 'c',
                    'type': 'ordinal',
                    'range': 'category10',
                    'domain': series_names,
                }
            ],
            'axes': [
                {'type': 'x', 'scale': 'x', 'title': x_title},
                {'type': 'y', 'scale': 'y', 'title': y_title, 'grid': True},
            ],
            'marks': marks,
        }

        if show_legend:
            spec['legends'] = [{'fill': 'c'}]

        self.vega(spec)

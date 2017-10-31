import unittest
from unittest.mock import patch
import httpretty
import json

from pyshowoff import Client, Notebook


class TestClient(unittest.TestCase):
    @httpretty.activate
    def test_request(self):
        body = {'test': 'test response'}
        httpretty.register_uri(httpretty.GET, "http://hostname:616/api/v2/notebooks",
                               body=json.dumps(body),
                               content_type="application/json")
        client = Client('http://hostname:616')
        res = client.request('get', '/api/v2/notebooks')
        self.assertEqual(res.result(1).json(), body)

    @httpretty.activate
    def test_request_with_disabled_async(self):
        body = {'test': 'test response'}
        httpretty.register_uri(httpretty.GET, "http://hostname:616/api/v2/notebooks",
                               body=json.dumps(body),
                               content_type="application/json")
        client = Client('http://hostname:616', disable_async=True)
        with patch.object(client, 'request', wraps=client.request) as mock_request:
            res = client.request('get', '/api/v2/notebooks')
            mock_request.assert_called()
            self.assertEqual(res.result(1).json(), body)

    @httpretty.activate
    def test_add_notebook(self):
        res_body = {
            'data': {
                'type': 'notebooks',
                'id': '42',
                'attributes': {'title': 'New notebook'}
            }
        }
        httpretty.register_uri(httpretty.POST, "http://hostname:616/api/v2/notebooks",
                               body=json.dumps(res_body),
                               content_type="application/json")
        client = Client('http://hostname:616')
        future = client.add_notebook('New notebook')
        notebook = future.result(1)
        req_body = json.loads(httpretty.last_request().body)
        self.assertEqual(req_body, {
            'data': {
                'type': 'notebooks',
                'attributes': {'title': 'New notebook'}
            }
        })
        self.assertEqual(notebook.id, '42')


class TestNotebook(unittest.TestCase):
    @httpretty.activate
    def test_add_frame(self):
        res_body = {
            'data': {
                'type': 'frames',
                'id': '12',
                'attributes': {'title': 'New frame'}
            }
        }
        httpretty.register_uri(httpretty.POST, "http://hostname:616/api/v2/frames",
                               body=json.dumps(res_body),
                               content_type="application/json")

        client = Client('http://hostname:616')
        notebook = Notebook(client, '42')

        frame = notebook.add_frame('New frame').result()
        self.assertEqual(frame.id, '12')
        self.assertEqual(frame.client, client)

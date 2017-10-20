import unittest
from unittest.mock import patch

from pyshowoff import Client


class TestClient(unittest.TestCase):
    def test_request(self):
        client = Client('hostname:616')
        with patch('requests.Session.send') as mock_send:
            client.request('get', '/api/v2/notebooks')
            req = mock_send.call_args[0][0]
            self.assertEqual(req.method, 'GET')
            self.assertEqual(req.url, 'http://hostname:616/api/v2/notebooks')

    def test_new_notebook(self):
        client = Client('hostname:616')
        with patch('pyshowoff.Client.request') as mock_request:
            client.new_notebook('New notebook')
            method, path, data = mock_request.call_args[0]
            self.assertEqual(method, 'post')
            self.assertEqual(path, '/api/v2/notebooks')
            self.assertEqual(data, {
                'data': {
                    'type': 'notebooks',
                    'attributes': {'title': 'New notebook'}
                }
            })

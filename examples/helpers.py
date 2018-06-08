from os import environ


def get_showoff_credentials():
    url = environ.get('SHOWOFF_URL')
    key_id = environ.get('SHOWOFF_KEY_ID')
    secret_key = environ.get('SHOWOFF_SECRET_KEY')
    assert url, 'SHOWOFF_URL not set'
    assert key_id, 'SHOWOFF_KEY_ID not set'
    assert secret_key, 'SHOWOFF_SECRET_KEY not set'
    return url, key_id, secret_key

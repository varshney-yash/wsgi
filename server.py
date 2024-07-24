from io import StringIO

def parse_http(http):
    request, *headers, _, body = http.split('\r\n')
    method, path, protocol = request.split(' ')
    headers = dict(
        line.split(': ', 1)
        for line in headers
    )
    return method, path, protocol, headers, body

def format_headers(headers):
    env = {}
    for header, value in headers.items():
        key = 'HTTP_' + header.upper().replace('-', '_')
        env[key] = value
    return env

def to_environ(method, path, protocol, headers, body, addr):
    return {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'SERVER_PROTOCOL': protocol,
        'wsgi.input': StringIO(body),
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'http',
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '8000',
        'REMOTE_ADDR': addr[0],
        **format_headers(headers),
    }

def start_response(status, headers):
    response_headers = [f'{k}: {v}' for k, v in headers]
    return f'HTTP/1.1 {status}\r\n' + '\r\n'.join(response_headers) + '\r\n\r\n'

def application(environ, start_response):
    response = view(environ)
    response_headers = [
        ('Content-Type', 'text/plain'),
        ('Content-Length', str(len(response)))
    ]
    start_response('200 OK', response_headers)
    return [response.encode('utf-8')]

def view(environ):
    path = environ['PATH_INFO']
    return f'Hello from {path}'

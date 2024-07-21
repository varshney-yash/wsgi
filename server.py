import socket
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
    start_response_output = start_response('200 OK', response_headers)
    return [start_response_output.encode('utf-8'), response.encode('utf-8')]

def view(environ):
    path = environ['PATH_INFO']
    return f'Hello from {path}'

def run_server(host, port, application):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(1)
        print(f"Serving on {host}:{port}...")

        while True:
            conn, addr = s.accept()
            with conn:
                try:
                    http_request = conn.recv(1024).decode('utf-8')
                    method, path, protocol, headers, body = parse_http(http_request)
                    environ = to_environ(method, path, protocol, headers, body, addr)
                    response = application(environ, start_response)
                    for data in response:
                        conn.sendall(data)
                except Exception as e:
                    print(f"Error: {e}")
                    conn.sendall(b'HTTP/1.1 500 Internal Server Error\r\n\r\n')

if __name__ == "__main__":
    run_server('localhost', 8000, application)
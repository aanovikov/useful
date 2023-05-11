import os
import subprocess
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

class CustomRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if 'login' in self.headers and self.headers['login'].lower() == 'true':
            self.login()
        elif 'logout' in self.headers and self.headers['logout'].lower() == 'true':
            self.logout()
        else:
            self.send_error(401, 'Unauthorized.')
    
    def login(self):
        if 'login' in self.headers and self.headers['login'].lower() == 'true':
            url = urllib.parse.urlparse(self.path)
            if url.path == '/auto-login':
                query_params = urllib.parse.parse_qs(url.query)
                id = query_params.get('id', [None])[0]
                pin = query_params.get('pin', [None])[0]

                if id and pin:
                    id = urllib.parse.unquote(id)
                    pin = urllib.parse.unquote(pin)

                    script_path = os.path.expanduser('~/auto/login-470.sh')
                    subprocess.run(['bash', '-c', f'source /root/.bash_profile; {script_path} {id} {pin}'])

                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'Login script executed successfully.')
                else:
                    self.send_error(400, 'Missing parameters.')
            else:
                self.send_error(404, 'Not found.')
        else:
            self.send_error(401, 'Unauthorized.')
    def logout(self):
        if 'logout' in self.headers and self.headers['logout'].lower() == 'true':
            url = urllib.parse.urlparse(self.path)
            if url.path == '/auto-login':
                query_params = urllib.parse.parse_qs(url.query)
                id = query_params.get('id', [None])[0]
                
                if id:
                    id = urllib.parse.unquote(id)
                    
                    script_path = os.path.expanduser('~/auto/logout-470.sh')
                    subprocess.run(['bash', '-c', f'source /root/.bash_profile; {script_path} {id}'])

                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'Logout script executed successfully.')
                else:
                    self.send_error(400, 'Missing parameters.')
            else:
                self.send_error(404, 'Not found.')
        else:
            self.send_error(401, 'Unauthorized.')
        

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass

if __name__ == '__main__':
    # Replace 'vpn_interface_ip' with the IP address of your VPN interface.
    server_address = ('10.8.0.4', 8000)
    httpd = ThreadingHTTPServer(server_address, CustomRequestHandler)
    print('Server running on http://{}:{}'.format(*server_address))
    httpd.serve_forever()
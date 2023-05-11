import subprocess
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
class RequestHandler(BaseHTTPRequestHandler):

    def __init__(self, request, address, server, proc):
        self.proc = proc
        super().__init__(request, address, server)

    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if self.headers.get('import') == 'true':
            try:
                subprocess.Popen('expect -f /root/web/import.exp > /root/web/status.txt', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'Import command executed successfully')
            except subprocess.CalledProcessError as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(bytes(f'Error executing import command: {str(e)}', 'utf-8'))
        elif self.headers.get('status') == 'true':
            try:
                with open('/root/web/status.txt', 'r') as f:
                    data = f.read()
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(bytes(data, 'utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(bytes(f'Error getting status: {str(e)}', 'utf-8'))
        elif self.headers.get('done') == 'true':
            try:
                with open('/root/web/done.txt', 'w') as f:
                    f.write('done')
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'Init command executed successfully')
            except subprocess.CalledProcessError as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(bytes(f'Error executing init command: {str(e)}', 'utf-8'))
        elif 'text' in params:
            text = params['text'][0]
            if not os.path.exists('/root/web/phrase.txt'):
                open('/root/web/phrase.txt', 'w').close()
            with open('/root/web/phrase.txt', 'w') as f:
                f.write(text)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Phrase was written to file')
        elif self.headers.get('restart') == 'true':
            try:
                subprocess.run(['docker', 'restart', 'minima9001'])
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'docker restart command executed successfully')
            except subprocess.CalledProcessError as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(bytes(f'Error executing init command: {str(e)}', 'utf-8'))
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid request')

def get_unique_ip():
    cmd = "ip addr | grep 'inet 10.8.0' | awk '{print $2}' | cut -d'/' -f1"
    result = subprocess.check_output(cmd, shell=True, text=True).strip()
    return result

def run():
    proc = subprocess.Popen('expect -f /root/web/expect.exp', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    ip = get_unique_ip()
    httpd = HTTPServer((ip, 5000), lambda request, address, server: RequestHandler(request, address, server, proc))
    print('Web server started')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
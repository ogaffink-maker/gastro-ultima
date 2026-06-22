import http.server
import socketserver
import os
import json

PORT = 8000
DIRECTORY = "."

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        if self.path == '/api/upload-image':
            try:
                # Read headers
                product_id = self.headers.get('x-product-id')
                file_ext = self.headers.get('x-file-extension', '.jpg')
                content_length = int(self.headers.get('Content-Length', 0))

                if not product_id or content_length == 0:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Missing product ID or file content'}).encode('utf-8'))
                    return

                # Normalise and validate extension
                if not file_ext.startswith('.'):
                    file_ext = '.' + file_ext
                if file_ext.lower() not in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
                    file_ext = '.jpg'

                # Read raw body binary data
                file_data = self.rfile.read(content_length)

                # Define save path
                new_filename = f"product_{product_id}{file_ext.lower()}"
                save_path = os.path.join("images", new_filename)

                # Write to file
                os.makedirs("images", exist_ok=True)
                with open(save_path, 'wb') as f:
                    f.write(file_data)

                # Update products.json
                json_path = "products.json"
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        products = json.load(f)

                    updated = False
                    for p in products:
                        if str(p['id']) == str(product_id):
                            p['image'] = f"./images/{new_filename}"
                            updated = True
                            break

                    if updated:
                        with open(json_path, 'w', encoding='utf-8') as f:
                            json.dump(products, f, ensure_ascii=False, indent=2)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                # Include a cache buster timestamp in response path
                timestamp = int(os.path.getmtime(save_path))
                self.wfile.write(json.dumps({
                    'success': True,
                    'imagePath': f"./images/{new_filename}?t={timestamp}"
                }).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))

        elif self.path == '/api/delete-product':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(content_length).decode('utf-8'))
                product_id = body.get('id')

                if product_id is None:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Missing product ID'}).encode('utf-8'))
                    return

                # Normalize to int for reliable comparison
                try:
                    product_id = int(product_id)
                except (ValueError, TypeError):
                    pass

                json_path = "products.json"
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        products = json.load(f)

                    original_len = len(products)
                    products = [p for p in products if int(p.get('id', -1)) != product_id]

                    if len(products) < original_len:
                        with open(json_path, 'w', encoding='utf-8') as f:
                            json.dump(products, f, ensure_ascii=False, indent=2)

                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
                    else:
                        self.send_response(404)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'error': 'Product not found'}).encode('utf-8'))
                else:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'products.json not found'}).encode('utf-8'))

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'x-product-id, x-file-extension, content-type')
        self.end_headers()

# To allow reusing the port immediately after stopping
socketserver.TCPServer.allow_reuse_address = True

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"Serving HTTP on http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server...")

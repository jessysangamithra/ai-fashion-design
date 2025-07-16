import http.server
import socketserver
import os
import cgi
from urllib.parse import parse_qs

PORT = 8000

class StyleMeHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path.startswith('/index.html'):
            self.path = '/index.html'
        elif self.path.startswith('/style.css'):
            self.path = '/style.css'
        elif self.path.startswith('/images/'):
            pass  # serve images
        else:
            self.path = '/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/recommend':
            self.handle_recommend()
        elif self.path == '/contact':
            self.handle_contact()
        else:
            self.send_error(404, 'File not found')

    def handle_recommend(self):
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
        if ctype == 'multipart/form-data':
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST'})
            occasion = form.getvalue('occasion', 'casual')
            weather = form.getvalue('weather', 'sunny')
            color = form.getvalue('color', 'blush')
            # Simulate AI logic
            suggestion, img_url, advice = get_suggestion(occasion, weather, color)
            # Render result page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'r', encoding='utf-8') as f:
                html = f.read()
            # Insert result card into results section
            result_html = f'''
            <div class="result-card">
                <img src="{img_url}" alt="Outfit Suggestion">
                <h3>{suggestion}</h3>
                <p>{advice}</p>
            </div>
            '''
            html = html.replace('<!-- Results will be rendered here by Python backend -->', result_html)
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_error(400, 'Bad request')

    def handle_contact(self):
        content_length = self.headers.get('content-length')
        if content_length is None:
            self.send_error(400, 'Content-Length header missing')
            return
        length = int(content_length)
        post_data = self.rfile.read(length).decode('utf-8')
        data = parse_qs(post_data)
        name = data.get('name', [''])[0]
        email = data.get('email', [''])[0]
        preference = data.get('preference', [''])[0]
        # Simulate storing or sending the contact info
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open('index.html', 'r', encoding='utf-8') as f:
            html = f.read()
        thank_you = f'<div class="result-card"><h3>Thank you, {name}!</h3><p>We have received your message and will get back to you soon.</p></div>'
        html = html.replace('<!-- Results will be rendered here by Python backend -->', thank_you)
        self.wfile.write(html.encode('utf-8'))

def get_suggestion(occasion, weather, color):
    # Simulated AI logic for outfit suggestions
    if occasion == 'formal':
        suggestion = 'Elegant Blazer & Trousers'
        img_url = 'https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=400&q=80'
        advice = 'Pair a pastel blazer with tailored trousers and a silk blouse for a chic formal look.'
    elif occasion == 'party':
        suggestion = 'Trendy Party Dress'
        img_url = 'https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=crop&w=400&q=80'
        advice = 'Opt for a flowy dress in your favorite pastel shade and accessorize with statement jewelry.'
    elif occasion == 'work':
        suggestion = 'Smart Workwear'
        img_url = 'https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?auto=format&fit=crop&w=400&q=80'
        advice = 'A soft blouse with a pencil skirt or tailored pants in cream or blush is perfect for the office.'
    else:
        suggestion = 'Casual Chic Outfit'
        img_url = 'https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?auto=format&fit=crop&w=400&q=80'
        advice = 'Try a comfy pastel sweater with jeans or a skirt for a relaxed, stylish vibe.'
    # Weather and color tweaks
    if weather == 'cold':
        advice += ' Add a cozy pastel coat or scarf for warmth.'
    elif weather == 'hot':
        advice += ' Choose light, breathable fabrics.'
    if color == 'lavender':
        advice += ' Lavender accessories will make your look pop!'
    elif color == 'cream':
        advice += ' Cream tones add elegance and softness.'
    elif color == 'babyblue':
        advice += ' Baby blue is perfect for a fresh, modern feel.'
    return suggestion, img_url, advice

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with socketserver.TCPServer(("", PORT), StyleMeHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        httpd.serve_forever() 
from flask import Flask, render_template, request, redirect
import sqlite3
import random
import string

app = Flask(__name__, template_folder='templates')

# 데이터베이스 연결 및 테이블 생성
def get_db_connection():
    conn = sqlite3.connect('urls.db')
    return conn

# URL을 짧게 만들기 위한 함수
def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for i in range(6))
    return short_url

# 홈페이지
@app.route('/')
def index():
    return render_template('index.html')

# 단축 URL 생성
@app.route('/shorten', methods=['POST'])
def shorten():
    original_url = request.form.get('original_url')

    # 이미 짧은 URL이 있는지 확인
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT short_url FROM url_mapping WHERE original_url = ?', (original_url,))
    existing_short_url = cursor.fetchone()
    if existing_short_url:
        conn.close()
        return render_template('index.html', short_url=existing_short_url[0])

    # 짧은 URL 생성 및 저장
    short_url = generate_short_url()
    cursor.execute('INSERT INTO url_mapping (original_url, short_url) VALUES (?, ?)', (original_url, short_url))
    conn.commit()
    conn.close()

    return render_template('index.html', short_url=short_url)

# 짧은 URL 리다이렉션
@app.route('/<short_url>')
def redirect_to_original(short_url):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT original_url FROM url_mapping WHERE short_url = ?', (short_url,))
    original_url = cursor.fetchone()
    conn.close()
    if original_url:
        return redirect(original_url[0])
    else:
        return "URL not found."

if __name__ == '__main__':
    app.run(debug=True, threaded=True)

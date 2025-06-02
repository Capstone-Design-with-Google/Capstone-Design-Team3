import json, os, sqlite3
#새로 추가한 부분
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
from dotenv import load_dotenv
load_dotenv()  # .env 파일을 자동으로 읽어서 환경변수로 등록
from flask import Flask, redirect, request, url_for, jsonify
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask import send_from_directory
from flask import send_file
from oauthlib.oauth2 import WebApplicationClient
import requests
import traceback  # 파일 상단에 추가
from db import init_db_command
from user import User
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import run_ai_shorts_generator
from flask import url_for

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "구글_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "구글_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

app = Flask(
    __name__,
    static_url_path='/videos',
    static_folder=os.path.join(BASE_DIR, 'output', 'videos')
)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

login_manager = LoginManager()
login_manager.init_app(app)

from flask_cors import CORS
CORS(app, supports_credentials=True, origins=[
    "http://localhost:3000",
    "http://localhost:5000"
])

@login_manager.unauthorized_handler
def unauthorized():
    return "You must be logged in to access this content.", 403

client = WebApplicationClient(GOOGLE_CLIENT_ID)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route("/login")
def login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/login/callback")
def callback():
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    user = User(id_=unique_id, name=users_name, email=users_email, profile_pic=picture)
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)
    login_user(user)
    # 로그인 후 프론트엔드로 리다이렉트
    return redirect("http://localhost:3000/oauth-redirect")
    # 또는 Codespaces에서 프론트도 돌린다면 그 주소로!

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/api/user")
@login_required
def api_user():
    return jsonify({
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "profile_pic": current_user.profile_pic
    })

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

# [여기 아래에 추가하세요]
@app.route('/api/receive-url', methods=['POST'])
@login_required
def receive_url():
    data = request.get_json()
    print("✅ 받은 데이터:", data)

    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        print(f"🎯 URL 수신됨: {url}")
        video_path = run_ai_shorts_generator(url)
        print(f"🎬 생성된 비디오 경로: {video_path}")

        if video_path:
            video_filename = os.path.basename(video_path)
            video_url = f"/videos/{video_filename}"
            print(f"🌐 반환할 videoUrl: {video_url}")
            return jsonify({'videoUrl': video_url})
        else:
            print("⚠️ run_ai_shorts_generator가 None 반환")
            return jsonify({'error': '영상 생성에 실패했습니다.'}), 500
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# output/videos 폴더 경로
VIDEO_FOLDER = os.path.join(os.path.dirname(__file__), 'output', 'videos')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
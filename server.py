import http.server
import json
import os
import socketserver
import sys
import webbrowser
from pathlib import Path

# Windows 콘솔 utf-8 인코딩 대응
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# api/generate 모듈 가져오기
sys.path.insert(0, str(Path(__file__).resolve().parent))
from api.generate import generate_with_gemini, load_env_if_needed

PORT = 8000
DIRECTORY = Path(__file__).resolve().parent

class LocalAppHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def do_POST(self):
        if self.path == "/api/generate":
            load_env_if_needed()
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")

            try:
                data = json.loads(body)
                job = data.get("job", "").strip()
                experience = data.get("experience", "").strip()
                strength = data.get("strength", "").strip()

                if not job or not experience or not strength:
                    self._send_json({"error": "지원 직무, 경험, 강점을 모두 입력해주세요."}, status=400)
                    return

                api_key = os.environ.get("GEMINI_API_KEY")
                if not api_key or api_key == "여기에_키_입력":
                    self._send_json({
                        "error": "GEMINI_API_KEY가 설정되지 않았습니다. .env 파일에 올바른 API 키를 등록해주세요."
                    }, status=500)
                    return

                prompt = f"""
당신은 대기업 및 공기업 취업 자기소개서 전문 컨설턴트입니다.
제공된 정보를 바탕으로 설득력 있고 완성도 높은 자기소개서 '지원 동기 및 직무 역량' 문단을 작성해 주세요.

[지원자 입력 정보]
- 지원 직무: {job}
- 주요 경험 및 활동: {experience}
- 핵심 강점 및 역량: {strength}

[작성 가이드라인]
1. 분량: 공백 포함 450~600자 내외의 1~2개 완성된 단락으로 작성하세요.
2. 구조: 두괄식으로 직무에 대한 관심과 포부를 시작하고, 경험 속에서 발휘된 강점을 구체적으로 연결하세요.
3. 어조: 정중하고 자신감 넘치는 비즈니스 서술체(~했습니다, ~하고자 합니다)를 유지하세요.
4. 출력 형식: 부연 설명이나 인사말 없이 자기소개서 본문 텍스트만 출력하세요.
"""
                result_text = generate_with_gemini(api_key, prompt)
                self._send_json({"result": result_text}, status=200)

            except Exception as e:
                self._send_json({"error": f"서버 오류가 발생했습니다: {str(e)}"}, status=500)
        else:
            self.send_error(404, "Endpoint not found")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def _send_json(self, data, status=200):
        response_body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

def run():
    load_env_if_needed()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[!] 경고: .env 파일에 GEMINI_API_KEY가 없습니다. 문장 생성 시 오류가 발생할 수 있습니다.")
    else:
        print("[OK] GEMINI_API_KEY 로드 완료!")

    port = PORT
    server = None
    for attempt in range(5):
        try:
            socketserver.TCPServer.allow_reuse_address = True
            server = socketserver.TCPServer(("", port), LocalAppHandler)
            break
        except OSError:
            port += 1

    if not server:
        print("[ERROR] 사용 가능한 포트를 찾지 못했습니다.")
        return

    url = f"http://localhost:{port}"
    print("=" * 60)
    print(f"[START] 자소서 메이트 로컬 서버가 시작되었습니다!")
    print(f"[URL] 접속 주소: {url}")
    print(f"[INFO] 종료하려면 콘솔 창을 닫거나 Ctrl + C 를 누르세요.")
    print("=" * 60)

    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[STOP] 서버를 종료합니다.")
        server.server_close()

if __name__ == "__main__":
    run()

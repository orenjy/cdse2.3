import json
import os
from http.server import BaseHTTPRequestHandler
from pathlib import Path

# 로컬 개발 시 .env 파일 수동 로드 (외부 패키지 의존 없이 처리)
def load_env_if_needed():
    if not os.environ.get("GEMINI_API_KEY"):
        env_path = Path(__file__).resolve().parent.parent / ".env"
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        os.environ[key.strip()] = val.strip()

def generate_with_gemini(api_key: str, prompt: str) -> str:
    """최신 google.genai 및 google.generativeai SDK를 모두 지원하는 유연한 생성 함수"""
    errors = []

    # 1. 신규 표준 google.genai SDK 우선 시도
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        for model_name in ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-2.5-flash"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                errors.append(f"google.genai ({model_name}): {str(e)}")
                continue
    except ImportError:
        pass

    # 2. 레거시 google.generativeai SDK 시도
    try:
        import google.generativeai as legacy_genai
        legacy_genai.configure(api_key=api_key)
        for model_name in ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-2.5-flash"]:
            try:
                model = legacy_genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                errors.append(f"google.generativeai ({model_name}): {str(e)}")
                continue
    except ImportError:
        pass

    detail = "; ".join(errors) if errors else "Gemini SDK(google-genai 또는 google-generativeai)가 설치되지 않았습니다."
    raise RuntimeError(f"Gemini API 호출에 실패했습니다: {detail}")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        load_env_if_needed()

        # Content-Length 읽기
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")

        try:
            data = json.loads(body)
            job = data.get("job", "").strip()
            experience = data.get("experience", "").strip()
            strength = data.get("strength", "").strip()

            # 유효성 검사
            if not job or not experience or not strength:
                self._send_json({"error": "지원 직무, 경험, 강점을 모두 입력해주세요."}, status=400)
                return

            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key or api_key == "여기에_키_입력":
                self._send_json({
                    "error": "GEMINI_API_KEY가 설정되지 않았습니다. .env 파일 또는 Vercel 환경 변수에 올바른 API 키를 등록해주세요."
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

    def do_OPTIONS(self):
        # CORS 사전 요청 대응
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
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

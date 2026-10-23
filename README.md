# 자소서 메이트 (Jaso-Mate) ✍️

> 지원 직무, 경험, 핵심 역량을 바탕으로 설득력 있는 맞춤형 자기소개서 지원동기 문단을 생성해주는 AI 웹서비스입니다.

---

## 🌐 1. 배포 정보 및 제출 링크
- **배포 URL (Vercel)**: `https://jaso-mate.vercel.app` *(배포 완료 후 실제 URL로 갱신)*
- **GitHub 저장소**: `https://github.com/사용자아이디/jaso-mate` *(GitHub 업로드 후 갱신)*
- **서비스 기획서**: [SERVICE_PLAN.md](./SERVICE_PLAN.md) *(과제 필수 패키지)*

---

## 📌 2. 서비스 소개 및 주요 섹션 (4개 섹션 구성)

바닐라 웹 기술과 Vercel Python Serverless Function을 기반으로 제작되었으며, 상단 고정 네비게이션을 통해 각 섹션으로 부드럽게 이동(Smooth Scroll)할 수 있습니다.

| 섹션 | 섹션명 | 상세 기능 및 역할 |
|:---:|:---:|:---|
| **#about** | **서비스 소개 (Hero)** | 서비스 목적 및 핵심 가치 3가지(빠른 초안, 두괄식 구성, 원클릭 복사) 안내 |
| **#generator** | **AI 문장 생성기 (Core)** | • 직무/경험/강점 입력 기반 Gemini 1.5 Flash 문단 생성<br>• 원클릭 예시 프리셋(개발자/마케터/기획직)<br>• 실시간 글자 수 카운터 및 원클릭 클립보드 복사<br>• **실패 처리 UX**: 빈값 검증, 25초 타임아웃 방지, 서버 에러 대응 |
| **#guide** | **합격 작성 팁** | 합격률을 높이는 자소서 3원칙 (두괄식 배치, 수치화, 회사와의 연결) |
| **#faq** | **자주 묻는 질문 (FAQ)** | 아코디언 형태의 Q&A (AI 초안 활용법, Gemini 모델 스펙, 개인정보 보안) |

---

## 🔄 3. 서비스 아키텍처 및 데이터 흐름

```
[사용자 브라우저]
  │  1. 직무·경험·강점 입력 후 [생성하기] 클릭
  ▼
[Vanilla JavaScript (main.js)]
  │  2. 필수값 검증 및 fetch('/api/generate', { AbortController (25s) })
  ▼
[Vercel Serverless Function (api/generate.py)]
  │  3. 환경 변수(GEMINI_API_KEY) 로드 및 프롬프트 엔지니어링
  ▼
[Google Gemini 1.5 Flash API]
  │  4. 450~600자 내외 비즈니스 서술체 문단 생성 후 반환
  ▼
[프론트엔드 화면 렌더링]
     5. 결과 표시, 글자 수 계산, 원클릭 클립보드 복사 지원
```

---

## 🛡️ 4. AI 기능 실패 처리 기준 (UX 정책)

과제 요구사항에 따라 3가지 실패 상황에 대해 명확한 사용자 피드백을 제공합니다:

1. **빈 입력 (필수값 누락)**:
   - 3개 입력 필드 중 빈값이 있을 경우 즉시 경고 안내 (`⚠️ 지원 직무, 주요 경험, 핵심 강점을 모두 입력해주세요.`)
2. **지연 / 타임아웃 (25초)**:
   - 4.5초 경과 시: `💡 Gemini 1.5가 문맥을 정교하게 다듬고 있습니다...` 로딩 문구 동적 변경
   - 25초 초과 시: `AbortController`를 통해 요청 중단 후 타임아웃 안내 (`⏳ 서버 응답 시간이 초과되었습니다...`)
3. **API 및 서버 오류 (4xx / 5xx)**:
   - API 키 미설정, 트래픽 쿼터 초과, 서버 장애 발생 시 사용자 친화적 에러 박스 표출

---

## 🛠️ 5. 기술 스택 (Tech Stack)

- **Frontend**: HTML5, CSS3 (Flexbox/Grid, 모바일 반응형 미디어 쿼리), Vanilla JavaScript (ES6+, Fetch API, AbortController)
- **Backend**: Python 3.9+ (Vercel Serverless Function - `BaseHTTPRequestHandler`)
- **AI SDK**: `google-generativeai` (Gemini 1.5 Flash)
- **Deploy**: Vercel, GitHub
- **Security**: Gemini API Key는 `.env` 및 Vercel 환경 변수로만 격리 보관 (Git 커밋 차단)

---

## 📁 6. 프로젝트 구조

```text
jaso-mate/
├── index.html          # 메인 페이지 (네비게이션 및 4개 섹션 마크업)
├── server.py           # [로컬 원클릭 서버] 정적 웹 + API 통합 개발 서버
├── start_local.bat     # [Windows] 더블 클릭으로 바로 실행하는 배치 파일
├── requirements.txt    # 백엔드 의존성 (google-genai, google-generativeai)
├── README.md           # 프로젝트 종합 안내 문서
├── SERVICE_PLAN.md     # [제출 필수] 서비스 기획서
├── .env                # Gemini API 키 환경변수 (Git 제외)
├── .gitignore          # Git 제외 목록 (.env, __pycache__, .vercel 등)
├── css/
│   └── style.css       # 반응형 스타일 시트 (모바일 미디어 쿼리 포함)
├── js/
│   └── main.js         # 프론트 로직 (API 호출, 타임아웃 UX, 프리셋, FAQ)
└── api/
    └── generate.py     # Vercel 서버리스 함수 (Gemini API 백엔드 엔드포인트)
```

---

## 🚀 7. 로컬 실행 방법

> ⚠️ **주의**: `index.html` 파일을 브라우저로 직접 더블 클릭(`file:///`)해서 열면 브라우저 보안 정책상 `.env` 환경 변수와 백엔드 API를 호출할 수 없습니다. 반드시 아래 로컬 서버 구동 방식을 이용해주세요.

### 🌟 방법 1: 원클릭 실행 (가장 추천 - Windows)
프로젝트 폴더 안의 **`start_local.bat`** 파일을 마우스로 **더블 클릭**하면 끝납니다!
- 자동으로 로컬 서버가 실행되고 기본 웹 브라우저(`http://localhost:8000`)가 즉시 열립니다.

---

### 💻 방법 2: 파이썬 터미널 실행
VS Code 터미널 또는 PowerShell에서 다음 명령어를 입력합니다:
```bash
# 필수 패키지 설치
pip install -r requirements.txt

# 로컬 개발 서버 실행
python server.py
```
실행 후 브라우저에서 `http://localhost:8000`으로 접속하시면 됩니다.

---

### ⚡ 방법 3: Vercel CLI 이용
Node.js 및 Vercel CLI 환경을 사용하고자 할 경우:
```powershell
# Vercel CLI 전역 설치
npm i -g vercel

# Vercel 로컬 개발 환경 구동
vercel dev
```

---

## ☁️ 8. Vercel 배포 가이드

1. **GitHub 저장소 생성 및 코드 Push**:
   ```powershell
   git init
   git add .
   git commit -m "feat: 자소서 메이트 완성 (반응형, 타임아웃 UX, 4개 섹션)"
   git branch -M main
   git remote add origin https://github.com/사용자아이디/저장소명.git
   git push -u origin main
   ```
2. **Vercel 대시보드 연동**:
   - [Vercel](https://vercel.com/) 대시보드 로그인 후 `Add New...` > `Project` 클릭
   - 방금 푸시한 GitHub 저장소를 선택(Import)
3. **환경 변수(API Key) 등록**:
   - 배포 설정 화면의 **Environment Variables** 탭으로 이동
   - **Key**: `GEMINI_API_KEY`
   - **Value**: 발급받은 실제 Gemini API 키 입력 후 `Add`
4. **Deploy 완료**:
   - `Deploy` 버튼을 클릭하면 약 1분 이내에 배포 URL이 생성됩니다.

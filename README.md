# Project Echo

## 🚀 프로젝트 개요

Project Echo는 디지털 마케팅 성과를 분석하고 리포트를 생성하는 자동화된 시스템입니다. 특정 브랜드와 경쟁 브랜드의 유튜브, 네이버 데이터를 수집하고, Gemini AI를 활용하여 심층 분석 리포트를 생성합니다. 생성된 리포트는 웹 페이지에서 인터랙티브한 차트와 함께 확인할 수 있으며, 마크다운 파일로도 저장됩니다.

## ✨ 주요 기능

-   **데이터 수집:**
    -   **YouTube:** 채널 상세 정보 및 인기 동영상 데이터 수집
    -   **Naver:** 검색량 트렌드, 쇼핑 검색 결과 (리뷰 수 포함) 수집
-   **AI 기반 분석:** Gemini AI 모델을 활용하여 수집된 데이터를 기반으로 심층적인 마케팅 리포트 (주간 헤드라인, 핵심 요약, 성과 대시보드, 상세 분석, 전략 제언) 생성
-   **인터랙티브 차트:** Chart.js를 활용하여 네이버 검색량 트렌드, 유튜브 구독자/조회수 비교, 네이버 쇼핑 관심도 점유율 등 시각적인 차트 제공
-   **리포트 저장:** 생성된 리포트를 데이터베이스에 저장하고, 추가적으로 마크다운 파일로 내보내 분석 및 활용 용이
-   **진행 상황 UI:** 리포트 생성 과정의 실시간 진행 상황을 허브 페이지에서 직관적으로 확인 가능

## 🛠️ 기술 스택

-   **백엔드:** Python, Django
-   **데이터 수집:** Google YouTube Data API v3, Naver Open API (DataLab, Shopping)
-   **AI 분석:** Google Gemini API
-   **데이터베이스:** SQLite (기본)
-   **프론트엔드:** HTML, CSS, JavaScript, Chart.js
-   **패키지 관리:** pip

## ⚙️ 설치 및 실행 방법

### 1. 환경 설정

1.  **저장소 클론:**
    ```bash
    git clone https://github.com/your-username/project_echo.git
    cd project_echo
    ```
2.  **가상 환경 설정 및 활성화:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate # macOS/Linux
    # venv\Scripts\activate # Windows
    ```
3.  **의존성 설치:**
    ```bash
    pip install -r requirements.txt
    ```
    `requirements.txt` 파일이 없다면, 다음 명령어로 생성할 수 있습니다:
    ```bash
    pip freeze > requirements.txt
    ```
    (필요한 라이브러리: `Django`, `google-api-python-client`, `requests`, `pandas`, `matplotlib`, `wordcloud`, `weasyprint`, `python-dotenv`)

### 2. API 키 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 API 키들을 추가합니다.

```dotenv
# .env
YOUTUBE_API_KEY=YOUR_YOUTUBE_API_KEY
NAVER_CLIENT_ID=YOUR_NAVER_CLIENT_ID
NAVER_CLIENT_SECRET=YOUR_NAVER_CLIENT_SECRET
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```
-   **YouTube Data API:** Google Cloud Console에서 API 키를 발급받으세요.
-   **Naver Open API:** 네이버 개발자 센터에서 애플리케이션을 등록하고 Client ID와 Client Secret을 발급받으세요.
-   **Gemini API:** Google AI Studio 또는 Google Cloud Console에서 API 키를 발급받으세요.

### 3. 데이터베이스 마이그레이션

```bash
python3 manage.py migrate
```

### 4. 관리자 계정 생성 (선택 사항)

리포트 관리자 페이지에 접근하려면 관리자 계정을 생성해야 합니다.

```bash
python3 manage.py createsuperuser
```

### 5. 개발 서버 실행

```bash
python3 manage.py runserver
```

서버가 `http://127.0.0.1:8000/` 에서 실행됩니다. 웹 브라우저에서 해당 주소로 접속하여 리포트 허브 페이지를 확인하세요.

## 📊 리포트 생성 및 확인

1.  **리포트 허브 페이지 접속:** `http://127.0.0.1:8000/`
2.  **브랜드 정보 입력:** "리포트 생성" 섹션에서 메인 브랜드명, 경쟁 브랜드명, 타겟 페르소나 키워드를 입력합니다.
3.  **리포트 생성 시작:** "리포트 생성 시작" 버튼을 클릭하면 비동기적으로 리포트 생성이 시작되며, 진행 상황이 UI에 표시됩니다.
4.  **리포트 확인:** 생성이 완료되면 "생성된 리포트" 목록에서 해당 리포트를 클릭하여 상세 내용을 확인합니다. 인터랙티브 차트와 AI 분석 결과를 볼 수 있습니다.
5.  **마크다운 리포트:** 생성된 리포트는 프로젝트 루트의 `repodt_data/` 폴더에 마크다운 파일로도 저장됩니다.

## 📂 프로젝트 구조 (핵심 부분)

```
project_echo/
├── project_echo/
│   ├── settings.py             # Django 설정 파일
│   └── urls.py                 # 프로젝트 URL 설정
├── reports/
│   ├── management/
│   │   └── commands/
│   │       └── collect_data.py # 핵심 데이터 수집 및 리포트 생성 로직 (Django Custom Command)
│   ├── services/
│   │   ├── chart_service.py    # Chart.js 데이터 생성 로직
│   │   ├── gemini_analyzer.py  # Gemini AI 분석 로직
│   │   ├── naver_collector.py  # 네이버 데이터 수집 로직
│   │   └── youtube_collector.py# 유튜브 데이터 수집 로직
│   ├── templates/
│   │   └── reports/
│   │       ├── hub_page.html   # 리포트 허브 페이지 (생성 폼, 진행 상황, 목록)
│   │       └── report_detail.html # 리포트 상세 페이지 (인터랙티브 차트 포함)
│   ├── views.py                # Django 뷰 (웹 요청 처리, 진행 상황 조회)
│   └── models.py               # Django 모델 (데이터베이스 스키마)
├── media/                      # 생성된 차트 이미지 등 미디어 파일 저장
├── 리포트 분석 데이터/         # 생성된 마크다운 리포트 저장
├── .env                        # 환경 변수 (API 키 등)
├── db.sqlite3                  # SQLite 데이터베이스 파일 (개발용)
├── manage.py                   # Django 관리 명령어 실행 스크립트
└── requirements.txt            # Python 의존성 목록
```

## 🤝 기여

기여를 환영합니다! 버그 리포트, 기능 제안, 코드 개선 등 어떤 형태의 기여든 좋습니다.

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

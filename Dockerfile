# 1. 베이스 이미지 설정
FROM python:3.11-slim

# 2. 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. 작업 디렉터리 설정 및 소스 코드 복사
WORKDIR /app
COPY . /app/

# 4. 시스템 패키지 및 Python 의존성 설치
RUN apt-get update   && apt-get install -y --no-install-recommends gcc python3-dev libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info fonts-nanum   && rm -rf /var/lib/apt/lists/*   && fc-cache -fv
RUN pip install --no-cache-dir -r requirements.txt

# 5. Entrypoint 스크립트 복사 및 권한 설정
COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 6. 정적 파일 수집
RUN python manage.py collectstatic --noinput

# 7. Gunicorn 실행 (Entrypoint를 통해)
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8100", "--timeout", "120", "project_echo.wsgi:application"]

# Youth

2025 신구대학교 EXPO 컴퓨터소프트웨어과 출품작

# 팀원들 개발 시 환경 설정 순서

1.  레파지토리 clone 또는 pull
2.  frontend 세팅하기
    ```py
    cd frontend
    yarn install
    ```
3.  backend 세팅 (FastAPI + 가상환경)
    ```py
    cd backend
    python -m venv venv # 가상환경 생성
    .\venv\Scripts\Activate.ps1 # 가상환경 실행 (PowerShell 기준)
    pip install -r requirements.txt # <- 요구사항 파일이 있을 경우
    ```
4.  FastAPI 서버 실행

        ```py
        python -m uvicorn main:app --reload

        ```

    - 접속 주소: http://localhost:8000

## python 가상환경 실행 명령어

1. ven/Scripts/active

# Youth

2025 신구대학교 EXPO 컴퓨터소프트웨어과 출품작

```0904 메모
aws 계정 권한 오류로 s3사용을 못하고 있음
우선은 Flask 로컬저장을 이용해 기능 구현 하고 추후 개선 예정
```

# 팀원들 개발 시 환경 설정 순서

1.  레파지토리 clone 또는 pull
2.  frontend 세팅하기
    ```py
    cd frontend
    yarn install
    ```
3.  backend 세팅 (Flask + 가상환경)
    ```py
    cd backend
    python -m venv venv # 가상환경 생성
    source venv/Scripts/activate # 가상환경 실행 (bash 기준)
    pip install flask
    ```
    ```py
    rest api 필요하면 깔기 (현재 안했음) 
    pip install flask-cors
    ```       

4.  서버 실행
    ```py
    python app.py
    ```
- 접속 주소: http://127.0.0.1:5000


## python 가상환경 실행 명령어
1. 활성화 
    ```source venv/Scripts/activate```
2. 앞에 (venv)붙으면 성공 ```(venv) dayoun@DESKTOP-XXXX MINGW64 ~/Youth/backend```
3. 비활성화 
```deactivate```


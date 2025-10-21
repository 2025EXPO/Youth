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
    flask run --host=0.0.0.0 --port=5000 --debug
    ```

- 접속 주소: http://127.0.0.1:5000

## python 가상환경 실행 명령어

1. 활성화
   `source venv/Scripts/activate`
2. 앞에 (venv)붙으면 성공 `(venv) dayoun@DESKTOP-XXXX MINGW64 ~/Youth/backend`
3. 비활성화
   `deactivate`

## 1018 AWS S3 연동(S3를 이용한 외부 이미지 접근 과정 정리)

### 1. 외부 사용자에게 QR로 이미지 전달이 가능해야함

포토부스에서 합성된 이미지를 고객에게 QR 코드로 즉시 제공
외부 사용자가 인터넷을 통해 이미지를 열 수 있는 저장소가 필요

처음에 두 가지 방안을 검토했음

| 구분 | 방식           | 설명                                                       |
| ---- | -------------- | ---------------------------------------------------------- |
| A    | EC2 + 서버     | Flask를 EC2에 배포하여 자체적으로 서버 운영                |
| B    | S3 버킷 업로드 | Flask가 이미지를 S3에 업로드하고, 고객은 S3 URL(QR)로 접근 |

**👉 최종 선택: S3만 사용하기로 결정**

**이유**

- EC2는 Flask 서버를 외부에 계속 띄워야해서 비용이 든다.
- '이미지 조회'의 간단한 기능만 필요하기 때문에 굳이 필요 없음<br>
  Flask: **이미지 합성 → S3 업로드** 만 하면 됨
- S3에 업로드된 이미지는 URL로 어디서든 접근 가능.
- 따라서 **EC2 없이도** QR 코드로 이미지 제공이 가능함

---

### 2. S3 버킷 생성 및 접근 정책 설정

- **리전:** `ap-northeast-3 (오사카)`
- **버킷 이름:** `계정이름-s3`_(expo용으로 교수님께서 주신 계정이라 해당 계정 이름으로 시작해야함)_

#### 설정 내용

- 버킷 생성 시 **모든 퍼블릭 액세스 차단 해제**
- 외부 사용자가 QR로 `/final/` 폴더의 이미지를 직접 볼 수 있도록
  **버킷 정책(JSON)** 을 수동으로 작성하여 적용

#### 적용된 버킷 정책

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Statement1",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::버킷이름/final/*" //혹시 몰라 계정명은 가림
    }
  ]
}
```

#### 정책 세부 내용

| 항목                                              | 설명                                                       |
| ------------------------------------------------- | ---------------------------------------------------------- |
| `"Principal": "*"`                                | 누구나 접근 가능                                           |
| `"Action": "s3:GetObject"`                        | 조회(GET)만 허용 (삭제·업로드 불가)                        |
| `"Resource": "arn:aws:s3:::expo-2025-s3/final/*"` | `/final/` 폴더 내부 파일만 외부 접근 허용                  |
| 결과                                              | `/uploads/`, `/print/` 등은 비공개 `/final/` 폴더만 공개됨 |

---

### 3. 테스트 진행

1. 버킷 내에 `final/` 폴더를 생성
2. 임의의 이미지(`test.png`)를 업로드
3. 퍼블릭 URL을 복사해 브라우저에서 접근

```
https://버킷이름.s3.ap-northeast-3.amazonaws.com/final/test.png
```

👉 **이미지가 정상적으로 열림 → 퍼블릭 접근 정책 적용 완료**

---

## 정리

> `버킷이름` 버킷의 `/final/` 폴더는
> EC2 없이도 외부 사용자가 QR을 통해 바로 접근 가능한
> 이미지 저장소로 완성되었음

## 근데 내가 Access Key / Secret Key 발급 금지된 상태라 IAM Role을 사용해야해서 EC2로 서버 배포하기로 했습니다...

## 🚀 EC2 서버 배포 및 코드 반영 방식

### ✅ 배경

Access Key / Secret Key 발급이 금지된 환경이므로,
**IAM Role**을 이용해 **EC2 인스턴스에 직접 Flask 서버를 배포**했습니다.

> 💡 내 로컬 PC에는 S3 접근 권한이 없지만,
> EC2에는 **IAM Role(SafeRoleForAllSguUsers)** 이 연결되어 있어
> Flask가 `boto3`를 통해 S3 업로드를 수행할 수 있습니다.

---

### 🧩 서버 코드 전송 (로컬 → EC2)

코드 수정 후 EC2로 직접 덮어쓰기 할 때👇

```bash
scp -i "C:\Users\kangd\Documents\GitHub\Youth\expo-2025.pem" -r "C:\Users\kangd\Documents\GitHub\Youth\backend" ec2-user@56.155.140.77:/home/ec2-user/
```

> ⚠️ `scp` 명령은 **로컬(내 PC)** 에서 실행해야 합니다.
> (PuTTY 안이 아니라 Windows PowerShell에서 실행)

---

### 🧠 서버 재실행

EC2에 접속(PuTTY)한 뒤👇

```bash
pkill -f app.py       # (선택) 기존 Flask 서버 중지
cd Youth/backend      # Flask 프로젝트 폴더로 이동
python3 app.py        # Flask 서버 실행
```

> ✅ Flask 서버가 정상 실행되면
> `* Running on http://0.0.0.0:5000` 로그가 표시됩니다.

---

### 🔄 코드 수정 반영 (Git 방식)

코드를 자주 수정한다면 `scp` 대신 **Git pull 방식**을 권장합니다.

로컬에서 수정 후 GitHub에 push한 뒤,
EC2 터미널(PuTTY)에서👇

```bash
cd Youth
git pull origin main
```

> GitHub의 최신 코드가 EC2에 자동 반영됩니다.

---

### 🧹 폴더 삭제 (불필요한 폴더 정리)

EC2에서 불필요한 폴더를 삭제할 때👇

```bash
rm -rf backend
```

> ⚠️ `rm -rf` 명령은 복구 불가능하므로 **삭제 대상이 정확한지 꼭 확인**하세요.

---

## ✅ 전체 흐름 요약

| 단계                 | 위치         | 설명                                 |
| -------------------- | ------------ | ------------------------------------ |
| 코드 수정            | 로컬 (내 PC) | VSCode 등에서 수정                   |
| GitHub 업로드        | 로컬         | GitHub Desktop 또는 CLI로 push       |
| EC2 업데이트         | EC2 (PuTTY)  | `git pull origin main`               |
| 서버 실행            | EC2 (PuTTY)  | `cd Youth/backend && python3 app.py` |
| 파일 직접 전송(대안) | 로컬         | `scp` 명령으로 수동 업로드           |

---

📘 **요약 한 줄**

> 내 컴퓨터에는 AWS 권한이 없지만,
> EC2는 IAM Role을 통해 자동 인증되므로
> Flask 서버를 EC2에 배포하고, Git pull로 최신 코드만 반영하는 구조입니다 ✅

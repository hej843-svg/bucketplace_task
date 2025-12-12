# 오늘의집 Android 앱 자동화 테스트 프로젝트

오늘의집 Android 앱의 설치 및 로그인 플로우를 자동화하는 테스트 프로젝트입니다. Appium과 Python을 사용하여 Google Play Store에서 앱을 설치하고, 이메일로 로그인 시나리오를 검증합니다.

## 프로젝트 개요

이 프로젝트는 다음 기능을 자동화합니다:
- **앱 설치**: Google Play Store에서 "오늘의집" 앱 검색 및 설치
- **로그인 플로우**: 다양한 시나리오에 대한 로그인 테스트
  - 정상 네트워크 환경에서의 앱 최초 실행
  - 네트워크 연결 해제 상태에서의 앱 실행
  - 로그인 페이지 UI 검증
  - 이메일 로그인 기능 검증
  - 로그인 버튼 비활성화 동작 검증
  - 로그인 성공/실패 시나리오
  - 로그인 실패 횟수 제한 및 초기화 검증
  - 네트워크 연결 해제 상태에서의 로그인 처리
  - 앱 재실행 시 로그인 상태 유지 검증

## 요구 사항

- **Python**: 3.10 이상
- **Android Studio**: Android SDK 및 에뮬레이터 사용
- **Appium Server**: 2.x (또는 1.x) 실행 중
- **Node.js**: Appium 설치용
- **ADB**: Android SDK platform-tools에 포함

## 설치

### 1. 저장소 클론 및 가상 환경 설정

```bash
cd {clone_path}
python -m venv .venv
.venv\Scripts\activate  # Windows
# 또는
source .venv/bin/activate  # Linux/Mac
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env` 파일을 생성하고 다음 항목을 설정하세요:

```bash
# Appium 서버 설정
APPIUM_SERVER_URL=http://127.0.0.1:4723

# 디바이스 설정
PLATFORM_NAME=Android
PLATFORM_VERSION=13.0  # 비어있으면 자동 감지
DEVICE_NAME=emulator-5554
AUTOMATION_NAME=UiAutomator2

# 앱 정보
APP_PACKAGE=net.bucketplace
APP_ACTIVITY=se.ohou.screen.splash.SplashActivity

# 오늘의집 앱 로그인 정보
LOGIN_ID=your_email@example.com
LOGIN_PASSWORD=your_password
```

## 프로젝트 구조

```
.
├── requirements.txt          # Python 의존성 패키지
├── pytest.ini               # pytest 설정 파일
├── README.md                 # 프로젝트 문서
├── .env                      # 환경 변수
└── src/
    ├── config/
    │   └── settings.py       # 환경 변수 로딩 및 Appium Capabilities 설정
    ├── driver.py             # Appium WebDriver 생성 헬퍼
    └── pages/                # Page Object Model
        ├── base_page.py      # 공통 기능 (BasePage)
        ├── app_drawer_page.py      # 기기의 앱 서랍 페이지
        ├── playstore_page.py       # Google Play Store 페이지
        ├── search_results_page.py  # 검색 결과 페이지
        ├── splash_page.py          # 스플래시 페이지
        ├── login_page.py          # 로그인 페이지
        ├── login_page_by_email.py # 이메일 로그인 페이지
        ├── main_home_page.py      # 메인 홈페이지
        ├── my_page.py             # 마이페이지
        └── setting_page.py        # 설정 페이지
└── tests/
    ├── conftest.py           # pytest fixtures (driver 등)
    ├── test_install_app.py   # 앱 설치 테스트 (INSTALL_001)
    └── test_login_flow.py    # 로그인 플로우 테스트 (LOGIN_001 ~ LOGIN_013)
```

## 테스트 실행

### 사전 준비

1. **Android 에뮬레이터 실행**
   - Android Studio에서 에뮬레이터를 실행하거나
   - 명령줄에서 `emulator -avd <avd_name>` 실행

2. **Appium 서버 실행** (별도 터미널)
   ```bash
   appium
   ```

### 테스트 실행 방법

#### 전체 테스트 실행
```bash
.venv\Scripts\activate
pytest
```

#### 특정 테스트 파일 실행
```bash
# 앱 설치 테스트만 실행
pytest tests/test_install_app.py

# 로그인 플로우 테스트만 실행
pytest tests/test_login_flow.py
```

#### 우선순위별 테스트 실행
- 주의 사항: 한 묶음으로 수행되어야하는 케이스가 존재합니다.
```bash
# Priority 1 테스트만 실행
pytest -m p1

# Priority 2 테스트만 실행
pytest -m p2

# Priority 3 테스트만 실행
pytest -m p3
```

#### 특정 테스트 케이스 실행
```bash
# LOGIN_001 테스트만 실행
pytest tests/test_login_flow.py::test_login_flow[LOGIN_001]

# INSTALL_001 테스트만 실행
pytest tests/test_install_app.py::test_install_app[INSTALL_001]
```

#### 상세 로그와 함께 실행
```bash
pytest --log-cli-level=DEBUG
```

## 테스트 케이스
- Testcase_doc folder의 문서 참고 (https://github.com/hej843-svg/bucketplace_task/blob/main/testcase_doc/OHOUS_TESTCASE_android_v.1.0.ods)

## 주요 기능

### Page Object Model (POM)
모든 페이지는 Page Object Model 패턴을 따릅니다. 각 페이지 클래스는 해당 페이지의 요소(locator)와 동작을 캡슐화합니다.

### Soft Assertion
`pytest-check`를 사용하여 테스트 중 일부 assertion이 실패해도 나머지 테스트를 계속 진행할 수 있습니다.

### 공통 기능
- **BasePage**: 모든 페이지에서 공통으로 사용되는 기능
  - 요소 찾기, 클릭, 텍스트 입력
  - 명시적 대기 (WebDriverWait)
  - 스크롤 기능
  - 토스트 메시지 확인
  - 네트워크 제어 (연결/해제)
  - 앱 종료 및 재실행
  - 시스템 팝업 처리

### 로깅
- pytest 로그는 `pytest_log.txt` 파일에 저장됩니다
- DEBUG 레벨 로그로 상세한 실행 정보 확인 가능

## 문제 해결

### 테스트 실패 시
- `pytest_log.txt` 파일에서 상세 로그 확인
- `--log-cli-level=DEBUG` 옵션으로 실시간 로그 확인
- 에뮬레이터 화면에서 실제 동작 확인

## 개발 환경

이 프로젝트는 다음 환경에서 개발 및 테스트되었습니다:

### 필수 소프트웨어 버전

- **Java (JDK)**: openjdk version "21.0.9" 2025-10-21 LTS
  ```bash
  java -version
  ```

- **Node.js**: v25.2.1
  ```bash
  node -v
  ```

- **Appium**: 3.1.2
  ```bash
  appium --version
  ```

- **Appium Inspector**: v2025.11.1

- **Python**: 3.14.0
  ```bash
  python --version
  ```

- **ADB (Android Debug Bridge)**: version 1.0.41, Version 36.0.0-13206524
  ```bash
  adb version
  ```

### 운영 체제

- **OS**: Windows 10.0.26100

### 버전 확인 명령어

각 소프트웨어의 버전을 확인하려면 위의 명령어를 실행하세요.

## 라이선스

이 프로젝트는 오늘의집 내부 채용 과제 제출 목적으로 사용됩니다.

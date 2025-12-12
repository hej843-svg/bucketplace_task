import time
import pytest
import pytest_check as check
from src.pages.app_drawer_page import AppDrawerPage
from src.pages.main_home_page import MainHomePage
from src.pages.my_page import MyPage
from src.pages.setting_page import SettingPage
from src.pages.splash_page import SplashPage
from src.pages.login_page import LoginPage
from src.pages.login_page_by_email import LoginPageByEmail
from src.config.settings import load_config

# LOGIN_001: 인터넷 네트워크 연결이 양호한 상태에서 설치한 앱이 정상적으로 최초 실행되는지 확인
@pytest.mark.parametrize("test_name", ["LOGIN_001"])
@pytest.mark.p1
def test_login_flow(test_name, driver):
    test_id = test_name
    
    # Pre Processing: 스플래시 페이지 초기화
    splash_page = SplashPage(driver)

    # Pre Processing: 앱 서랍 페이지 초기화
    app_drawer = AppDrawerPage(driver)

    # Pre Processing: 인터넷 네트워크 연결이 양호한지 확인
    assert app_drawer.is_network_connected(), "네트워크가 연결되어 있지 않습니다."

    # Pre Processing: 앱 설치 완료 확인
    assert app_drawer.wait_for_app_installed(timeout=10), "앱이 설치되지 않았습니다."

    # LOGIN_001-1: Test Step - 앱 서랍에서 앱 아이콘 탭
    assert app_drawer.launch_ohous_app(), "오늘의집 앱 실행에 실패했습니다."

    # LOGIN_001-2: Assertion - 앱 로고 페이지가 5초 이내에 노출되었다 사라짐
    # TODO: check fail 원인 분석 필요
    # check.is_true(splash_page.wait_for_splash_whole_page_loaded(timeout=5), "앱 로고 페이지가 5초 이내에 노출되지 않았습니다.")

    # LOGIN_001-2: Assertion - "Ohouse" 이미지뷰를 포함한 splash 화면이 5초 이내에 노출되었다 사라짐
    # TODO: check fail 원인 분석 필요
    # check.is_true(splash_page.wait_for_splash_lottie_page_loaded(timeout=5), "Ohouse splash 로티 페이지가 5초 이내에 노출되지 않았습니다.")

    # LOGIN_001-2-1: Test Step & Assertion - 앱 정상 실행 확인
    assert app_drawer.wait_for_app_running(timeout=10), "앱이 정상적으로 실행되지 않았습니다."

    # LOGIN_001-2-2: Test Step & Assertion - 로그인 페이지에 진입했는지 확인
    login_page = LoginPage(driver)
    check.is_true(login_page.is_login_page_loaded(timeout=10), "로그인 페이지가 10초 이내에 로드되지 않았습니다.")
    
    # Tear Down: 현재 화면의 모든 페이지 닫기
    app_drawer.terminate_all_apps()

    print(f"TEST {test_name} COMPLETED")


# LOGIN_002: 인터넷 네트워크 연결이 양호하지 않은 상태에서 설치한 앱이 정상적으로 최초 실행되는지 확인
@pytest.mark.parametrize("test_name", ["LOGIN_002"])
@pytest.mark.p2
def test_login_flow_no_network(test_name, driver):
    test_id = test_name
    
    # Pre Processing: 스플래시 페이지 초기화
    splash_page = SplashPage(driver)

    # Pre Processing: 앱 서랍 페이지 초기화
    app_drawer = AppDrawerPage(driver)

    # Pre Processing: 앱 설치 완료 확인
    assert app_drawer.wait_for_app_installed(timeout=10), "앱이 설치되지 않았습니다."

    # LOGIN_002-1: Test Step - 인터넷 네트워크 연결 끊기
    assert app_drawer.disable_network(), "네트워크 연결을 끊지 못했습니다."
    assert not app_drawer.is_network_connected(), "네트워크가 여전히 연결되어 있습니다."

    # LOGIN_002-2: Test Step - 앱 서랍에서 앱 아이콘 탭
    assert app_drawer.launch_ohous_app(), "오늘의집 앱 실행에 실패했습니다."

    # LOGIN_002-3-1: Test Step & Assertion - 앱 정상 실행 확인
    assert app_drawer.wait_for_app_running(timeout=10), "앱이 정상적으로 실행되지 않았습니다."

    # LOGIN_002-3-2: Test Step & Assertion - 로그인 페이지에 진입했는지 확인
    login_page = LoginPage(driver)
    check.is_true(login_page.is_login_page_loaded(timeout=10), "로그인 페이지가 10초 이내에 로드되지 않았습니다.")
    
    # Tear Down: 네트워크 연결 복구
    app_drawer.enable_network()

    # Tear Down: 현재 화면의 모든 페이지 닫기
    app_drawer.terminate_all_apps()
    
    print(f"TEST {test_name} COMPLETED")


# LOGIN_003: 로그인 페이지 UI 확인
@pytest.mark.parametrize("test_name", ["LOGIN_003"])
@pytest.mark.p3
def test_login_page_ui(test_name, driver):
    test_id = test_name

    # Pre Processing: 앱실행
    app_drawer = AppDrawerPage(driver)
    assert app_drawer.pre_processing_launch_ohous_app(), "오늘의집 앱 실행에 실패했습니다."

    # Pre Processing: 로그인 페이지 초기화 및 로드 대기
    login_page = LoginPage(driver)
    # 로그인 페이지가 완전히 로드될 때까지 대기
    check.is_true(login_page.is_login_page_loaded(timeout=20), "로그인 페이지가 20초 이내에 로드되지 않았습니다.")

    # LOGIN_003-1: Test Step & Assertion - 로그인 페이지의 모든 요소들이 노출되는지 확인
    check.is_true(login_page.are_login_elements_present(timeout=5), "로그인 페이지의 모든 요소들이 5초이내에 노출되지 않았습니다.")

    # Tear Down: 현재 화면의 모든 페이지 닫기
    app_drawer.terminate_all_apps()


### LOGIN-004 ~ LOGIN-013 그룹 테스트, 케이스 간 앱 종료 동작 없음.
# LOGIN_004: 이메일로 로그인 페이지 전환 확인
@pytest.mark.parametrize("test_name", ["LOGIN_004"])
@pytest.mark.p1
def test_login_page_email_login(test_name, driver):
    test_id = test_name

    # Pre Processing: 앱실행
    app_drawer = AppDrawerPage(driver)
    assert app_drawer.pre_processing_launch_ohous_app(), "오늘의집 앱 실행에 실패했습니다."

    # Pre Processing: 로그인 페이지 초기화 및 로드 대기
    login_page = LoginPage(driver)
    check.is_true(login_page.is_login_page_loaded(timeout=10), "로그인 페이지가 10초 이내에 로드되지 않았습니다.")

    # LOGIN_004-1: Test Step - [이메일로 로그인] 텍스트 버튼 탭
    login_page.click(login_page.IMAIL_LOGIN_BUTTON)

    # LOGIN_004-2: Assertion - 이메일로 로그인 페이지가 10초 이내에 로드되었는지 확인
    login_page_by_email = LoginPageByEmail(driver)
    check.is_true(login_page_by_email.is_email_login_page_loaded(timeout=10), "이메일로 로그인 페이지가 10초 이내에 로드되지 않았습니다.")

    print(f"TEST {test_name} COMPLETED")


# LOGIN_005: 이메일로 로그인 페이지의 뒤로가기 아이콘 탭 시 로그인 페이지로 복귀하는지 확인
@pytest.mark.parametrize("test_name", ["LOGIN_005"])
@pytest.mark.p2
def test_login_page_email_login_back_button(test_name, driver):
    test_id = test_name

    # Pre Processing: 이메일로 로그인 페이지 노출된 상태
    login_page_by_email = LoginPageByEmail(driver)
    check.is_true(login_page_by_email.is_email_login_page_loaded(timeout=10), "이메일로 로그인 페이지가 10초 이내에 로드되지 않았습니다.")

    # LOGIN_005-1: Test Step - 좌측 상단의 [<-] 아이콘 버튼 탭 탭
    login_page_by_email.click(login_page_by_email.BACK_BUTTON)

    # LOGIN_005-2: Assertion - 로그인 페이지가 10초 이내에 로드되었는지 확인
    login_page = LoginPage(driver)
    check.is_true(login_page.is_login_page_loaded(timeout=10), "로그인 페이지가 10초 이내에 로드되지 않았습니다.")

    print(f"TEST {test_name} COMPLETED")


# LOGIN_006: 이메일로 로그인 페이지 UI 확인
@pytest.mark.parametrize("test_name", ["LOGIN_006"])
@pytest.mark.p3
def test_login_page_email_login_ui(test_name, driver):
    test_id = test_name

    # LOGIN_005에서의 마지막 페이지가 로그인 페이지이기 때문에 이메일로 로그인 페이지 버튼 탭하여 이메일로 로그인 페이지로 이동
    login_page = LoginPage(driver)
    check.is_true(login_page.is_login_page_loaded(timeout=10), "로그인 페이지가 10초 이내에 로드되지 않았습니다.")
    login_page.click(login_page.IMAIL_LOGIN_BUTTON)

    # Pre Processing: 이메일로 로그인 페이지 노출된 상태
    login_page_by_email = LoginPageByEmail(driver)
    check.is_true(login_page_by_email.is_email_login_page_loaded(timeout=10), "이메일로 로그인 페이지가 10초 이내에 로드되지 않았습니다.")

    # LOGIN_006-1: Test Step - 이메일로 로그인 페이지의 모든 요소들이 노출되는지 확인
    check.is_true(login_page_by_email.are_email_login_elements_present(timeout=5), "이메일로 로그인 페이지의 모든 요소들이 5초 이내에 노출되지 않았습니다.")

    print(f"TEST {test_name} COMPLETED")


# LOGIN_007: 로그인 버튼 비활성화 동작 및 토스트 위젯 안내문구 확인
@pytest.mark.parametrize("test_name", ["LOGIN_007"])
@pytest.mark.p2
def test_login_page_email_login_login_button_disabled(test_name, driver):
    test_id = test_name 

    # Pre Processing: 이메일로 로그인 페이지 노출된 상태
    login_page_by_email = LoginPageByEmail(driver)
    check.is_true(login_page_by_email.is_email_login_page_loaded(timeout=10), "이메일로 로그인 페이지가 10초 이내에 로드되지 않았습니다.")

    # LOGIN_007-1, 2: Test Step - 이메일, 비밀번호 입력란에 빈값 입력
    login_page_by_email.clear_text_android(login_page_by_email.ID_INPUT_FIELD)
    login_page_by_email.clear_text_android(login_page_by_email.PASSWORD_INPUT_FIELD)

    login_page_by_email.click(login_page_by_email.ID_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.ID_INPUT_FIELD, "")
    login_page_by_email.click(login_page_by_email.PASSWORD_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.PASSWORD_INPUT_FIELD, "")

    # LOGIN_007-3-1: Assertion - [로그인하기] 로그인 버튼 비활성화 확인
    check.is_true(login_page_by_email.is_element_effectively_disabled(login_page_by_email.LOGIN_BUTTON), "[로그인하기] 로그인 버튼이 활성화 상태입니다.")

    # LOGIN_007-3-2: Assertion - "이메일을 입력해주세요." 토스트 위젯 노출되었다 사라짐
    check.is_true(login_page_by_email.wait_for_toast_message(toast_text="이메일을 입력해주세요.", timeout=5), "이메일을 입력해주세요. 토스트 위젯이 노출되지 않았습니다.")
    check.is_true(login_page_by_email.wait_for_toast_to_disappear(toast_text="이메일을 입력해주세요.", timeout=5), "이메일을 입력해주세요. 토스트 위젯이 노출되었다 사라지지 않았습니다.")

    # LOGIN_007-4, 5: Test Step - 이메일 입력란에 임의의 text, 비밀번호 입력란에 빈값 입력
    # 이메일 로그인 페이지가 여전히 로드되어 있는지 확인
    check.is_true(login_page_by_email.is_email_login_page_loaded(timeout=5), "이메일로 로그인 페이지가 로드되지 않았습니다.")
    login_page_by_email.clear_text_android(login_page_by_email.ID_INPUT_FIELD)
    login_page_by_email.clear_text_android(login_page_by_email.PASSWORD_INPUT_FIELD)

    login_page_by_email.click(login_page_by_email.ID_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.ID_INPUT_FIELD, "test@test.com")
    login_page_by_email.click(login_page_by_email.PASSWORD_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.PASSWORD_INPUT_FIELD, "")
    
    # LOGIN_007-6: Assertion - [로그인하기] 로그인 버튼 비활성화 확인
    check.is_true(login_page_by_email.is_element_effectively_disabled(login_page_by_email.LOGIN_BUTTON), "[로그인하기] 로그인 버튼이 활성화 상태입니다.")

    # LOGIN_007-6: Assertion - "비밀번호를 입력해주세요." 토스트 위젯 노출되었다 사라짐
    check.is_true(login_page_by_email.wait_for_toast_message(toast_text="비밀번호를 입력해주세요.", timeout=5), "비밀번호를 입력해주세요. 토스트 위젯이 노출되지 않았습니다.")
    check.is_true(login_page_by_email.wait_for_toast_to_disappear(toast_text="비밀번호를 입력해주세요.", timeout=5), "비밀번호를 입력해주세요. 토스트 위젯이 노출되었다 사라지지 않았습니다.")

    # LOGIN_007-7, 8: Test Step - 이메일 입력란에 빈값 입력, 비밀번호 입력란에 임의의 text 입력
    # 이메일 로그인 페이지가 여전히 로드되어 있는지 확인
    check.is_true(login_page_by_email.is_email_login_page_loaded(timeout=5), "이메일로 로그인 페이지가 로드되지 않았습니다.")
    login_page_by_email.clear_text_android(login_page_by_email.ID_INPUT_FIELD)
    login_page_by_email.clear_text_android(login_page_by_email.PASSWORD_INPUT_FIELD)
    
    login_page_by_email.click(login_page_by_email.ID_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.ID_INPUT_FIELD, "")
    login_page_by_email.click(login_page_by_email.PASSWORD_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.PASSWORD_INPUT_FIELD, "test1234")
    
    # LOGIN_007-9: Assertion - [로그인하기] 로그인 버튼 비활성화 확인
    check.is_true(login_page_by_email.is_element_effectively_disabled(login_page_by_email.LOGIN_BUTTON), "[로그인하기] 로그인 버튼이 활성화 상태입니다.")

    # LOGIN_007-7: Assertion - "이메일을 입력해주세요." 토스트 위젯 노출되었다 사라짐
    check.is_true(login_page_by_email.wait_for_toast_message(toast_text="이메일을 입력해주세요.", timeout=5), "이메일을 입력해주세요. 토스트 위젯이 노출되지 않았습니다.")
    check.is_true(login_page_by_email.wait_for_toast_to_disappear(toast_text="이메일을 입력해주세요.", timeout=5), "이메일을 입력해주세요. 토스트 위젯이 노출되었다 사라지지 않았습니다.")

    print(f"TEST {test_name} COMPLETED")


# LOGIN-008: 올바른 계정으로 로그인 시도 시 로그인 성공 동작 확인
@pytest.mark.parametrize("test_name", ["LOGIN_008"])
@pytest.mark.p1
def test_login_page_email_login_login_success(test_name, driver):
    test_id = test_name

    # Pre Processing: 이메일로 로그인 페이지 노출된 상태
    login_page_by_email = LoginPageByEmail(driver)
    check.is_true(login_page_by_email.is_email_login_page_loaded(timeout=10), "이메일로 로그인 페이지가 10초 이내에 로드되지 않았습니다.")

    # Pre Processing: 환경 변수에서 로그인 정보 로드
    config = load_config()
    assert config.login_id is not None, ".env 파일에 LOGIN_ID가 설정되어 있지 않습니다."
    assert config.login_password is not None, ".env 파일에 LOGIN_PASSWORD가 설정되어 있지 않습니다."

    # LOGIN_008-1: Test Step -  이메일 입력란에 보유한 계정의 이메일 text 입력
    login_page_by_email.clear_text_android(login_page_by_email.ID_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.ID_INPUT_FIELD, config.login_id)

    # LOGIN_008-2: Test Step - 비밀번호 입력란에 보유한 계정의 비밀번호 text 입력
    login_page_by_email.clear_text_android(login_page_by_email.PASSWORD_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.PASSWORD_INPUT_FIELD, config.login_password)

    # LOGIN_008-3: Test Step - [로그인하기] 로그인 버튼 탭
    login_page_by_email.click(login_page_by_email.LOGIN_BUTTON)

    # LOGIN_008-3: Assertion - "로그인 중입니다." 안내문구의 팝업창 노출되었다 사라짐
    # Step 1: 팝업이 나타났는지 확인 (매우 짧은 timeout으로 빠르게 확인)
    check.is_true(login_page_by_email.wait_for_toast_message(toast_text="로그인 중입니다.", timeout=0.5), "로그인 중입니다. 안내문구의 팝업창이 노출되지 않았습니다.")
    # Step 2: 팝업이 사라졌는지 확인
    check.is_true(login_page_by_email.wait_for_toast_to_disappear(toast_text="로그인 중입니다.", timeout=10), "로그인 중입니다. 안내문구의 팝업창이 노출되었다 사라지지 않았습니다.")

    main_home_page = MainHomePage(driver)
    # 만약 Google Password Manager 안내문구 팝업이 노출되었다면 [나중에] 또는 [사용 안함] 버튼 탭
    if main_home_page.is_google_password_manager_popup_present(timeout=1):
        main_home_page.click_google_password_manager_dismiss_button(timeout=1)

    # LOGIN_008-3: Assertion - 오늘의집 메인 홈페이지가 10초 이내에 노출됨
    check.is_true(main_home_page.is_main_home_page_loaded(timeout=10), "오늘의집 메인 홈페이지가 10초 이내에 노출되지 않았습니다.")

    print(f"TEST {test_name} COMPLETED")


# LOGIN_009: 잘못된 비밀번호로 로그인 시도 시 로그인 실패 동작 확인
@pytest.mark.parametrize("test_name", ["LOGIN_009"])    
@pytest.mark.p2
def test_login_page_email_login_password_login_failed(test_name, driver):
    test_id = test_name

    # Pre Processing: 환경 변수에서 로그인 정보 로드
    config = load_config()
    assert config.login_id is not None, ".env 파일에 LOGIN_ID가 설정되어 있지 않습니다."
    assert config.login_password is not None, ".env 파일에 LOGIN_PASSWORD가 설정되어 있지 않습니다."

    # Pre Processing: 이메일로 로그인 페이지 노출된 상태
    # LOGIN-008에서 메인 홈 페이지 노출된 상태므로 로그아웃하여 이메일로 로그인 페이지로 이동
    main_home_page = MainHomePage(driver)
    result, error_message = main_home_page.logout_in_main_home_page(main_home_page, timeout=20)
    check.is_true(result, error_message)
    
    login_page = LoginPage(driver)
    check.is_true(login_page.is_login_page_loaded(timeout=10), "로그인 페이지가 10초 이내에 노출되지 않았습니다.")

    login_page.click(login_page.IMAIL_LOGIN_BUTTON)

    login_page_by_email = LoginPageByEmail(driver)
    check.is_true(login_page_by_email.is_email_login_page_loaded(timeout=10), "이메일로 로그인 페이지가 10초 이내에 로드되지 않았습니다.")

    # LOGIN_008-1: Test Step -  이메일 입력란에 보유한 계정의 이메일 text 입력
    login_page_by_email.clear_text_android(login_page_by_email.ID_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.ID_INPUT_FIELD, config.login_id)

    # LOGIN_008-2: Test Step - 비밀번호 입력란에 보유한 계정의 비밀번호가 아닌 임의의 text 입력
    login_page_by_email.clear_text_android(login_page_by_email.PASSWORD_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.PASSWORD_INPUT_FIELD, "wrong_password")

    # LOGIN_008-2: Assertion - 비밀번호 입력란에 입력한 text가 마스킹되어 노출됨
    check.is_true(login_page_by_email.is_input_field_masked(login_page_by_email.PASSWORD_INPUT_FIELD), "비밀번호 입력란에 입력한 text가 마스킹되어 노출되지 않았습니다.")

    # LOGIN_008-3: Test Step - [로그인하기] 로그인 버튼 탭
    login_page_by_email.click(login_page_by_email.LOGIN_BUTTON)

    # LOGIN_008-4: Assertion - "10번 실패하면 10분간 로그인이 제한돼요. ({로그인 실패한 횟수}/10)" 안내문구의 토스트 위젯 노출되었다 사라짐
    # 로그인 실패 횟수는 중요하지 않기 때문에 toast_text에 n/10 대신 안내문구만 넣어서 확인
    check.is_true(login_page_by_email.wait_for_toast_message(toast_text="10번 실패하면 10분간 로그인이 제한돼요.", timeout=5), "10번 실패하면 10분간 로그인이 제한돼요. 안내문구의 토스트 위젯이 노출되지 않았습니다.")
    check.is_true(login_page_by_email.wait_for_toast_to_disappear(toast_text="10번 실패하면 10분간 로그인이 제한돼요.", timeout=5), "10번 실패하면 10분간 로그인이 제한돼요. 안내문구의 토스트 위젯이 노출되었다 사라지지 않았습니다.")

    print(f"TEST {test_name} COMPLETED")


# LOGIN_010: 잘못된 비밀번호로 연속 10회 미만 로그인 시도 후 로그인 성공 시 로그인 실패 횟수 초기화 확인
@pytest.mark.parametrize("test_name", ["LOGIN_010"])
@pytest.mark.p3
def test_login_page_email_login_lock_count_reset(test_name, driver):
    test_id = test_name

    # Pre Processing: 이메일로 로그인 페이지 노출된 상태
    login_page_by_email = LoginPageByEmail(driver)
    check.is_true(login_page_by_email.is_email_login_page_loaded(timeout=10), "이메일로 로그인 페이지가 10초 이내에 로드되지 않았습니다.")

    # Pre Processing: 환경 변수에서 로그인 정보 로드
    config = load_config()
    assert config.login_id is not None, ".env 파일에 LOGIN_ID가 설정되어 있지 않습니다."
    assert config.login_password is not None, ".env 파일에 LOGIN_PASSWORD가 설정되어 있지 않습니다."

    # Pre Processing: 잘못된 비밀번호로 로그인 연속 3회 시도된 상태
    login_page_by_email.attempt_login_multiple_times(
        email=config.login_id,
        password="wrong_password",
        count=3
    )

    # LOGIN_009-1: Test Step - 가입된 계정과 일치하는 이메일 입력 후 입력한 이메일의 비밀번호가 아닌 임의의 text의 비밀번호로 로그인 시도
    login_page_by_email.clear_text_android(login_page_by_email.ID_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.ID_INPUT_FIELD, config.login_id)
    login_page_by_email.clear_text_android(login_page_by_email.PASSWORD_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.PASSWORD_INPUT_FIELD, "wrong_password")
    login_page_by_email.click(login_page_by_email.LOGIN_BUTTON)

    # LOGIN_009-1-1: Assertion - "로그인 중입니다." 안내문구의 팝업창 노출되었다 사라짐
    check.is_true(login_page_by_email.wait_for_toast_message(toast_text="로그인 중입니다.", timeout=0.5), "로그인 중입니다. 안내문구의 팝업창이 노출되지 않았습니다.")
    check.is_true(login_page_by_email.wait_for_toast_to_disappear(toast_text="로그인 중입니다.", timeout=10), "로그인 중입니다. 안내문구의 팝업창이 노출되었다 사라지지 않았습니다.")

    # LOGIN_009-1-2: Assertion - "10번 실패하면 10분간 로그인이 제한돼요. (4/10)" 안내문구의 토스트 위젯 노출되었다 사라짐
    check.is_true(login_page_by_email.wait_for_toast_message(toast_text="10번 실패하면 10분간 로그인이 제한돼요. (4/10)", timeout=5), "10번 실패하면 10분간 로그인이 제한돼요. (4/10) 안내문구의 토스트 위젯이 노출되지 않았습니다.")
    check.is_true(login_page_by_email.wait_for_toast_to_disappear(toast_text="10번 실패하면 10분간 로그인이 제한돼요. (4/10)", timeout=5), "10번 실패하면 10분간 로그인이 제한돼요. (4/10) 안내문구의 토스트 위젯이 노출되었다 사라지지 않았습니다.")
    time.sleep(1)

    # LOGIN_009-2: Test Step - 가입된 계정의 정보와 올바른 이메일과 비밀번호 로그인
    login_page_by_email.clear_text_android(login_page_by_email.ID_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.ID_INPUT_FIELD, config.login_id)
    login_page_by_email.clear_text_android(login_page_by_email.PASSWORD_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.PASSWORD_INPUT_FIELD, config.login_password)
    login_page_by_email.click(login_page_by_email.LOGIN_BUTTON)

    # LOGIN_009-2: Assertion - 로그인 성공
    main_home_page = MainHomePage(driver)
    check.is_true(main_home_page.is_main_home_page_loaded(timeout=10), "오늘의집 메인 홈페이지가 10초 이내에 노출되지 않았습니다.")

    # LOGIN_009-3: Step - 메인 홈페이지의 하단 footer의 [마이페이지] 버튼 클릭 후 우측 상단의 [설정] 아이콘 버튼 탭
    # LOGIN_009-3: Assertion - 설정 페이지가 10초 이내에 노출됨
    # LOGIN_009-4: Test Step - 페이지 최하단으로 스크롤하여 [로그아웃] 버튼 탭
    # LOGIN_009-4-1: Assertion - 하단에 "(오늘의집 아이콘) 로그아웃 되었습니다." 토스트 위젯 노출되었다 사라짐
    result, error_message = main_home_page.logout_in_main_home_page(main_home_page, timeout=20)
    check.is_true(result, error_message)
    
    # LOGIN_009-4-2: Assertion - 로그아웃되어 로그인 페이지가 10초 이내에 노출됨
    login_page = LoginPage(driver)
    check.is_true(login_page.is_login_page_loaded(timeout=10), "로그인 페이지가 10초 이내에 노출되지 않았습니다.")

    # LOGIN_009-5: Test Step - [이메일로 로그인] 텍스트 버튼 탭
    login_page.click(login_page.IMAIL_LOGIN_BUTTON)

    # LOGIN_009-5: Assertion - 이메일로 로그인 페이지가 10초 이내에 노출됨
    login_page_by_email = LoginPageByEmail(driver)
    check.is_true(login_page_by_email.is_email_login_page_loaded(timeout=10), "이메일로 로그인 페이지가 10초 이내에 노출되지 않았습니다.")

    # LOGIN_009-6: Test Step - 가입된 계정과 일치하는 이메일 입력 후 입력한 이메일의 비밀번호가 아닌 임의의 text의 비밀번호로 로그인 시도
    login_page_by_email.clear_text_android(login_page_by_email.ID_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.ID_INPUT_FIELD, config.login_id)
    login_page_by_email.clear_text_android(login_page_by_email.PASSWORD_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.PASSWORD_INPUT_FIELD, "wrong_password")
    login_page_by_email.click(login_page_by_email.LOGIN_BUTTON)

    # LOGIN_009-6: Assertion - 로그인 실패 횟수가 초기화되어 하단 영역에 "10번 실패하면 10분간 로그인이 제한돼요. (1/10)" 안내문구의 토스트 위젯 노출되었다 사라짐
    check.is_true(login_page_by_email.wait_for_toast_message(toast_text="10번 실패하면 10분간 로그인이 제한돼요. (1/10)", timeout=5), "10번 실패하면 10분간 로그인이 제한돼요. (1/10) 안내문구의 토스트 위젯이 노출되지 않았습니다.")
    check.is_true(login_page_by_email.wait_for_toast_to_disappear(toast_text="10번 실패하면 10분간 로그인이 제한돼요. (1/10)", timeout=5), "10번 실패하면 10분간 로그인이 제한돼요. (1/10) 안내문구의 토스트 위젯이 노출되었다 사라지지 않았습니다.")

    print(f"TEST {test_name} COMPLETED")


# LOGIN_011: 잘못된 비밀번호로 연속 10회 로그인 시도 시 로그인 재한 동작되어 10분간 로그인 시도 불가한지 확인
@pytest.mark.parametrize("test_name", ["LOGIN_011"])
@pytest.mark.p3
def test_login_page_email_login_lock_blocked(test_name, driver):
    test_id = test_name

    # Pre Processing: 이메일로 로그인 페이지 노출된 상태
    login_page_by_email = LoginPageByEmail(driver)
    check.is_true(login_page_by_email.is_email_login_page_loaded(timeout=10), "이메일로 로그인 페이지가 10초 이내에 로드되지 않았습니다.")

    # Pre Processing: 환경 변수에서 로그인 정보 로드
    config = load_config()
    assert config.login_id is not None, ".env 파일에 LOGIN_ID가 설정되어 있지 않습니다."
    assert config.login_password is not None, ".env 파일에 LOGIN_PASSWORD가 설정되어 있지 않습니다."

    # Pre Processing: 잘못된 비밀번호로 로그인 연속 9회 시도된 상태
    login_page_by_email.attempt_login_multiple_times(
        email=config.login_id,
        password="wrong_password",
        count=9
    )

    # LOGIN_011-1: Test Step - 이메일 입력란에 보유한 계정의 이메일 text 입력
    login_page_by_email.clear_text_android(login_page_by_email.ID_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.ID_INPUT_FIELD, config.login_id)

    # LOGIN_011-2: Test Step - 비밀번호 입력란에 보유한 계정의 비밀번호가 아닌 임의의 text 입력
    login_page_by_email.clear_text_android(login_page_by_email.PASSWORD_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.PASSWORD_INPUT_FIELD, "wrong_password")

    # LOGIN_011-3: Test Step - [로그인하기] 로그인 버튼 탭
    login_page_by_email.click(login_page_by_email.LOGIN_BUTTON)

    # LOGIN_011-3-1: Assertion - 중앙 영역에 "로그인 중입니다." 안내문구의 팝업창 노출되었다 사라짐
    check.is_true(login_page_by_email.wait_for_toast_message(toast_text="로그인 중입니다.", timeout=0.5), "로그인 중입니다. 안내문구의 팝업창이 노출되지 않았습니다.")
    check.is_true(login_page_by_email.wait_for_toast_to_disappear(toast_text="로그인 중입니다.", timeout=10), "로그인 중입니다. 안내문구의 팝업창이 노출되었다 사라지지 않았습니다.")

    # LOGIN_011-3-2: Assertion - 로그인 실패 횟수가 초기화되어 하단 영역에 "로그인이 제한되었어요. 10분 후 다시 시도해주세요." 안내문구의 토스트 위젯 노출되었다 사라짐
    check.is_true(login_page_by_email.wait_for_toast_message(toast_text="로그인이 제한되었어요. 10분 후 다시 시도해주세요.", timeout=5), "로그인이 제한되었어요. 10분 후 다시 시도해주세요. 안내문구의 토스트 위젯이 노출되지 않았습니다.")
    check.is_true(login_page_by_email.wait_for_toast_to_disappear(toast_text="로그인이 제한되었어요. 10분 후 다시 시도해주세요.", timeout=5), "로그인이 제한되었어요. 10분 후 다시 시도해주세요. 안내문구의 토스트 위젯이 노출되었다 사라지지 않았습니다.")

    # LOGIN_011-4: Test Step - 마지막 로그인 시도 후 10분 경과 전 가입된 계정과 다른 이메일 또는 비밀번호로 로그인 시도
    time.sleep(10)
    login_page_by_email.clear_text_android(login_page_by_email.ID_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.ID_INPUT_FIELD, config.login_id)
    login_page_by_email.clear_text_android(login_page_by_email.PASSWORD_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.PASSWORD_INPUT_FIELD, "wrong_password")
    login_page_by_email.click(login_page_by_email.LOGIN_BUTTON)

    # LOGIN_011-4-1: Assertion - 중앙 영역에 "로그인 중입니다." 안내문구의 팝업창 노출되었다 사라짐
    check.is_true(login_page_by_email.wait_for_toast_message(toast_text="로그인 중입니다.", timeout=0.5), "로그인 중입니다. 안내문구의 팝업창이 노출되지 않았습니다.")
    check.is_true(login_page_by_email.wait_for_toast_to_disappear(toast_text="로그인 중입니다.", timeout=10), "로그인 중입니다. 안내문구의 팝업창이 노출되었다 사라지지 않았습니다.")

    # LOGIN_011-4-2: Assertion - 로그인 실패 횟수가 초기화되어 하단 영역에 "로그인이 제한되었어요. 10분 후 다시 시도해주세요" 안내문구의 토스트 위젯 노출되었다 사라짐
    check.is_true(login_page_by_email.wait_for_toast_message(toast_text="로그인이 제한되었어요. 10분 후 다시 시도해주세요.", timeout=5), "로그인이 제한되었어요. 10분 후 다시 시도해주세요. 안내문구의 토스트 위젯이 노출되지 않았습니다.")
    check.is_true(login_page_by_email.wait_for_toast_to_disappear(toast_text="로그인이 제한되었어요. 10분 후 다시 시도해주세요.", timeout=5), "로그인이 제한되었어요. 10분 후 다시 시도해주세요. 안내문구의 토스트 위젯이 노출되었다 사라지지 않았습니다.")

    # LOGIN_011-5: Test Step - 마지막 로그인 시도 후 10분 경과 후 가입된 계정과 일치하는 이메일과 비밀번호로 로그인 시도
    login_page_by_email.wait_with_session_keepalive(590)  # 10분 대기
    login_page_by_email.clear_text_android(login_page_by_email.ID_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.ID_INPUT_FIELD, config.login_id)
    login_page_by_email.clear_text_android(login_page_by_email.PASSWORD_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.PASSWORD_INPUT_FIELD, config.login_password)
    login_page_by_email.click(login_page_by_email.LOGIN_BUTTON)

    # LOGIN_011-5: Assertion - 로그인 성공하여 오늘의집 메인 페이지가 10초 이내에 노출됨
    main_home_page = MainHomePage(driver)
    check.is_true(main_home_page.is_main_home_page_loaded(timeout=10), "오늘의집 메인 홈페이지가 10초 이내에 노출되지 않았습니다.")

    print(f"TEST {test_name} COMPLETED")


# LOGIN_012: 로그인 시도 시 네트워크 연결 해제 상황에서 로그인 불가와 오류 처리 적합성 확인 및 네트워크 연결 재개 시 정상 로그인 가능한지 확인
@pytest.mark.parametrize("test_name", ["LOGIN_012"])    
@pytest.mark.p3
def test_login_page_email_login_network_disconnected(test_name, driver):
    test_id = test_name

    # Pre Processing: 이메일로 로그인 페이지 노출된 상태 
    # LOGIN_011 에서 마지막 페이지가 오늘의집 메인 페이지이므로 로그아웃하여 이메일로 로그인 페이지까지의 step 진행
    main_home_page = MainHomePage(driver)
    result, error_message = main_home_page.logout_in_main_home_page(main_home_page, timeout=20)
    check.is_true(result, error_message)
    
    # 로그인 페이지 진입 확인
    login_page = LoginPage(driver)
    # 로그아웃 토스트 위젯 노출 및 사라짐 확인
    check.is_true(login_page.wait_for_toast_message(toast_text="로그아웃 되었습니다.", timeout=5), "로그아웃 되었습니다. 토스트 위젯이 노출되지 않았습니다.")
    check.is_true(login_page.wait_for_toast_to_disappear(toast_text="로그아웃 되었습니다.", timeout=5), "로그아웃 되었습니다. 토스트 위젯이 노출되었다 사라지지 않았습니다.")

    # [이메일로 로그인] 텍스트 버튼 탭
    login_page.click(login_page.IMAIL_LOGIN_BUTTON)

    # 이메일로 로그인 페이지가 10초 이내에 노출되었는지 확인
    login_page_by_email = LoginPageByEmail(driver)
    check.is_true(login_page_by_email.is_email_login_page_loaded(timeout=10), "이메일로 로그인 페이지가 10초 이내에 노출되지 않았습니다.")

    # Pre Processing: 환경 변수에서 로그인 정보 로드
    config = load_config()
    assert config.login_id is not None, ".env 파일에 LOGIN_ID가 설정되어 있지 않습니다."
    assert config.login_password is not None, ".env 파일에 LOGIN_PASSWORD가 설정되어 있지 않습니다."

    # LOGIN_012-1: Test Step - 이메일 입력란에 보유한 계정의 이메일 text 입력
    login_page_by_email.clear_text_android(login_page_by_email.ID_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.ID_INPUT_FIELD, config.login_id)

    # LOGIN_012-2: Test Step - 비밀번호 입력란에 보유한 계정의 비밀번호 text 입력
    login_page_by_email.clear_text_android(login_page_by_email.PASSWORD_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.PASSWORD_INPUT_FIELD, config.login_password)

    # LOGIN_012-3: Test Step - 기기의 인터넷 네트워크 연결 기능 off
    app_drawer = AppDrawerPage(driver)
    assert app_drawer.disable_network(), "네트워크 연결을 끊지 못했습니다."
    assert not app_drawer.is_network_connected(), "네트워크가 여전히 연결되어 있습니다."

    # LOGIN_012-4: Test Step - [로그인하기] 로그인 버튼 탭
    login_page_by_email.click(login_page_by_email.LOGIN_BUTTON)

    # LOGIN_012-4-2: Assertion - 중앙 영역에 "로그인 중입니다." 안내문구의 팝업창 노출되었다 사라짐
    check.is_true(login_page_by_email.wait_for_toast_message(toast_text="로그인 중입니다.", timeout=0.5), "로그인 중입니다. 안내문구의 팝업창이 노출되지 않았습니다.")
    check.is_true(login_page_by_email.wait_for_toast_to_disappear(toast_text="로그인 중입니다.", timeout=10), "로그인 중입니다. 안내문구의 팝업창이 노출되었다 사라지지 않았습니다.")

    # LOGIN_012-4-2: Assertion - 하단 영역에 "Unable to solve host "ohous.se": No address associated with hostname" 안내문구의 토스트 위젯 노출되었다 사라짐
    check.is_true(login_page_by_email.wait_for_toast_message(toast_text="Unable to solve host \"ohous.se\": No address associated with hostname", timeout=5), "Unable to solve host \"ohous.se\": No address associated with hostname 안내문구의 토스트 위젯이 노출되지 않았습니다.")
    check.is_true(login_page_by_email.wait_for_toast_to_disappear(toast_text="Unable to solve host \"ohous.se\": No address associated with hostname", timeout=5), "Unable to solve host \"ohous.se\": No address associated with hostname 안내문구의 토스트 위젯이 노출되었다 사라지지 않았습니다.")

    # LOGIN_012-5: Test Step - 기기의 인터넷 네트워크 연결 기능 on
    app_drawer.enable_network()
    assert app_drawer.is_network_connected(), "네트워크가 연결되지 않았습니다."

    # LOGIN_012-6: Test Step - 이메일 입력란에 보유한 계정의 이메일 text 입력
    login_page_by_email.clear_text_android(login_page_by_email.ID_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.ID_INPUT_FIELD, config.login_id)

    # LOGIN_012-7: Test Step - 비밀번호 입력란에 보유한 계정의 비밀번호 text 입력
    login_page_by_email.clear_text_android(login_page_by_email.PASSWORD_INPUT_FIELD)
    login_page_by_email.type(login_page_by_email.PASSWORD_INPUT_FIELD, config.login_password)

    # LOGIN_012-8: Test Step - [로그인하기] 로그인 버튼 탭
    login_page_by_email.click(login_page_by_email.LOGIN_BUTTON)

    # LOGIN_012-6: Assertion - 로그인 성공하여 오늘의집 메인 페이지가 10초 이내에 노출됨
    main_home_page = MainHomePage(driver)
    check.is_true(main_home_page.is_main_home_page_loaded(timeout=10), "오늘의집 메인 홈페이지가 10초 이내에 노출되지 않았습니다.")

    print(f"TEST {test_name} COMPLETED")


# LOGIN_013: 이미 로그인된 상태에서 앱 재실행 동작 시 메인 홈페이지 노출 확인
@pytest.mark.parametrize("test_name", ["LOGIN_013"])    
@pytest.mark.p3
def test_login_page_email_login_app_restart(test_name, driver):
    test_id = test_name

    # Pre Processing: 이미 가입된 계정으로 로그인되어 앱 실행된 상태
    # LOGIN_012에서 로그인되어 메인 홈페이지 진입한 상태

    # LOGIN_013-1: Test Step - 앱 종료
    app_drawer = AppDrawerPage(driver)
    assert app_drawer.terminate_all_apps(), "앱을 종료하지 못했습니다."

    # LOGIN_013-2: Test Step - 앱 아이콘 탭하여 앱 실행
    assert app_drawer.launch_ohous_app(), "오늘의집 앱 실행에 실패했습니다."

    # LOGIN_013-2: Assertion - 오늘의집 메인 페이지가 10초 이내에 노출됨
    main_home_page = MainHomePage(driver)
    check.is_true(main_home_page.is_main_home_page_loaded(timeout=10), "오늘의집 메인 홈페이지가 10초 이내에 노출되지 않았습니다.")

    print(f"TEST {test_name} COMPLETED")
"""
pytest 공통 fixture 정의
이 파일의 fixture는 tests 디렉토리 내의 모든 테스트에서 자동으로 사용 가능합니다.
"""
import time
import logging
import pytest
from src.driver import create_driver

# TRACE 레벨 추가 (DEBUG보다 낮은 레벨)
TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, "TRACE")

def trace(self, message, *args, **kws):
    """TRACE 레벨 로깅 메서드 추가"""
    if self.isEnabledFor(TRACE_LEVEL):
        self._log(TRACE_LEVEL, message, args, **kws)

logging.Logger.trace = trace

# selenium webdriver 관련 로거 설정
# pytest의 --log-cli-level 설정을 따르도록 propagate=True로 설정
selenium_loggers = [
    'selenium.webdriver.remote.remote_connection',
    'selenium.webdriver.common.service',
    'selenium.webdriver.common.selenium_manager',
    'urllib3.connectionpool',
]

# DEBUG 레벨로 설정하되, pytest의 로깅 시스템을 따르도록 설정
# --log-cli-level=DEBUG로 실행하면 DEBUG 이상만 출력됨
for logger_name in selenium_loggers:
    logger = logging.getLogger(logger_name)
    # DEBUG 레벨로 설정 (TRACE가 아닌)
    logger.setLevel(logging.DEBUG)
    # pytest의 로깅 시스템을 따르도록 propagate=True 설정
    # 별도 핸들러를 추가하지 않고 pytest의 핸들러를 사용
    logger.propagate = True
    # 기존에 추가된 핸들러가 있다면 제거 (pytest가 관리하도록)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)


@pytest.fixture(scope="function")
def driver():
    """
    Appium WebDriver를 생성하고 정리하는 fixture (일반용)
    
    각 테스트마다 드라이버를 생성하고 테스트 종료 후 정리합니다.
    앱을 실행하지 않고 드라이버만 생성합니다.
    
    Yields:
        webdriver.Remote: Appium WebDriver 인스턴스
        
    Example:
        def test_example(driver):
            # driver를 사용하여 테스트 수행
            driver.find_element(...)
    """
    # 앱 실행 없이 드라이버 생성
    driver = create_driver(skip_app_launch=True)
    
    yield driver
    
    driver.quit()


@pytest.fixture(scope="function")
def driver_playstore():
    """
    Appium WebDriver를 생성하고 플레이 스토어를 실행하는 fixture
    
    test_install_app.py에서만 사용합니다.
    플레이 스토어 앱을 자동으로 실행합니다.
    
    Yields:
        webdriver.Remote: Appium WebDriver 인스턴스
        
    Example:
        def test_install_app(driver_playstore):
            # 플레이 스토어가 이미 실행된 상태
            driver_playstore.find_element(...)
    """
    # 앱 실행 없이 드라이버 생성
    driver = create_driver(skip_app_launch=True)
    # 플레이 스토어 앱 실행
    driver.activate_app("com.android.vending")
    # 플레이 스토어가 완전히 로드될 때까지 대기
    time.sleep(3)
    
    yield driver
    
    driver.quit()


@pytest.fixture(scope="function")
def driver_without_app_launch():
    """
    앱 실행 없이 드라이버만 생성하는 fixture
    
    특정 앱을 직접 제어하고 싶을 때 사용합니다.
    
    Yields:
        webdriver.Remote: Appium WebDriver 인스턴스
        
    Example:
        def test_custom_app(driver_without_app_launch):
            driver = driver_without_app_launch
            driver.activate_app("com.example.app")
            # 테스트 수행
    """
    driver = create_driver(skip_app_launch=True)
    
    yield driver
    
    driver.quit()


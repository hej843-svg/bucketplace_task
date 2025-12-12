import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from src.pages.base_page import BasePage

class SearchResultsPage(BasePage):
    # 검색 결과 페이지에서 오늘의집 앱을 찾는 locator (여러 옵션)
    OHOUS_APP_OPTIONS = [
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("오늘의집 - 라이프스타일 슈퍼앱 BUCKETPLACE ")'),
        (AppiumBy.XPATH, "//android.widget.TextView[contains(@text,'오늘의집')]"),
    ]
    # 앱 상세 페이지의 설치 버튼 locator (여러 옵션)
    INSTALL_BUTTON_OPTIONS = [
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.Button").instance(1)'),
        (AppiumBy.XPATH, "//androidx.compose.ui.platform.ComposeView[@resource-id='com.android.vending:id/0_resource_name_obfuscated']/android.view.View/android.view.View[1]/android.view.View/android.view.View/android.view.View/android.view.View[1]/android.view.View[2]/android.widget.Button")
    ]

    def __init__(self, driver):
        super().__init__(driver)

    def wait_for_search_results(self, timeout=10):
        """
        검색 결과 페이지가 로드될 때까지 대기합니다.
        """
        import time
        for _ in range(timeout):
            try:
                # 검색 결과가 나타났는지 확인 (오늘의집 텍스트가 있는지 확인)
                for locator in self.OHOUS_APP_OPTIONS[:2]:  # 처음 두 개만 빠르게 체크
                    try:
                        element = self.driver.find_element(*locator)
                        if element and element.is_displayed():
                            return True
                    except NoSuchElementException:
                        continue
            except Exception:
                pass
            time.sleep(1)
        return False

    def select_ohous(self, max_retries=3):
        """
        검색 결과에서 오늘의집 앱을 선택하고 앱 상세 페이지로 이동합니다.
        """
        # 검색 결과 페이지가 로드될 때까지 대기
        if not self.wait_for_search_results(timeout=10):
            raise TimeoutException("검색 결과 페이지가 로드되지 않았습니다.")
        
        # 시스템 팝업 처리
        self.handle_system_popup()
        time.sleep(1)
        
        # 오늘의집 앱 찾기 및 클릭
        for attempt in range(max_retries):
            for locator in self.OHOUS_APP_OPTIONS:
                try:
                    ohous_app = self.wait_for_clickable(locator, timeout=5)
                    if ohous_app:
                        ohous_app.click()
                        # 앱 상세 페이지로 이동할 때까지 대기
                        time.sleep(3)
                        # 시스템 팝업 처리
                        self.handle_system_popup()
                        # 앱 상세 페이지가 로드되었는지 확인 (설치 버튼이 나타날 때까지 대기)
                        self.wait_for_app_detail_page(timeout=10)
                        return
                except (TimeoutException, NoSuchElementException):
                    continue
            
            if attempt < max_retries - 1:
                # 스크롤 후 재시도
                try:
                    self.scroll_to_text("오늘의집")
                    time.sleep(1)
                except Exception:
                    pass
                continue
            else:
                raise TimeoutException("검색 결과에서 '오늘의집' 앱을 찾을 수 없습니다.")
    
    def wait_for_app_detail_page(self, timeout=10):
        """
        앱 상세 페이지가 로드될 때까지 대기합니다.
        설치 버튼이 나타나는지 확인합니다.
        """
        for _ in range(timeout):
            try:
                # 설치 버튼이 나타났는지 확인
                for locator in self.INSTALL_BUTTON_OPTIONS:
                    try:
                        element = self.driver.find_element(*locator)
                        if element and element.is_displayed():
                            return True
                    except NoSuchElementException:
                        continue
            except Exception:
                pass
            time.sleep(1)
        return False

    def install_app(self, max_retries=3):
        """
        앱 상세 페이지에서 설치 버튼을 클릭합니다.
        """
        # 시스템 팝업 처리
        self.handle_system_popup()
        time.sleep(1)
        
        # 앱 상세 페이지가 로드되었는지 확인
        if not self.wait_for_app_detail_page(timeout=5):
            raise TimeoutException("앱 상세 페이지가 로드되지 않았습니다.")
        
        # 설치 버튼 찾기 및 클릭
        for attempt in range(max_retries):
            for locator in self.INSTALL_BUTTON_OPTIONS:
                try:
                    install_button = self.wait_for_clickable(locator, timeout=5)
                    if install_button:
                        install_button.click()
                        time.sleep(1)  # 설치 시작 대기
                        return
                except (TimeoutException, NoSuchElementException):
                    continue
            
            if attempt < max_retries - 1:
                # 시스템 팝업 처리 후 재시도
                self.handle_system_popup()
                time.sleep(1)
                continue
            else:
                raise TimeoutException("앱 상세 페이지에서 설치 버튼을 찾을 수 없습니다.")
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from src.pages.base_page import BasePage

class PlayStorePage(BasePage):
    """플레이 스토어 페이지를 제어하는 클래스"""
    
    # 하단의 검색 아이콘 버튼, 검색 영역 TextView, 검색 입력 필드 EditText 찾기
    SEARCH_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.ImageView").instance(3)')
    # 검색 영역 TextView (클릭 가능)
    SEARCH_TEXTVIEW_OPTIONS = [
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("앱 및 게임 검색")'),
        (AppiumBy.XPATH, "//android.widget.TextView[@text='앱 및 게임 검색']"),
    ]
    # 검색 입력 필드 EditText (TextView 클릭 후 나타남)
    SEARCH_EDIT_TEXT_OPTIONS = [
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.EditText")'),
        (AppiumBy.XPATH, "//android.widget.EditText"),
    ]
    # 검색 실행 버튼 (키보드의 검색 버튼 또는 검색 아이콘)
    SEARCH_SUBMIT_OPTIONS = [
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("검색")'),
        (AppiumBy.XPATH, "//android.widget.Button[contains(@content-desc,'검색')]"),
        (AppiumBy.XPATH, "//android.widget.ImageButton[contains(@content-desc,'검색')]"),
    ]
    # 검색 결과 페이지 확인용 locator
    SEARCH_RESULTS_INDICATOR = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text,'오늘의집')]")

    def __init__(self, driver):
        super().__init__(driver)

    def search_app(self, app_name, max_retries=3):
        """
        앱 검색을 시도합니다. 시스템 팝업이 나타나면 처리하고 재시도합니다.
        base_page의 wait 메서드를 활용하여 불필요한 대기 시간을 최소화합니다.
        
        Args:
            app_name: 검색할 앱 이름
            max_retries: 최대 재시도 횟수
        """
        for attempt in range(max_retries):
            try:
                # 시스템 팝업이 있을 때만 처리
                if self._check_popup_exists()[0]:
                    self.handle_system_popup()
                
                self._open_search_screen()
                self._click_search_textview()
                search_input = self._find_search_input_field()
                self._enter_search_query(search_input, app_name)
                self._execute_search(search_input)
                self._wait_for_search_results()
                
                # 시스템 팝업이 있을 때만 처리
                if self._check_popup_exists()[0]:
                    self.handle_system_popup()
                
                return
                
            except (TimeoutException, NoSuchElementException) as e:
                if attempt < max_retries - 1:
                    self._restart_playstore()
                    continue
                else:
                    raise Exception(f"검색 실패 (최대 재시도 횟수 초과): {e}")
    
    def _open_search_screen(self):
        """
        검색 화면을 엽니다. 검색 버튼을 클릭합니다.
        
        Raises:
            TimeoutException: 검색 버튼을 찾을 수 없을 때
        """
        self.wait_for_clickable(self.SEARCH_BUTTON, timeout=10)
        self.click(self.SEARCH_BUTTON)
        # 시스템 팝업이 있을 때만 처리
        if self._check_popup_exists()[0]:
            self.handle_system_popup()
    
    def _click_search_textview(self):
        """
        검색 영역 TextView를 찾아서 클릭합니다.
        
        Raises:
            TimeoutException: 검색 영역 TextView를 찾을 수 없을 때
        """
        search_textview = None
        for locator in self.SEARCH_TEXTVIEW_OPTIONS:
            try:
                search_textview = self.wait_for_clickable(locator, timeout=5)
                if search_textview:
                    break
            except (TimeoutException, NoSuchElementException):
                continue
        
        if not search_textview:
            raise TimeoutException("검색 영역(TextView)을 찾을 수 없습니다.")
        
        search_textview.click()
        # 시스템 팝업이 있을 때만 처리
        if self._check_popup_exists()[0]:
            self.handle_system_popup()
    
    def _find_search_input_field(self):
        """
        검색 입력 필드(EditText)를 찾습니다.
        
        Returns:
            WebElement: 검색 입력 필드 요소
            
        Raises:
            TimeoutException: 검색 입력 필드를 찾을 수 없을 때
        """
        for locator in self.SEARCH_EDIT_TEXT_OPTIONS:
            try:
                search_input = self.wait_for_visible(locator, timeout=5)
                if search_input:
                    return search_input
            except (TimeoutException, NoSuchElementException):
                continue
        
        # 마지막 시도: 모든 EditText 중 첫 번째 것 사용
        try:
            edit_texts = self.driver.find_elements(
                AppiumBy.ANDROID_UIAUTOMATOR, 
                'new UiSelector().className("android.widget.EditText")'
            )
            if edit_texts and len(edit_texts) > 0:
                return edit_texts[0]
            else:
                raise TimeoutException("검색 입력 필드(EditText)를 찾을 수 없습니다.")
        except Exception as e:
            raise TimeoutException(f"검색 입력 필드(EditText)를 찾을 수 없습니다: {e}")
    
    def _enter_search_query(self, search_input, app_name):
        """
        검색 입력 필드에 검색어를 입력합니다.
        
        Args:
            search_input: 검색 입력 필드 WebElement
            app_name: 검색할 앱 이름
        """
        search_input.clear()
        search_input.send_keys(app_name)
    
    def _execute_search(self, search_input):
        """
        검색을 실행합니다. 여러 방법을 시도합니다.
        
        Args:
            search_input: 검색 입력 필드 WebElement
        """
        search_executed = False
        
        # 방법 1: Android KEYCODE_ENTER 사용
        try:
            self.driver.press_keycode(66)  # KEYCODE_ENTER
            search_executed = True
        except Exception:
            pass
        
        # 방법 2: 검색 버튼 찾아서 클릭
        if not search_executed:
            for locator in self.SEARCH_SUBMIT_OPTIONS:
                try:
                    search_button = self.wait_for_clickable(locator, timeout=2)
                    if search_button:
                        search_button.click()
                        search_executed = True
                        break
                except (TimeoutException, NoSuchElementException):
                    continue
        
        # 방법 3: 엔터 키 재시도
        if not search_executed:
            try:
                search_input.send_keys("\n")
            except Exception:
                pass
    
    def _wait_for_search_results(self, timeout=10):
        """
        검색 결과 페이지가 로드될 때까지 대기합니다.
        
        Args:
            timeout: 최대 대기 시간 (초)
        """
        try:
            self.wait_for_present(self.SEARCH_RESULTS_INDICATOR, timeout=timeout)
        except TimeoutException:
            # 검색 결과가 없을 수도 있으므로 계속 진행
            pass
    
    def _restart_playstore(self):
        """
        플레이 스토어 앱을 재시작합니다. 재시도 시 사용됩니다.
        """
        # 시스템 팝업이 있을 때만 처리
        if self._check_popup_exists()[0]:
            self.handle_system_popup()
        
        self.driver.activate_app("com.android.vending")
        # 검색 버튼이 나타날 때까지 대기 (앱 재시작 확인)
        try:
            self.wait_for_clickable(self.SEARCH_BUTTON, timeout=10)
        except TimeoutException:
            pass  # 재시도 루프에서 다시 시도
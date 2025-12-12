from appium.webdriver.common.appiumby import AppiumBy
from src.config.settings import load_config
from src.pages.base_page import BasePage
import pytest_check as check
import logging
import time

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class LoginPageByEmail(BasePage):
    """이메일로 로그인 페이지를 제어하는 클래스"""
    
    # 이메일로 로그인 페이지의 필수 요소 locator
    BACK_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("net.bucketplace:id/backIcon")')
    TITLE_TEXT = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("net.bucketplace:id/title")')
    # ID_INPUT_FIELD: 여러 locator 옵션을 시도 (placeholder 텍스트가 사라질 수 있음)
    ID_INPUT_FIELD = (AppiumBy.XPATH, '(//android.widget.AutoCompleteTextView[@resource-id="net.bucketplace:id/inputField"])[1]')
    # PASSWORD_INPUT_FIELD: 여러 locator 옵션을 시도 (placeholder 텍스트가 사라질 수 있음)
    PASSWORD_INPUT_FIELD = (AppiumBy.XPATH, '(//android.widget.AutoCompleteTextView[@resource-id="net.bucketplace:id/inputField"])[2]')
    LOGIN_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("net.bucketplace:id/loginButton")')
    PASSWORD_FINDING_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("net.bucketplace:id/passwordFindingButton")')

    EMAIL_INPUT_EMPTY_TOAST_WIDGET = (AppiumBy.XPATH, "//android.widget.Toast[@text=\"이메일을 입력해주세요.\"]")
    PASSWORD_INPUT_EMPTY_TOAST_WIDGET = (AppiumBy.XPATH, "//android.widget.Toast[@text=\"비밀번호를 입력해주세요.\"]")

    LOGIN_LOADING_POPUP_WIDGET = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("로그인 중입니다.")')
    LOGIN_FAILED_TEXT_WIDGET = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("10번 실패하면 10분간 로그인이 제한돼요.")')

    def __init__(self, driver):
        super().__init__(driver)
    
    def are_email_login_elements_present(self, timeout=5):
        """
        이메일로 로그인 페이지의 필수 요소들이 모두 있는지 확인합니다.
        check 방식을 사용하여 실패해도 다음 step을 수행할 수 있습니다.
        
        Args:
            timeout: 각 요소를 찾기 위한 최대 대기 시간 (초)
            
        Returns:
            bool: 모든 필수 요소가 있으면 True, 하나라도 없으면 False
        """
        
        # 먼저 앱이 실행 중인지 확인 (앱이 종료되지 않았는지 확인)
        try:
            config = load_config()
            app_package = config.app_package
            current_package = self.driver.current_package
            if current_package != app_package:
                check.fail(f"앱이 실행 중이 아닙니다. 현재 패키지: {current_package}, 예상 패키지: {app_package}")
                return False
        except Exception as e:
            check.fail(f"앱 실행 상태 확인 실패: {e}")
            return False
        
        # 각 요소에 대한 여러 locator 옵션 정의
        elements_to_check = [
            ("BACK_BUTTON", [
                self.BACK_BUTTON,
                (AppiumBy.XPATH, '//android.widget.ImageView[@resource-id="net.bucketplace:id/backIcon"]'),
            ]),
            ("TITLE_TEXT", [
                self.TITLE_TEXT,
                (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="net.bucketplace:id/title"]'),
            ]),
            ("ID_INPUT_FIELD", [
                self.ID_INPUT_FIELD,
                (AppiumBy.XPATH, '(//android.widget.AutoCompleteTextView[@resource-id="net.bucketplace:id/inputField"])[1]'),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("이메일")'),
                (AppiumBy.XPATH, '//android.widget.AutoCompleteTextView[@resource-id="net.bucketplace:id/inputField" and @text="이메일"]'),
            ]),
            ("PASSWORD_INPUT_FIELD", [
                self.PASSWORD_INPUT_FIELD,
                (AppiumBy.XPATH, '(//android.widget.AutoCompleteTextView[@resource-id="net.bucketplace:id/inputField"])[2]'),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("비밀번호")'),
                (AppiumBy.XPATH, '//android.widget.AutoCompleteTextView[@resource-id="net.bucketplace:id/inputField" and @text="비밀번호"]'),
            ]),
            ("LOGIN_BUTTON", [
                self.LOGIN_BUTTON,
                (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="net.bucketplace:id/loginButton"]'),
            ]),
            ("PASSWORD_FINDING_BUTTON", [
                self.PASSWORD_FINDING_BUTTON,
                (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="net.bucketplace:id/passwordFindingButton"]'),
            ]),
        ]
        
        all_passed = True
        
        # 각 요소를 여러 locator 옵션으로 시도하여 확인
        for element_name, locator_options in elements_to_check:
            element_found = False
            found_element = None
            
            # 여러 locator 옵션을 순차적으로 시도
            for locator in locator_options:
                try:
                    # 먼저 is_element_present로 빠르게 확인
                    if self.is_element_present(locator, timeout=1):
                        # wait_for_visible로 다시 확인하여 확실하게 검증
                        found_element = self.wait_for_visible(locator, timeout=2)
                        element_found = True
                        break
                except Exception:
                    continue
            
            # 요소를 찾았는지 확인
            check.is_true(element_found, f"{element_name} 요소가 존재하지 않습니다.")
            if not element_found:
                all_passed = False

        # TITLE_TEXT의 텍스트가 "이메일 로그인"인지 확인
        title_text_found = False
        title_text_value = None
        title_text_locators = [
            self.TITLE_TEXT,
            (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="net.bucketplace:id/title"]')
        ]
        
        for locator in title_text_locators:
            try:
                element = self.wait_for_visible(locator, timeout=2)
                title_text_value = element.text or element.get_attribute("content-desc") or ""
                if title_text_value:
                    title_text_found = True
                    break
            except Exception:
                continue
        
        if title_text_found:
            check.equal(title_text_value, "이메일 로그인", f"TITLE_TEXT의 텍스트가 '이메일 로그인'이 아닙니다. 실제 텍스트: '{title_text_value}'")
            if title_text_value != "이메일 로그인":
                all_passed = False
        else:
            check.fail("TITLE_TEXT 요소를 찾을 수 없습니다.")
            all_passed = False
        
        # ID_INPUT_FIELD의 텍스트가 "이메일"인지 확인
        id_input_field_found = False
        id_input_field_text = None
        id_input_field_locators = [
            self.ID_INPUT_FIELD,
            (AppiumBy.XPATH, '//android.widget.AutoCompleteTextView[@resource-id="net.bucketplace:id/inputField" and @text="이메일"]')
        ]
        
        for locator in id_input_field_locators:
            try:
                element = self.wait_for_visible(locator, timeout=2)
                email_login_text = element.text or element.get_attribute("content-desc") or ""
                if email_login_text:
                    email_login_found = True
                    break
            except Exception:
                continue
        
        if email_login_found:
            check.equal(email_login_text, "이메일", f"ID_INPUT_FIELD의 텍스트가 '이메일'이 아닙니다. 실제 텍스트: '{email_login_text}'")
            if email_login_text != "이메일":
                all_passed = False
        else:
            check.fail("ID_INPUT_FIELD 요소를 찾을 수 없습니다.")
            all_passed = False

        #PASSWORD_INPUT_FIELD의 텍스트가 "비밀번호"인지 확인
        password_input_field_found = False
        password_input_field_text = None
        password_input_field_locators = [
            self.PASSWORD_INPUT_FIELD,
            (AppiumBy.XPATH, '//android.widget.AutoCompleteTextView[@resource-id="net.bucketplace:id/inputField" and @text="비밀번호"]')
        ]
        
        for locator in password_input_field_locators:
            try:
                element = self.wait_for_visible(locator, timeout=2)
                password_input_field_text = element.text or element.get_attribute("content-desc") or ""
                if password_input_field_text:
                    password_input_field_found = True
                    break
            except Exception:
                continue
        
        if password_input_field_found:
            check.equal(password_input_field_text, "비밀번호", f"PASSWORD_INPUT_FIELD의 텍스트가 '비밀번호'가 아닙니다. 실제 텍스트: '{password_input_field_text}'")
            if password_input_field_text != "비밀번호":
                all_passed = False
        else:
            check.fail("PASSWORD_INPUT_FIELD 요소를 찾을 수 없습니다.")
            all_passed = False
        
        # LOGIN_BUTTON의 텍스트가 "로그인하기"인지 확인
        login_button_found = False
        login_button_text = None
        login_button_locators = [
            self.LOGIN_BUTTON,
            (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="net.bucketplace:id/loginButton"]')
        ]
        
        for locator in login_button_locators:
            try:
                element = self.wait_for_visible(locator, timeout=2)
                login_button_text = element.text or element.get_attribute("content-desc") or ""
                if login_button_text:
                    login_button_found = True
                    break
            except Exception:
                continue
        
        if login_button_found:
            check.equal(login_button_text, "로그인하기", f"LOGIN_BUTTON의 텍스트가 '로그인하기'가 아닙니다. 실제 텍스트: '{login_button_text}'")
            if login_button_text != "로그인하기":
                all_passed = False
        else:
            check.fail("LOGIN_BUTTON 요소를 찾을 수 없습니다.")
            all_passed = False

        # PASSWORD_FINDING_BUTTON의 텍스트가 "비밀번호 재설정"인지 확인
        password_finding_button_found = False
        password_finding_button_text = None
        password_finding_button_locators = [
            self.PASSWORD_FINDING_BUTTON,
            (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="net.bucketplace:id/passwordFindingButton"]')
        ]
        
        for locator in password_finding_button_locators:
            try:
                element = self.wait_for_visible(locator, timeout=2)
                password_finding_button_text = element.text or element.get_attribute("content-desc") or ""
                if password_finding_button_text:
                    password_finding_button_found = True
                    break
            except Exception:
                continue
        
        if password_finding_button_found:
            check.equal(password_finding_button_text, "비밀번호 재설정", f"ANONYMOUS_ORDER_CHECK_BUTTON의 텍스트가 '비밀번호 재설정'이 아닙니다. 실제 텍스트: '{password_finding_button_text}'")
            if password_finding_button_text != "비밀번호 재설정":
                all_passed = False
        else:
            check.fail("PASSWORD_FINDING_BUTTON 요소를 찾을 수 없습니다.")
            all_passed = False
        
        return all_passed
    
    def is_email_login_page_loaded(self, timeout=10):
        """
        이메일로 로그인 페이지가 로드되었는지 확인합니다.
        이메일로 로그인 페이지의 요소들이 나타날 때까지 대기합니다.
        
        Args:
            timeout: 최대 대기 시간 (초)
            
        Returns:
            bool: 이메일로 로그인 페이지가 로드되었으면 True
        """
        
        try:
            # 이메일로 로그인 페이지의 핵심 요소들
            key_elements = [
                ("TITLE_TEXT", self.TITLE_TEXT),
                ("ID_INPUT_FIELD", self.ID_INPUT_FIELD),
                ("PASSWORD_INPUT_FIELD", self.PASSWORD_INPUT_FIELD),
                ("LOGIN_BUTTON", self.LOGIN_BUTTON),
                ("PASSWORD_FINDING_BUTTON", self.PASSWORD_FINDING_BUTTON),
            ]
            
            # 먼저 이메일로 로그인 페이지가 이미 로드되어 있는지 빠르게 확인
            all_elements = key_elements
            for element_name, locator in all_elements:
                try:
                    if self.is_element_present(locator, timeout=1):
                        return True
                except Exception:
                    continue
            
            # 이메일로 로그인 페이지의 핵심 요소들이 나타날 때까지 대기
            # 여러 요소 중 하나라도 나타나면 이메일로 로그인 페이지가 로드된 것으로 간주
            start_time = time.time()
            while time.time() - start_time < timeout:
                found_elements = []
                # 모든 요소 확인 (key_elements)
                for element_name, locator in all_elements:
                    try:
                        # 먼저 is_element_present로 빠르게 확인
                        if self.is_element_present(locator, timeout=0.5):
                            found_elements.append(element_name)
                            # wait_for_visible로 다시 확인하여 확실하게 검증
                            try:
                                self.wait_for_visible(locator, timeout=2)
                                return True
                            except Exception:
                                pass
                    except Exception:
                        continue
                
                time.sleep(0.5)  # 0.5초마다 확인하여 더 빠르게 반응
            
            return False
        except Exception:
            return False
    
    def check_specific_element(self, locator, timeout=5):
        """
        특정 요소가 있는지 확인합니다.
        
        Args:
            locator: 확인할 요소의 locator (tuple)
            timeout: 최대 대기 시간 (초)
            
        Returns:
            bool: 요소가 있으면 True, 없으면 False
        """
        return self.is_element_present(locator, timeout=timeout)
    
    def attempt_login_multiple_times(self, email, password, count=1):
        """
        로그인을 여러 번 시도하는 함수입니다.
        이메일과 비밀번호를 입력하고 로그인 버튼을 클릭하는 과정을 반복합니다.

        Args:
            email: 입력할 이메일 주소
            password: 입력할 비밀번호
            count: 로그인 시도 횟수 (기본값: 1)

        Returns:
            None
        """
        import time
        
        for i in range(count):
            # 이메일 입력란 초기화 및 입력
            self.clear_text_android(self.ID_INPUT_FIELD)
            self.type(self.ID_INPUT_FIELD, email)
            
            # 비밀번호 입력란 초기화 및 입력
            self.clear_text_android(self.PASSWORD_INPUT_FIELD)
            self.type(self.PASSWORD_INPUT_FIELD, password)
            
            # 로그인 버튼 클릭
            self.click(self.LOGIN_BUTTON)
            
            # 마지막 시도가 아니면 다음 시도를 위해 짧은 대기
            if i < count - 1:
                time.sleep(0.5)  # 다음 시도 전 짧은 대기




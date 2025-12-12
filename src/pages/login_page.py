from appium.webdriver.common.appiumby import AppiumBy
from src.config.settings import load_config
from src.pages.base_page import BasePage
import pytest_check as check
import logging
import time

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class LoginPage(BasePage):
    """로그인 페이지를 제어하는 클래스"""
    
    # 로그인 페이지의 필수 요소 locator
    BUCKETPLACE_LOGO = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("net.bucketplace:id/logo")')  # 오늘의집 로고 이미지뷰
    GUIDE_IMAGE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("net.bucketplace:id/guideImage")')  # 오늘의집 가이드 이미지뷰
    KAKAO_LOGIN_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("net.bucketplace:id/kakaoLoginButton")')  # 카카오 로그인 버튼
    KAKAO_LOGO = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("net.bucketplace:id/loginIcon")')  # 카카오 로고 이미지뷰
    KAKAO_LOGIN_TEXT = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("net.bucketplace:id/loginText")')  # 카카오 로그인 텍스트
    NAVER_LOGIN_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("net.bucketplace:id/naverLoginButton")')  # 네이버 로그인 버튼
    FACEBOOK_LOGIN_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("net.bucketplace:id/facebookLoginButton")')  # 페이스북 로그인 버튼
    APPLE_LOGIN_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("net.bucketplace:id/appleLoginButton")')  # Apple 로그인 버튼
    IMAIL_LOGIN_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("net.bucketplace:id/emailLogInText")')  # IMAIL 로그인 버튼
    IMAIL_SIGNUP_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("net.bucketplace:id/emailSignUpText")')  # IMAIL 회원가입 버튼
    CUSTOMER_SERVICE_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("net.bucketplace:id/customerServiceText")')  # 고객센터 버튼
    ANONYMOUS_ORDER_CHECK_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("net.bucketplace:id/anonymousOrderCheck")')  # 비회원 주문 조회 버튼

    def __init__(self, driver):
        super().__init__(driver)
    
    def are_login_elements_present(self, timeout=5):
        """
        로그인 페이지의 필수 요소들이 모두 있는지 확인합니다.
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
            ("BUCKETPLACE_LOGO", [
                self.BUCKETPLACE_LOGO,
                (AppiumBy.XPATH, '//android.widget.ImageView[@resource-id="net.bucketplace:id/logo"]'),
            ]),
            ("GUIDE_IMAGE", [
                self.GUIDE_IMAGE,
                (AppiumBy.XPATH, '//android.widget.ImageView[@resource-id="net.bucketplace:id/guideImage"]'),
            ]),
            ("KAKAO_LOGIN_BUTTON", [
                self.KAKAO_LOGIN_BUTTON,
                (AppiumBy.XPATH, '//android.view.ViewGroup[@resource-id="net.bucketplace:id/kakaoLoginButton"]'),
            ]),
            ("NAVER_LOGIN_BUTTON", [
                self.NAVER_LOGIN_BUTTON,
                (AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="네이버로 가입하기"]'),
            ]),
            ("FACEBOOK_LOGIN_BUTTON", [
                self.FACEBOOK_LOGIN_BUTTON,
                (AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="페이스북으로 가입하기"]'),
            ]),
            ("APPLE_LOGIN_BUTTON", [
                self.APPLE_LOGIN_BUTTON,
                (AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="애플로그인으로 가입하기"]'),
            ]),
            ("IMAIL_LOGIN_BUTTON", [
                self.IMAIL_LOGIN_BUTTON,
                (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="net.bucketplace:id/emailLogInText"]'),
            ]),
            ("IMAIL_SIGNUP_BUTTON", [
                self.IMAIL_SIGNUP_BUTTON,
                (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="net.bucketplace:id/emailSignUpText"]'),
            ]),
            ("CUSTOMER_SERVICE_BUTTON", [
                self.CUSTOMER_SERVICE_BUTTON,
                (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="net.bucketplace:id/customerServiceText"]'),
            ]),
            ("ANONYMOUS_ORDER_CHECK_BUTTON", [
                self.ANONYMOUS_ORDER_CHECK_BUTTON,
                (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="net.bucketplace:id/anonymousOrderCheck"]'),
            ])
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

        # KAKAO_LOGIN_TEXT의 텍스트가 "카카오톡으로 계속하기"인지 확인
        kakao_text_found = False
        kakao_text_value = None
        kakao_text_locators = [
            self.KAKAO_LOGIN_TEXT,
            (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="net.bucketplace:id/loginText"]')
        ]
        
        for locator in kakao_text_locators:
            try:
                element = self.wait_for_visible(locator, timeout=2)
                kakao_text_value = element.text or element.get_attribute("content-desc") or ""
                if kakao_text_value:
                    kakao_text_found = True
                    break
            except Exception:
                continue
        
        if kakao_text_found:
            check.equal(kakao_text_value, "카카오톡으로 계속하기", f"KAKAO_LOGIN_TEXT의 텍스트가 '카카오톡으로 계속하기'이 아닙니다. 실제 텍스트: '{kakao_text_value}'")
            if kakao_text_value != "카카오톡으로 계속하기":
                all_passed = False
        else:
            check.fail("KAKAO_LOGIN_TEXT 요소를 찾을 수 없습니다.")
            all_passed = False
        
        # IMAIL_LOGIN_BUTTON의 텍스트가 "이메일로 로그인"인지 확인
        email_login_found = False
        email_login_text = None
        email_login_locators = [
            self.IMAIL_LOGIN_BUTTON,
            (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="net.bucketplace:id/emailLogInText"]')
        ]
        
        for locator in email_login_locators:
            try:
                element = self.wait_for_visible(locator, timeout=2)
                email_login_text = element.text or element.get_attribute("content-desc") or ""
                if email_login_text:
                    email_login_found = True
                    break
            except Exception:
                continue
        
        if email_login_found:
            check.equal(email_login_text, "이메일로 로그인", f"IMAIL_LOGIN_BUTTON의 텍스트가 '이메일로 로그인'이 아닙니다. 실제 텍스트: '{email_login_text}'")
            if email_login_text != "이메일로 로그인":
                all_passed = False
        else:
            check.fail("IMAIL_LOGIN_BUTTON 요소를 찾을 수 없습니다.")
            all_passed = False

        # IMAIL_SIGNUP_BUTTON의 텍스트가 "이메일로 가입"인지 확인
        email_signup_found = False
        email_signup_text = None
        email_signup_locators = [
            self.IMAIL_SIGNUP_BUTTON,
            (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="net.bucketplace:id/emailSignUpText"]')
        ]
        
        for locator in email_signup_locators:
            try:
                element = self.wait_for_visible(locator, timeout=2)
                email_signup_text = element.text or element.get_attribute("content-desc") or ""
                if email_signup_text:
                    email_signup_found = True
                    break
            except Exception:
                continue
        
        if email_signup_found:
            check.equal(email_signup_text, "이메일로 가입", f"IMAIL_SIGNUP_BUTTON의 텍스트가 '이메일로 가입'이 아닙니다. 실제 텍스트: '{email_signup_text}'")
            if email_signup_text != "이메일로 가입":
                all_passed = False
        else:
            check.fail("IMAIL_SIGNUP_BUTTON 요소를 찾을 수 없습니다.")
            all_passed = False
        
        # CUSTOMER_SERVICE_BUTTON의 텍스트가 "로그인에 문제가 있으신가요?"인지 확인
        customer_service_found = False
        customer_service_text = None
        customer_service_locators = [
            self.CUSTOMER_SERVICE_BUTTON,
            (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="net.bucketplace:id/customerServiceText"]')
        ]
        
        for locator in customer_service_locators:
            try:
                element = self.wait_for_visible(locator, timeout=2)
                customer_service_text = element.text or element.get_attribute("content-desc") or ""
                if customer_service_text:
                    customer_service_found = True
                    break
            except Exception:
                continue
        
        if customer_service_found:
            check.equal(customer_service_text, "로그인에 문제가 있으신가요?", f"CUSTOMER_SERVICE_BUTTON의 텍스트가 '로그인에 문제가 있으신가요?'가 아닙니다. 실제 텍스트: '{customer_service_text}'")
            if customer_service_text != "로그인에 문제가 있으신가요?":
                all_passed = False
        else:
            check.fail("CUSTOMER_SERVICE_BUTTON 요소를 찾을 수 없습니다.")
            all_passed = False

        # ANONYMOUS_ORDER_CHECK_BUTTON의 텍스트가 "비회원 주문 조회하기"인지 확인
        anonymous_order_found = False
        anonymous_order_text = None
        anonymous_order_locators = [
            self.ANONYMOUS_ORDER_CHECK_BUTTON,
            (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="net.bucketplace:id/anonymousOrderCheck"]')
        ]
        
        for locator in anonymous_order_locators:
            try:
                element = self.wait_for_visible(locator, timeout=2)
                anonymous_order_text = element.text or element.get_attribute("content-desc") or ""
                if anonymous_order_text:
                    anonymous_order_found = True
                    break
            except Exception:
                continue
        
        if anonymous_order_found:
            check.equal(anonymous_order_text, "비회원 주문 조회하기", f"ANONYMOUS_ORDER_CHECK_BUTTON의 텍스트가 '비회원 주문 조회하기'가 아닙니다. 실제 텍스트: '{anonymous_order_text}'")
            if anonymous_order_text != "비회원 주문 조회하기":
                all_passed = False
        else:
            check.fail("ANONYMOUS_ORDER_CHECK_BUTTON 요소를 찾을 수 없습니다.")
            all_passed = False
        
        return all_passed
    
    def is_login_page_loaded(self, timeout=10):
        """
        로그인 페이지가 로드되었는지 확인합니다.
        로그인 페이지의 요소들이 나타날 때까지 대기합니다.
        
        Args:
            timeout: 최대 대기 시간 (초)
            
        Returns:
            bool: 로그인 페이지가 로드되었으면 True
        """
        
        try:
            # 로그인 페이지의 핵심 요소들 (여러 옵션 포함)
            key_elements = [
                ("BUCKETPLACE_LOGO", self.BUCKETPLACE_LOGO),
                ("GUIDE_IMAGE", self.GUIDE_IMAGE),
                ("KAKAO_LOGIN_BUTTON", self.KAKAO_LOGIN_BUTTON),
                ("IMAIL_LOGIN_BUTTON", self.IMAIL_LOGIN_BUTTON),
            ]
            
            # 추가 locator 옵션 (텍스트 기반)
            additional_elements = [
                ("IMAIL_LOGIN_BUTTON_TEXT", (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("이메일로 로그인")')),
                ("KAKAO_LOGIN_BUTTON_TEXT", (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("카카오로 로그인")')),
            ]
            
            # 먼저 로그인 페이지가 이미 로드되어 있는지 빠르게 확인
            all_elements = key_elements + additional_elements
            for element_name, locator in all_elements:
                try:
                    if self.is_element_present(locator, timeout=1):
                        return True
                except Exception:
                    continue
            
            # 로그인 페이지의 핵심 요소들이 나타날 때까지 대기
            # 여러 요소 중 하나라도 나타나면 로그인 페이지가 로드된 것으로 간주
            start_time = time.time()
            while time.time() - start_time < timeout:
                found_elements = []
                # 모든 요소 확인 (key_elements + additional_elements)
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




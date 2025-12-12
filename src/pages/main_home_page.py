from appium.webdriver.common.appiumby import AppiumBy
from src.config.settings import load_config
from src.pages.base_page import BasePage
import pytest_check as check
import logging
import time

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class MainHomePage(BasePage):
    """오늘의집 메인 홈페이지를 제어하는 클래스"""

    # 오늘의집 메인 홈페이지의 필수 요소 locator
    HOME_UP_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("홈").instance(0)')
    
    # 하단 footer
    HOME_BOTTOM_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("홈").instance(1)')
    COMMUNITY_BOTTOM_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("커뮤니티")')
    SHOPPING_BOTTOM_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("쇼핑")')
    INTERIOR_BOTTOM_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("인테리어/생활")')
    MYPAGE_BOTTOM_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("마이페이지")')

    
    def __init__(self, driver):
        super().__init__(driver)

    def are_main_home_page_elements_present(self, timeout=10):
        """
        오늘의집 메인 홈페이지의 필수 요소들이 모두 있는지 확인합니다.
        """
        return self.is_element_present(self.OHOUS_APP_ICON, timeout=timeout)
    
    def is_main_home_page_loaded(self, timeout=10):
        """
        오늘의집 메인 홈페이지가 로드되었는지 확인합니다.
        
        Args:
            timeout: 최대 대기 시간 (초)
            
        Returns:
            bool: 메인 홈페이지가 로드되었으면 True
        """

        try:
            # 메인 홈페이지의 핵심 요소들 (여러 옵션 포함)
            key_elements = [
                ("HOME_UP_BUTTON", self.HOME_UP_BUTTON),
                ("HOME_BOTTOM_BUTTON", self.HOME_BOTTOM_BUTTON),
                ("COMMUNITY_BOTTOM_BUTTON", self.COMMUNITY_BOTTOM_BUTTON),
                ("SHOPPING_BOTTOM_BUTTON", self.SHOPPING_BOTTOM_BUTTON),
                ("INTERIOR_BOTTOM_BUTTON", self.INTERIOR_BOTTOM_BUTTON),
                ("MYPAGE_BOTTOM_BUTTON", self.MYPAGE_BOTTOM_BUTTON),
            ]

            # 추가 locator 옵션 (텍스트 기반)
            additional_elements = [
                ("COMMUNITY_BOTTOM_BUTTON_TEXT", (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("커뮤니티")')),
                ("SHOPPING_BOTTOM_BUTTON_TEXT", (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("쇼핑")')),
                ("INTERIOR_BOTTOM_BUTTON_TEXT", (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("인테리어/생활")')),
                ("MYPAGE_BOTTOM_BUTTON_TEXT", (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("마이페이지")')),
            ]

            # 먼저 메인 홈페이지가 이미 로드되어 있는지 빠르게 확인
            all_elements = key_elements + additional_elements
            for element_name, locator in all_elements:
                try:
                    if self.is_element_present(locator, timeout=1):
                        return True
                except Exception:
                    continue
            
            # 메인 홈페이지의 핵심 요소들이 나타날 때까지 대기
            # 여러 요소 중 하나라도 나타나면 메인 홈페이지가 로드된 것으로 간주
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
    
    def is_google_password_manager_popup_present(self, timeout=3):
        """
        "비밀번호을(를) Google 비밀번호 관리자에 저장하시겠습니까?" 팝업이 존재하는지 확인합니다.
        
        Args:
            timeout: 팝업을 찾기 위한 최대 대기 시간 (초, 기본값: 3)
            
        Returns:
            bool: 팝업이 존재하면 True, 없으면 False
        """
        try:
            # 여러 locator 옵션 시도
            popup_locators = [
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("비밀번호을(를) Google 비밀번호 관리자에 저장하시겠습니까?")'),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("비밀번호을(를) Google 비밀번호 관리자에 저장하시겠습니까?")'),
                (AppiumBy.XPATH, '//android.widget.TextView[@text="비밀번호을(를) Google 비밀번호 관리자에 저장하시겠습니까?"]'),
                (AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "비밀번호을(를) Google 비밀번호 관리자에 저장하시겠습니까?")]'),
            ]
            
            for locator in popup_locators:
                try:
                    if self.is_element_present(locator, timeout=timeout):
                        element = self.find(locator, timeout=1)
                        if element and element.is_displayed():
                            return True
                except Exception:
                    continue
            
            return False
        except Exception as e:
            log.debug(f"Google 비밀번호 관리자 팝업 확인 중 오류 발생: {e}")
            return False
    
    def click_google_password_manager_dismiss_button(self, timeout=2):
        """
        Google 비밀번호 관리자 팝업의 "나중에" 또는 "사용 안함" 버튼을 클릭합니다.
        
        Args:
            timeout: 버튼을 찾기 위한 최대 대기 시간 (초, 기본값: 2)
            
        Returns:
            bool: 버튼을 성공적으로 클릭했으면 True, 찾지 못했거나 클릭 실패 시 False
        """
        try:
            # "나중에" 또는 "사용 안함" 두 가지 버튼 locator 옵션
            dismiss_button_locators = [
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("나중에")'),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("나중에")'),
                (AppiumBy.XPATH, '//android.widget.Button[@text="나중에"]'),
                (AppiumBy.XPATH, '//android.widget.TextView[@text="나중에"]'),
                (AppiumBy.XPATH, '//*[@text="나중에"]'),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("사용 안함")'),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("사용 안함")'),
                (AppiumBy.XPATH, '//android.widget.Button[@text="사용 안함"]'),
                (AppiumBy.XPATH, '//android.widget.TextView[@text="사용 안함"]'),
                (AppiumBy.XPATH, '//*[@text="사용 안함"]'),
            ]
            
            for button_locator in dismiss_button_locators:
                try:
                    if self.is_element_present(button_locator, timeout=timeout):
                        button = self.find(button_locator, timeout=1)
                        if button and button.is_displayed():
                            button.click()
                            import time
                            time.sleep(0.5)  # 팝업이 사라질 때까지 짧은 대기
                            log.info("Google 비밀번호 관리자 팝업에서 '나중에' 또는 '사용 안함' 버튼 클릭 완료")
                            return True
                except Exception:
                    continue
            
            log.warning("'나중에' 또는 '사용 안함' 버튼을 찾을 수 없습니다.")
            return False
        except Exception as e:
            log.debug(f"'나중에' 또는 '사용 안함' 버튼 클릭 중 오류 발생: {e}")
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
from appium.webdriver.common.appiumby import AppiumBy
from src.pages.base_page import BasePage
import pytest_check as check
import logging
import time

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class SettingPage(BasePage):
    """설정 페이지를 제어하는 클래스"""
    
    # 설정 페이지의 필수 요소 locator
    PAGE_TITLE_TEXT = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("설정").instance(1)')
    MY_INFO_MANAGEMENT_TEXT = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("내 정보 관리")')
    SETTING_TEXT = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("설정").instance(0)')
    SERVICE_INFO_TEXT = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("서비스 정보")')

    LOGOUT_TEXT_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("로그아웃")')
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def are_setting_page_elements_present(self, timeout=5):
        """
        설정 페이지의 필수 요소들이 모두 있는지 확인합니다.
        check 방식을 사용하여 실패해도 다음 step을 수행할 수 있습니다.
        
        Args:
            timeout: 각 요소를 찾기 위한 최대 대기 시간 (초)
            
        Returns:
            bool: 모든 필수 요소가 있으면 True, 하나라도 없으면 False
        """
        # TODO: 요소 확인 로직 구현
        return True
    
    def is_setting_page_loaded(self, timeout=10):
        """
        설정 페이지가 로드되었는지 확인합니다.
        설정 페이지의 요소들이 나타날 때까지 대기합니다.
        
        Args:
            timeout: 최대 대기 시간 (초)
            
        Returns:
            bool: 설정 페이지가 로드되었으면 True
        """
        
        try:
            # 설정 페이지의 핵심 요소들 (여러 옵션 포함)
            key_elements = [
                ("PAGE_TITLE_TEXT", self.PAGE_TITLE_TEXT),
                ("MY_INFO_MANAGEMENT_TEXT", self.MY_INFO_MANAGEMENT_TEXT),
                ("SETTING_TEXT", self.SETTING_TEXT),
                ("SERVICE_INFO_TEXT", self.SERVICE_INFO_TEXT),
            ]

            # 먼저 설정 페이지가 이미 로드되어 있는지 빠르게 확인
            all_elements = key_elements
            for element_name, locator in all_elements:
                try:
                    if self.is_element_present(locator, timeout=1):
                        return True
                except Exception:
                    continue

            # 설정 페이지의 핵심 요소들이 나타날 때까지 대기
            # 여러 요소 중 하나라도 나타나면 설정 페이지가 로드된 것으로 간주
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


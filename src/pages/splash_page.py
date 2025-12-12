from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from src.pages.base_page import BasePage


class SplashPage(BasePage):
    """스플래시 페이지를 제어하는 클래스"""
    
    # 스플래시 로티 요소 locator
    SPLASH_WHOLE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("net.bucketplace:id/splash_whole")')
    SPLASH_LOTTIE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("net.bucketplace:id/splash_lottie")')
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def wait_for_splash_lottie_page_loaded(self, timeout=5):
        """
        스플래시 로티 페이지가 로드되었는지 확인합니다.
        
        Args:
            timeout: 최대 대기 시간 (초)
            
        Returns:
            bool: 스플래시 로티 페이지가 로드되었으면 True
        """
        try:
            # 스플래시 로티 요소가 나타날 때까지 대기
            self.wait_for_visible(self.SPLASH_LOTTIE, timeout=timeout)
            return True
        except TimeoutException:
            return False

    def wait_for_splash_whole_page_loaded(self, timeout=5):
        """
        스플래시 전체 페이지가 로드되었는지 확인합니다.
        
        Args:
            timeout: 최대 대기 시간 (초)
            
        Returns:
            bool: 스플래시 전체 페이지가 로드되었으면 True
        """
        try:
            # 스플래시 전체 요소가 나타날 때까지 대기
            self.wait_for_visible(self.SPLASH_WHOLE, timeout=timeout)
            return True
        except TimeoutException:
            return False

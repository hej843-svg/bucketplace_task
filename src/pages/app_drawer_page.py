from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from src.pages.base_page import BasePage


class AppDrawerPage(BasePage):
    """앱 서랍 페이지를 제어하는 클래스"""
    
    # 앱 서랍 열기 버튼 locator
    APP_DRAWER_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("앱")')
    # 오늘의집 앱 아이콘 locator
    OHOUS_APP_ICON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("오늘의집")')
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def wait_for_app_installed(self, timeout=10):
        """
        앱이 설치되었는지 확인합니다.
        
        Args:
            timeout: 최대 대기 시간 (초)
            
        Returns:
            bool: 앱이 설치되어 있으면 True
        """
        try:
            # 앱 패키지가 설치되어 있는지 확인
            from src.config.settings import load_config
            config = load_config()
            app_package = config.app_package
            
            # adb를 통해 앱 설치 여부 확인
            import subprocess
            result = subprocess.run(
                ['adb', 'shell', 'pm', 'list', 'packages', app_package],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return app_package in result.stdout
        except Exception:
            return False
    
    def open_app_drawer(self):
        """
        앱 서랍을 엽니다.
        """
        # 홈 버튼 누르기
        self.driver.press_keycode(3)  # KEYCODE_HOME
        # 앱 서랍 열기 (스와이프 업 또는 앱 버튼 클릭)
        try:
            self.wait_for_clickable(self.APP_DRAWER_BUTTON, timeout=5)
            self.click(self.APP_DRAWER_BUTTON)
        except TimeoutException:
            # 앱 서랍 버튼을 찾을 수 없으면 홈 화면에서 위로 스와이프
            self.driver.swipe(500, 1500, 500, 500, 300)
    
    def launch_ohous_app(self):
        """
        오늘의집 앱을 실행합니다.
        앱 서랍을 열고 오늘의집 앱 아이콘을 클릭합니다.
        
        Returns:
            bool: 앱 실행에 성공했으면 True, 실패했으면 False
        """
        try:
            # 앱 서랍 열기
            self.open_app_drawer()
            
            # 오늘의집 앱 아이콘 클릭
            self.wait_for_clickable(self.OHOUS_APP_ICON, timeout=5)
            self.click(self.OHOUS_APP_ICON)
            
            return True
        except Exception as e:
            print(f"오늘의집 앱 실행 실패: {e}")
            return False
    
    def pre_processing_launch_ohous_app(self):
        """
        오늘의집 앱을 실행하기 위한 전처리 작업을 수행합니다.

        이미 앱이 실행되어 있다면 먼저 종료한 후 실행합니다.
        앱 서랍을 열고 오늘의집 앱 아이콘을 클릭합니다.
        앱이 정상적으로 실행되었는지 확인합니다.
        
        Returns:
            bool: 앱 실행에 성공했으면 True, 실패했으면 False
        """
        try:
            # Step 1: 이미 오늘의집 앱이 실행되어 있는지 확인하고 종료
            from src.config.settings import load_config
            config = load_config()
            app_package = config.app_package
            
            try:
                current_package = self.driver.current_package
                if current_package == app_package:
                    # 오늘의집 앱이 이미 실행 중이면 종료
                    self.terminate_all_apps(app_package)
            except Exception:
                # current_package를 확인할 수 없어도 계속 진행
                pass
            
            # Step 2: 앱 서랍 열기
            self.open_app_drawer()
            
            # Step 3: 오늘의집 앱 아이콘 클릭
            self.wait_for_clickable(self.OHOUS_APP_ICON, timeout=5)
            self.click(self.OHOUS_APP_ICON)
            
            # Step 4: 앱이 정상적으로 실행되었는지 확인
            return self.wait_for_app_running(timeout=10)
        except Exception as e:
            print(f"오늘의집 앱 실행 실패: {e}")
            return False
    
    def wait_for_app_running(self, timeout=10):
        """
        앱이 정상적으로 실행되었는지 확인합니다.
        (앱 아이콘 클릭은 호출 전에 이미 수행되어야 함)
        
        Args:
            timeout: 최대 대기 시간 (초)
            
        Returns:
            bool: 앱이 실행 중이면 True
        """
        import time
        from src.config.settings import load_config
        
        try:
            config = load_config()
            app_package = config.app_package
            
            # 앱이 실행될 때까지 대기 (current_package가 앱 패키지로 변경될 때까지)
            for _ in range(timeout):
                try:
                    current_package = self.driver.current_package
                    if current_package == app_package:
                        # 앱이 실행되었으므로 추가로 앱의 메인 화면이 로드될 때까지 짧은 대기
                        time.sleep(2)
                        return True
                except Exception:
                    pass
                time.sleep(1)
            
            return False
        except Exception:
            return False


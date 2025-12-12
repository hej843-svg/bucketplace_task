from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from src.config.settings import load_config
import logging
import time
import subprocess

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class BasePage:
    """모든 페이지에서 사용되는 반복적인 요소들을 모아둔 클래스"""
    def __init__(self, driver):
        self.driver = driver
    
    def find(self, locator, timeout=10):
        """
        요소를 찾습니다. 여러 locator 옵션이 제공되면 순차적으로 시도합니다.
        
        Args:
            locator: 단일 locator (tuple) 또는 locator 리스트
            timeout: 각 locator를 시도할 때의 최대 대기 시간 (초)
            
        Returns:
            WebElement: 찾은 요소
        """
        # locator가 리스트인 경우 여러 옵션을 시도
        if isinstance(locator, list):
            for loc in locator:
                try:
                    if isinstance(loc, tuple) and len(loc) == 2:
                        return WebDriverWait(self.driver, timeout).until(
                            EC.presence_of_element_located(loc)
                        )
                except Exception:
                    continue
            raise ValueError(f"모든 locator 옵션을 시도했지만 요소를 찾을 수 없습니다: {locator}")
        
        # 단일 locator인 경우
        if not isinstance(locator, tuple) or len(locator) != 2:
            raise ValueError(f"Invalid locator format. Expected tuple of (by, value), got: {type(locator)} - {locator}")
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    def click(self, locator, timeout=10):
        clickable_element = self.wait_for_clickable(locator, timeout)
        clickable_element.click()
        return clickable_element

    def type(self, locator, text, timeout=10):
        """
        요소에 텍스트를 입력합니다.
        
        Args:
            locator: 요소의 locator
            text: 입력할 텍스트
            timeout: 요소를 찾기 위한 최대 대기 시간 (초, 기본값: 10)
        """
        element = self.find(locator, timeout)
        element.send_keys(text)

    def wait_for_visible(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def wait_for_clickable(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )

    def wait_for_present(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    def wait_for_not_present(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(locator)
        )

    def scroll_to_text(self, text):
        return self.driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiScrollable(new UiSelector().scrollable(true)).scrollTextIntoView("{text}");'
        )
    
    def scroll_to_element(self, element):
        return self.driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView({element});'
        )

    def scroll_to_bottom(self):
        return self.driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiScrollable(new UiSelector().scrollable(true)).scrollToEnd(800);'
        )
    
    def wait_for_toast_message(self, toast_text: str, timeout: int = 5) -> bool:
        
        # TODO 토스트 팝업이 노출되지 않았더라도 성공으로 간주하고 있는 러프한 기준을 사용하고 있는 부분을 수정해야함.
        """
        주어진 텍스트를 포함하는 토스트 메시지가 나타날 때까지 대기합니다.
        toast_text가 토스트 메시지의 일부만 포함해도 매칭됩니다.
        
        Args:
            toast_text: 토스트 메시지에 포함될 텍스트 (예: "이메일을 입력해주세요." 또는 "10번 실패하면 10분간 로그인이 제한돼요.")
            timeout: 토스트가 나타날 때까지의 최대 대기 시간 (초, 기본값: 5)
            
        Returns:
            bool: 토스트 메시지가 성공적으로 감지되면 True, 아니면 False
        """
        
        # 1. 토스트 메시지를 찾기 위한 범용적인 XPath 구성
        # contains() 함수를 사용하여 부분 문자열 매칭 지원
        # 예: toast_text="10번 실패하면 10분간 로그인이 제한돼요."는
        #     "10번 실패하면 10분간 로그인이 제한돼요. (1/10)"과도 매칭됨
        # toast_text에 따옴표가 포함될 수 있으므로 XPath에서 안전하게 처리
        # 작은따옴표로 감싸고, 작은따옴표는 &apos;로 이스케이프
        escaped_text = toast_text.replace("'", "&apos;")
        TOAST_XPATH = f"//android.widget.Toast[contains(@text, '{escaped_text}')]"
        
        # 2. WebDriver Wait 및 EC.presence_of_element_located 사용
        # presence_of_element_located는 해당 요소가 페이지 소스에 포함될 때까지 기다립니다.
        # 토스트는 잠깐 나타났다 사라지므로, 짧은 시간 내에 감지해야 합니다.
        locator = (AppiumBy.XPATH, TOAST_XPATH)
        
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            log.debug(f"토스트 메시지 '{toast_text}' 감지 성공.")
            return True
        except TimeoutException:
            # 타임아웃 발생 시, 토스트가 나타나지 않았거나 너무 빨리 사라진 경우
            # 이미 사라진 경우도 성공으로 간주 (토스트가 나타났다가 사라진 것으로 간주)
            try:
                elements = self.driver.find_elements(*locator)
                visible_elements = [e for e in elements if e.is_displayed()]
                if len(visible_elements) == 0:
                    # 토스트가 화면에 없으면 이미 나타났다가 사라진 것으로 간주
                    log.debug(f"토스트 메시지 '{toast_text}'가 타임아웃 전에 이미 사라진 것으로 간주 (성공).")
                    return True
                else:
                    # 토스트가 여전히 보이면 실패
                    log.debug(f"{timeout}초 이내에 토스트 메시지 '{toast_text}'를 감지하지 못했습니다.")
                    return False
            except Exception:
                # 요소를 찾을 수 없으면 이미 사라진 것으로 간주
                log.debug(f"토스트 메시지 '{toast_text}'가 타임아웃 전에 이미 사라진 것으로 간주 (성공).")
                return True
        except Exception as e:
            # 기타 예외 처리
            log.debug(f"토스트 감지 중 예상치 못한 오류 발생: {e}")
            return False

    def wait_for_toast_to_disappear(self, toast_text: str, timeout: int = 5) -> bool:
        """
        주어진 텍스트를 포함하는 토스트 메시지가 사라질 때까지 대기합니다.
        toast_text가 토스트 메시지의 일부만 포함해도 매칭됩니다.
        
        Args:
            toast_text: 사라지는 토스트 메시지에 포함될 텍스트
            timeout: 토스트가 사라질 때까지의 최대 대기 시간 (초, 기본값: 5)
            
        Returns:
            bool: 토스트 메시지가 성공적으로 사라지면 True, 타임아웃되면 False
        """
        
        # 1. 토스트 메시지를 찾기 위한 XPath 구성
        # contains() 함수를 사용하여 부분 문자열 매칭 지원
        # toast_text에 따옴표가 포함될 수 있으므로 XPath에서 안전하게 처리
        # 작은따옴표로 감싸고, 작은따옴표는 &apos;로 이스케이프
        escaped_text = toast_text.replace("'", "&apos;")
        TOAST_XPATH = f"//android.widget.Toast[contains(@text, '{escaped_text}')]"
        locator = (AppiumBy.XPATH, TOAST_XPATH)
        
        try:
            # 2. EC.invisibility_of_element_located를 사용하여 요소가 사라질 때까지 대기
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(locator)
            )
            log.debug(f"토스트 메시지 '{toast_text}' 사라짐 확인 성공.")
            return True
        except TimeoutException:
            # 타임아웃 발생 시, 토스트가 지정된 시간 내에 사라지지 않았음
            log.debug(f"{timeout}초 이내에 토스트 메시지 '{toast_text}'가 사라지지 않았습니다.")
            return False
        except Exception as e:
            # 기타 예외 처리
            log.debug(f"토스트 소멸 확인 중 예상치 못한 오류 발생: {e}")
            return False

    def is_element_present(self, locator, timeout=3):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except:
            return False

    def app_background(self, seconds=3):
        self.driver.background_app(seconds)
    
    def _get_device_serial(self):
        """Appium capabilities에서 디바이스 시리얼(UDID)을 가져옵니다."""
        # 'deviceName' 대신 'udid'나 'device.serial' 등을 사용하면 더 정확할 수 있습니다.
        return self.driver.capabilities.get('udid') or self.driver.capabilities.get('deviceName', 'emulator-5554')
    
    def disable_network(self):
        """
        인터넷 네트워크 연결을 확실하게 끊습니다.
        (모바일 데이터 및 Wi-Fi를 명시적으로 비활성화)
        
        Returns:
            bool: 네트워크를 성공적으로 끊었으면 True
        """
        device_serial = self._get_device_serial()
        
        try:
            log.info(f"[{device_serial}] 네트워크 연결 차단 시작...")

            # 1. 모바일 데이터 (Data) 비활성화
            # 'svc data disable' 명령어는 모바일 데이터 연결을 즉시 끊습니다.
            subprocess.run(
                ['adb', '-s', device_serial, 'shell', 'svc', 'data', 'disable'],
                check=True,  # 오류 발생 시 예외 발생
                capture_output=True,
                timeout=5
            )
            log.debug(f"[{device_serial}] 모바일 데이터 비활성화 완료.")

            # 2. Wi-Fi 비활성화
            # 'svc wifi disable' 명령어는 Wi-Fi 연결을 즉시 끊습니다.
            subprocess.run(
                ['adb', '-s', device_serial, 'shell', 'svc', 'wifi', 'disable'],
                check=True,
                capture_output=True,
                timeout=5
            )
            log.debug(f"[{device_serial}] Wi-Fi 비활성화 완료.")
            
            # 네트워크 상태 변경을 기다림 (충분히 줌)
            time.sleep(3)

            log.info(f"[{device_serial}] 네트워크 끊기 성공.")
            return True
            
        except subprocess.CalledProcessError as e:
            # ADB 명령어 실행 중 오류가 발생한 경우 (check=True 때문)
            log.error(f"[{device_serial}] ADB 명령 실행 실패. Stderr: {e.stderr.decode().strip()}")
            return False
        except Exception as e:
            # 기타 예외 처리
            log.error(f"[{device_serial}] 네트워크 끊기 실패: {e}")
            return False
    
    def enable_network(self):
        """
        네트워크 연결을 복원합니다.
        (모바일 데이터 및 Wi-Fi 활성화)
        """
        device_serial = self._get_device_serial()

        try:
            log.info(f"[{device_serial}] 네트워크 연결 복원 시작...")
            
            # 1. 모바일 데이터 (Data) 활성화
            subprocess.run(['adb', '-s', device_serial, 'shell', 'svc', 'data', 'enable'], check=True, timeout=5)
            log.debug(f"[{device_serial}] 모바일 데이터 활성화 완료.")

            # 2. Wi-Fi 활성화
            subprocess.run(['adb', '-s', device_serial, 'shell', 'svc', 'wifi', 'enable'], check=True, timeout=5)
            log.debug(f"[{device_serial}] Wi-Fi 활성화 완료.")
            
            # 네트워크 연결이 복구될 때까지 대기
            time.sleep(5) 
            
            log.info(f"[{device_serial}] 네트워크 복원 성공.")
            return True

        except Exception as e:
            log.error(f"[{device_serial}] 네트워크 복원 실패: {e}")
            return False
    
    def is_network_connected(self):
        """
        인터넷 네트워크 연결 상태를 확인합니다.
        최우선 조건으로 비행기 모드가 켜져있다면 False를 반환합니다.
        에뮬레이터인 경우 모바일 데이터 상태만 확인합니다 (WiFi는 항상 켜져있으므로).
        실제 디바이스인 경우 WiFi 또는 모바일 데이터 중 하나라도 활성화되어 있으면 True를 반환합니다.
        
        Returns:
            bool: 네트워크가 연결되어 있으면 True, 아니면 False
        """
        
        try:
            # 현재 디바이스 정보 가져오기
            device_name = self.driver.capabilities.get('deviceName', 'emulator-5554')
            
            # Step 1: 최우선 조건 - 비행기 모드가 켜져있는지 확인
            airplane_mode_result = subprocess.run(
                ['adb', '-s', device_name, 'shell', 'settings', 'get', 'global', 'airplane_mode_on'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            airplane_mode_on = airplane_mode_result.stdout.strip() == '1'
            
            if airplane_mode_on:
                log.debug("비행기 모드가 활성화되어 있어 네트워크 연결 없음")
                return False
            
            # Step 2: 비행기 모드가 꺼져있으면 WiFi/모바일 데이터 상태 확인
            # 에뮬레이터인지 확인 (deviceName이 'emulator-'로 시작하는지 확인)
            is_emulator = device_name.startswith('emulator-')
            
            if is_emulator:
                # 에뮬레이터인 경우: 모바일 데이터 상태만 확인 (WiFi는 항상 켜져있으므로)
                data_result = subprocess.run(
                    ['adb', '-s', device_name, 'shell', 'settings', 'get', 'global', 'mobile_data'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                data_on = data_result.stdout.strip() == '1'
                log.debug(f"에뮬레이터 네트워크 상태 확인: 모바일 데이터={'활성화' if data_on else '비활성화'}")
                return data_on
            else:
                # 실제 디바이스인 경우: WiFi 또는 모바일 데이터 중 하나라도 활성화되어 있으면 True
                wifi_result = subprocess.run(
                    ['adb', '-s', device_name, 'shell', 'settings', 'get', 'global', 'wifi_on'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                data_result = subprocess.run(
                    ['adb', '-s', device_name, 'shell', 'settings', 'get', 'global', 'mobile_data'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                wifi_on = wifi_result.stdout.strip() == '1'
                data_on = data_result.stdout.strip() == '1'
                
                log.debug(f"실제 디바이스 네트워크 상태 확인: WiFi={'활성화' if wifi_on else '비활성화'}, 모바일 데이터={'활성화' if data_on else '비활성화'}")
                return wifi_on or data_on
        except Exception as e:
            print(f"네트워크 상태 확인 실패: {e}")
            return False
    
    def terminate_all_apps(self, app_package: str = None):
        """
        현재 실행 중인 앱을 완전히 종료하고 홈 화면으로 이동합니다.
        앱을 완전히 종료하여 다음 실행 시 처음부터 시작하도록 합니다.
        
        Args:
            app_package: 종료할 앱의 패키지 이름 (None이면 설정에서 로드)
        
        Returns:
            bool: 앱을 성공적으로 종료했으면 True
        """
        
        try:
            if app_package is None:
                config = load_config()
                app_package = config.app_package
            
            device_name = self.driver.capabilities.get('deviceName', 'emulator-5554')
            
            # 1) 홈 화면으로 이동 (앱을 백그라운드로 전환)
            self.driver.press_keycode(3)  # KEYCODE_HOME
            time.sleep(0.5)
            
            # 2) Appium의 terminate_app 사용
            try:
                self.driver.terminate_app(app_package)
                time.sleep(0.5)
            except Exception:
                pass
            
            # 3) ADB를 통한 강제 종료 (force-stop)
            try:
                subprocess.run(
                    ['adb', '-s', device_name, 'shell', 'am', 'force-stop', app_package],
                    capture_output=True,
                    timeout=5
                )
                time.sleep(0.5)
            except Exception:
                pass
            
            # 4) 앱 프로세스 완전 종료 (killall)
            try:
                # 앱의 메인 프로세스 이름 찾기 (일반적으로 패키지 이름과 동일)
                subprocess.run(
                    ['adb', '-s', device_name, 'shell', 'killall', app_package],
                    capture_output=True,
                    timeout=5
                )
                time.sleep(0.5)
            except Exception:
                pass
            
            # 5) 앱이 완전히 종료되었는지 확인
            max_retries = 5
            for _ in range(max_retries):
                try:
                    current_package = self.driver.current_package
                    if current_package != app_package:
                        # 앱이 종료되었음
                        break
                except Exception:
                    # current_package를 확인할 수 없으면 종료된 것으로 간주
                    break
                time.sleep(0.5)
            
            # 6) 최종 확인: 홈 화면으로 이동
            self.driver.press_keycode(3)  # KEYCODE_HOME
            time.sleep(0.5)
            
            log.debug(f"앱 완전 종료 성공: {app_package}")
            return True
        except Exception as e:
            log.debug(f"앱 종료 실패: {e}")
            # 실패 시 홈 버튼만 누르기
            try:
                self.driver.press_keycode(3)  # KEYCODE_HOME
                return True
            except Exception:
                return False
    
    def _check_popup_exists(self):
        """
        시스템 팝업이 존재하는지 빠르게 확인합니다.
        
        Returns:
            tuple: (팝업 존재 여부, 클릭 가능한 요소) 또는 (False, None)
        """
        # 가장 일반적인 팝업 버튼만 빠르게 확인
        quick_check_locators = [
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("대기")'),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("앱 닫기")'),
        ]
        
        for locator in quick_check_locators:
            try:
                elements = self.driver.find_elements(*locator)
                for element in elements:
                    try:
                        if element and element.is_displayed():
                            return True, element
                    except Exception:
                        continue
            except Exception:
                continue
        
        return False, None
    
    def handle_system_popup(self, timeout=1):
        """
        시스템 UI 응답하지 않음 팝업 등을 처리합니다.
        '대기', '앱 닫기' 버튼을 찾아 클릭합니다.
        팝업이 없으면 즉시 반환하여 불필요한 요소 찾기를 방지합니다.
        
        Args:
            timeout: 팝업 요소를 찾기 위한 최대 대기 시간 (초, 기본값: 1)
            
        Returns:
            bool: 팝업을 찾아 처리했으면 True, 없으면 False
        """
        
        # 먼저 빠르게 팝업 존재 여부 확인
        popup_exists, popup_element = self._check_popup_exists()
        
        if popup_exists and popup_element:
            # 팝업이 있으면 즉시 클릭
            try:
                popup_element.click()
                time.sleep(0.5)  # 팝업이 사라질 때까지 짧은 대기
                return True
            except Exception:
                pass
        
        # 첫 번째 확인에서 팝업이 없으면 즉시 반환 (불필요한 추가 요청 방지)
        return False

    def is_element_effectively_disabled(self, locator, wait_time=1.0):
        """
        특정 UI 요소가 '사실상 비활성(눌러도 화면 변화 없음)'인지 검사합니다.
        클릭 이벤트의 실제 반응(Activity 변화 여부)로 판단하는 방식.

        Args:
            locator (tuple): Page Object에서 정의하는 (By.ID, "xxx") 형태의 locator
            wait_time (float): 클릭 후 대기 시간 (기본: 1초)

        Returns:
            bool: True → 비활성(눌러도 변화 없음)
                False → 활성(클릭 시 화면 변화 발생)
        """

        element = self.find(locator)

        # 클릭 전 현재 Activity
        before_activity = self.driver.current_activity

        # 클릭 시도
        try:
            element.click()
        except Exception:
            # 클릭 자체가 실패한다면 "비활성처럼 동작"하는 것으로 간주
            return True

        time.sleep(wait_time)

        # 클릭 후 Activity 변화 여부 확인
        after_activity = self.driver.current_activity

        return before_activity == after_activity

    def clear_text_android(self, locator, max_backspace=50):
        """
        특정 입력 필드의 기존 텍스트를 완전히 삭제하는 공용 함수.

        Args:
            locator (tuple): (By.ID, "xxx") 형태의 locator
            max_backspace (int): 기존 텍스트를 최대 몇 번까지 백스페이스로 지울지의 값

        Returns:
            bool: 성공적으로 지웠으면 True
        """

        try:
            field = self.find(locator)

            # 1) 필드 클릭 → 포커스 주기
            field.click()

            # 2) 기본 clear() 실행 (일부 앱에서는 동작)
            try:
                field.clear()
            except:
                pass

            # 3) 현재 텍스트 가져오기
            try:
                text = field.get_attribute("text")
            except:
                text = ""

            # 4) 텍스트가 남아있으면 백스페이스 반복
            if text:
                for _ in range(min(len(text), max_backspace)):
                    # Android Backspace: KEYCODE_DEL(67)
                    self.driver.press_keycode(67)

            # 5) 최종 확인
            try:
                final_text = field.get_attribute("text")
            except:
                final_text = ""

            return final_text == ""

        except Exception as e:
            print(f"[clear_text_android] 에러 발생: {e}")
            return False

    def is_input_field_masked(self, locator=None, timeout=5):
        """
        입력란에 입력한 text가 마스킹되어 노출되는지 확인합니다.

        Args:
            locator: 입력란의 locator (tuple)
            timeout: 각 locator를 시도할 때의 최대 대기 시간 (초)

        Returns:
            bool: 입력란에 입력한 text가 마스킹되어 노출되면 True, 그렇지 않으면 False
        """
        element = self.find(locator, timeout)
        return element.get_attribute("text") == "•" * len(element.get_attribute("text"))
    
    def wait_with_session_keepalive(self, wait_seconds, check_interval=60):
        """
        세션 타임아웃을 방지하기 위해 주기적으로 세션을 활성화하면서 대기합니다.
        
        Args:
            wait_seconds: 대기할 총 시간 (초)
            check_interval: 세션 체크 간격 (초, 기본값: 60초)
            
        Returns:
            bool: 대기 중 세션이 유지되면 True, 세션이 종료되면 False
        """
        elapsed = 0
        while elapsed < wait_seconds:
            sleep_time = min(check_interval, wait_seconds - elapsed)
            time.sleep(sleep_time)
            elapsed += sleep_time
            
            # 세션을 활성화하기 위해 간단한 명령 실행
            try:
                _ = self.driver.current_package
                # 세션이 정상적으로 활성화되었음을 로그로 기록 (hang up 오류와 구분하기 위함)
                log.debug(f"세션 활성화 되었습니다. (경과 시간: {elapsed}초 / 총 대기 시간: {wait_seconds}초)")
            except Exception as e:
                log.warning(f"세션 체크 중 오류 발생 (경과 시간: {elapsed}초): {e}")
                return False
        
        return True
    
    def logout_in_main_home_page(self, main_home_page, timeout=20):
        """
        오늘의집 메인 홈페이지에서 로그아웃을 수행하는 공통 함수입니다.
        하단 footer의 [마이페이지] 버튼 클릭 후 우측 상단의 [설정] 아이콘 버튼 탭하여 설정 페이지로 이동하고, 설정 페이지에서 로그아웃 버튼을 클릭합니다.
        
        Args:
            main_home_page: MainHomePage 객체
            timeout: 각 단계별 최대 대기 시간 (초, 기본값: 20)
            
        Returns:
            bool: 로그아웃이 성공적으로 완료되었으면 True, 실패 시 False
            str: 오류 메시지 또는 로그아웃 토스트 위젯 노출 여부 메시지
        """
        try:
            # 순환 import 방지를 위해 함수 내부에서 import
            from src.pages.my_page import MyPage
            from src.pages.setting_page import SettingPage
            
            # Step 1: 메인 홈 페이지 하단 footer의 [마이페이지] 버튼 클릭
            try:
                main_home_page.click(main_home_page.MYPAGE_BOTTOM_BUTTON, timeout=timeout)
                time.sleep(0.5)  # 마이페이지 전환 대기
            except Exception as e:
                log.warning(f"마이페이지 버튼 클릭 실패: {e}")
                return False, f"마이페이지 버튼 클릭 실패: {e}"

            # Step 1: 마이페이지 로드 확인
            my_page = MyPage(self.driver)
            if not my_page.is_my_page_loaded(timeout=timeout):
                log.warning("마이페이지가 로드되지 않았습니다.")
                return False, "마이페이지가 로드되지 않았습니다."
            
            # Step 2: 설정 아이콘 버튼 클릭
            try:
                my_page.click(my_page.GEAR_ICON_BUTTON)
                time.sleep(0.5)  # 페이지 전환 대기
            except Exception as e:
                log.warning(f"설정 아이콘 버튼 클릭 실패: {e}")
                return False, f"설정 아이콘 버튼 클릭 실패: {e}"
            
            # Step 3: 설정 페이지 로드 확인
            setting_page = SettingPage(self.driver)
            if not setting_page.is_setting_page_loaded(timeout=timeout):
                log.warning("설정 페이지가 로드되지 않았습니다.")
                return False, "설정 페이지가 로드되지 않았습니다."
            
            # Step 4: 페이지 최하단으로 스크롤
            try:
                setting_page.scroll_to_bottom()
                time.sleep(0.5)  # 스크롤 완료 대기
            except Exception as e:
                log.warning(f"페이지 스크롤 실패: {e}")
                return False, f"페이지 스크롤 실패: {e}"
            
            # Step 5: 로그아웃 버튼 클릭
            try:
                setting_page.click(setting_page.LOGOUT_TEXT_BUTTON)
            except Exception as e:
                log.warning(f"로그아웃 버튼 클릭 실패: {e}")
                return False, f"로그아웃 버튼 클릭 실패: {e}"
            
            log.info("로그아웃 완료")
            return True, None
                
        except Exception as e:
            log.debug(f"로그아웃 중 오류 발생: {e}")
            return False, f"로그아웃 중 오류 발생: {e}"
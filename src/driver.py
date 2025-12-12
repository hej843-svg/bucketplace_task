from appium import webdriver
from appium.options.android import UiAutomator2Options

from src.config.settings import AppConfig, build_capabilities, load_config


def create_driver(cfg: AppConfig | None = None, skip_app_launch: bool = False) -> webdriver.Remote:
    """
    Appium Remote WebDriver를 생성합니다.
    
    Args:
        cfg: AppConfig 객체 (None이면 환경 변수에서 로드)
        skip_app_launch: True이면 앱 실행 없이 드라이버만 생성 (예: 플레이 스토어 앱을 직접 실행할 때)
    """
    config = cfg or load_config()
    caps = build_capabilities(config, skip_app_launch=skip_app_launch)
    options = UiAutomator2Options().load_capabilities(caps)

    driver = webdriver.Remote(command_executor=config.appium_server_url, options=options)
    driver.implicitly_wait(10)
    return driver


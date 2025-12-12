import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class AppConfig:
    appium_server_url: str
    platform_name: str
    platform_version: str
    device_name: str
    automation_name: str
    app_package: str
    app_activity: str
    login_id: str | None = None
    login_password: str | None = None


def load_config() -> AppConfig:
    load_dotenv()

    return AppConfig(
        appium_server_url=os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723"),
        platform_name=os.getenv("PLATFORM_NAME", "Android"),
        platform_version=os.getenv("PLATFORM_VERSION", ""),
        device_name=os.getenv("DEVICE_NAME", "emulator-5554"),
        automation_name=os.getenv("AUTOMATION_NAME", "UiAutomator2"),
        app_package=os.getenv("APP_PACKAGE", "net.bucketplace"),
        app_activity=os.getenv("APP_ACTIVITY", "se.ohou.screen.splash.SplashActivity"),
        login_id=os.getenv("LOGIN_ID"),
        login_password=os.getenv("LOGIN_PASSWORD"),
    )


def build_capabilities(cfg: AppConfig, skip_app_launch: bool = False) -> dict:
    """
    Appium desired capabilities를 생성합니다.
    
    Args:
        skip_app_launch: True이면 appPackage/appActivity를 설정하지 않음 (앱 실행 없이 드라이버만 생성)
    """
    caps = {
        "platformName": cfg.platform_name,
        "deviceName": cfg.device_name,
        "automationName": cfg.automation_name,
        "newCommandTimeout": 1200,  # 20분 (10분 대기 + 여유 시간)
        "noReset": True,  # 앱 데이터 유지
        "uiautomator2ServerLaunchTimeout": 90000,  # UiAutomator2 서버 초기화 타임아웃 (90초)
    }
    # platformVersion이 비어있지 않을 때만 추가 (비어있으면 Appium이 자동 감지), Android 버전을 뜻함.
    if cfg.platform_version:
        caps["platformVersion"] = cfg.platform_version
    # skip_app_launch가 False일 때만 앱 실행 정보 추가
    if not skip_app_launch and cfg.app_package and cfg.app_activity:
        caps["appPackage"] = cfg.app_package
        caps["appActivity"] = cfg.app_activity
    return caps


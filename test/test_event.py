from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.pointer_input import PointerInput

# [설정] Appium 서버 및 에뮬레이터 기본 연결 설정
options = UiAutomator2Options()
options.platform_name = "Android"
options.automation_name = "UiAutomator2"
options.device_name = "emulator-5554"  # adb devices 포트

options.app_package = "com.sampleapp"       # 실제 앱 패키지명
options.app_activity = "com.baemin.presentation.ui.root.ui.RootContainerActivity" # 메인 액티비티명
options.no_reset = True  # 기존 데이터 및 로그인 상태 유지

# appium 연결
driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
wait = WebDriverWait(driver, 10)

def setup_event_screen():
    """[공통 사전조건] 메인 홈 화면에서 이벤트 항목 접속"""
    event_entry_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(@content-desc, '이벤트') or contains(@text, '이벤트')]")))
    event_entry_btn.click()
    time.sleep(1.5)

def swipe_down_screen(driver):
    """화면 하단 스크롤 함수"""
    size = driver.get_window_size()
    width, height = size['width'], size['height']

    start_x, start_y = width / 2, height * 0.8
    end_x, end_y = width / 2, height * 0.2

    touch = PointerInput(interaction.POINTER_TOUCH, "touch")
    actions = ActionChains(driver)
    actions.w3c_actions.devices.append(touch)

    actions.w3c_actions.pointer_action.move_to_location(start_x, start_y)
    actions.w3c_actions.pointer_action.pointer_down(0)
    actions.w3c_actions.pointer_action.pause(0.6) 
    actions.w3c_actions.pointer_action.move_to_location(end_x, end_y)
    actions.w3c_actions.pointer_action.pause(0.5)
    actions.w3c_actions.pointer_action.pointer_up(0)
    actions.perform()
    time.sleep(1.5)

try:
    # ----------------------------------------------------
    # 1. EV_01: 배민 클럽 미가입 상태 시 쿠폰 발급 제한 (Negative)
    # ----------------------------------------------------
    print("▶ EV_01 테스트 시작: 배민 클럽 미가입 상태 권한 제한")
    setup_event_screen()

    # 1. '혜택' 멘트가 있는 광고 페이지 진입
    benefit_ad_page = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(@content-desc, '혜택')]")))
    benefit_ad_page.click()
    time.sleep(2)

    # 2. 쿠폰 버튼 클릭
    coupon_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(@text, '쿠폰 받기') or contains(@content-desc, '쿠폰')]")))
    coupon_btn.click()
    time.sleep(1.5)

    # 3. '발급 대상이 아니에요' 멘트의 팝업 노출 확인
    popup_msg = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(@text, '발급 대상이 아니에요')]")))
    assert popup_msg.is_displayed(), "EV_01 실패: '발급 대상이 아니에요' 팝업이 노출되지 않음"
    print("✅ EV_01 통과: 배민클럽 미가입 시 '발급 대상이 아니에요' 팝업 노출 확인")

    # 복귀
    driver.back()
    time.sleep(1)
    driver.back()
    time.sleep(1)

    # ----------------------------------------------------
    # 2. EV_02: 쿠폰 중복 수령 방지 (Negative)
    # ----------------------------------------------------
    print("▶ EV_02 테스트 시작: 중복 쿠폰 수령 방지")
    setup_event_screen()

    # 1. 인기 브랜드 영역 확인
    popular_brand_section = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(@text, '인기 브랜드')]")))
    assert popular_brand_section.is_displayed(), "EV_02 실패: 인기 브랜드 영역을 찾을 수 없음"

    # 2. 버거킹 쿠폰이 있는 상태에서 '버거킹' 탭 클릭
    bk_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(@text, '버거킹')]")))
    bk_tab.click()
    time.sleep(1.5)

    # 3. 쿠폰 받는 버튼 대신 '받기 완료' 멘트 노출 검증
    completed_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(@text, '받기 완료')]")))
    assert completed_btn.is_displayed(), "EV_02 실패: '받기 완료' 멘트가 존재하지 않거나 이미 지급된 상태가 아님"
    print("✅ EV_02 통과: 쿠폰 중복 수령 불가 및 '받기 완료' 버튼 상태 확인")

    # 복귀
    driver.back()
    time.sleep(1)

    # ----------------------------------------------------
    # 3. EV_03: 할인 관련 안내/설명창 노출 (Functional)
    # ----------------------------------------------------
    print("▶ EV_03 테스트 시작: 할인 정보 설명창 확인")
    setup_event_screen()

    # 1. '할인' 멘트 광고 페이지 진입
    discount_ad_page = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(@text, '할인')]")))
    discount_ad_page.click()
    time.sleep(2)

    # 2. 할인가게 (3번째 탭) 클릭
    # (일반적으로 ComposeView/RecyclerView 내의 3번째 탭 선택)
    discount_store_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "(//*[contains(@text, '할인가게') or contains(@resource-id, 'r2-trigger-tab-3')])")))
    discount_store_tab.click()
    time.sleep(1.5)

    # 3. 할인 가게 제목 옆 Info 아이콘 클릭
    info_icon = wait.until(EC.element_to_be_clickable((By.XPATH, "//android.view.View[@resource-id='tab-3']/android.view.View[1]/android.view.View/android.widget.TextView[2]")))
    info_icon.click()
    time.sleep(1)

    # 4. 관련 설명창 등장 검증
    info_dialog = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(@resource-id, 'dialog') or contains(@text, '정해진 시간') or contains(@text, '안내')]")))
    assert info_dialog.is_displayed(), "EV_03 실패: Info 아이콘 클릭 시 관련 설명창이 등장하지 않음"
    print("✅ EV_03 통과: 할인 가게 Info 아이콘 클릭 시 관련 설명창 정상 노출 확인")

    # 홈 화면 복귀
    driver.back()
    time.sleep(1)

except AssertionError as e:
    print(f"❌ 테스트 실패: {e}")
except Exception as e:
    print(f"⚠️ 에러 발생: {e}")
finally:
    driver.quit()
    print("▶ 모든 이벤트(EV) 도메인 테스트 시나리오 종료")
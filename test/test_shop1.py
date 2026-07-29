import pytest
import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.actions.interaction import POINTER_TOUCH
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.actions.mouse_button import MouseButton


@pytest.fixture(scope="class")
def driver_setup(request):
    """
    [Fixture] Appium 서버 및 에뮬레이터 연결 초기화 설정
    """
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = "emulator-5554"
    options.app_package = "com.sampleapp"
    options.app_activity = "com.baemin.presentation.ui.root.ui.RootContainerActivity"
    options.no_reset = True  # 데이터 및 로그인 상태 유지
    
    # ⭐ [핵심 추가] 현재 에뮬레이터에 켜져 있는 화면 상태를 그대로 유지하고 이어서 테스트 수행
    options.set_capability("dontStopAppOnReset", True)
    
    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    
    if request.cls is not None:
        request.cls.driver = driver
        
    yield driver
    driver.quit()

@pytest.mark.usefixtures("driver_setup")
class TestBaeminShop:

    def test_SHOP_01_search_entry(self):
        """
        [SHOP_01] 장보기·쇼핑 카테고리 검색창 진입 및 동작 확인
        - 기대결과: '장보기·쇼핑' 카테고리 탭이 선택된 검색 화면으로 정상 진입해야 함
        """
        

        time.sleep(1)
        shopbutton = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//androidx.compose.ui.platform.ComposeView[@resource-id='com.sampleapp:id/bottomTabBar']/android.view.View/android.view.View/android.view.View[2]/android.view.View[2]"))
        )
        shopbutton.click()

        time.sleep(2)

        # 장보기·쇼핑 화면에서 검색창 클릭 (식별자는 환경에 맞게 조정 필요)
        search_bar = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//android.widget.EditText"))
        )
        search_bar.click()

        time.sleep(2)  # 화면 전환 대기
        
        # 검색 진입 후 검증 대상 요소 (예: 뒤로가기 버튼이나 검색 입력 필드)
        # 예시: 검색창 진입 후 상단 입력 필드가 활성화되었는지 확인
        search_input = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//android.widget.EditText"))
        )
        assert search_input.is_displayed(), "검색 화면 진입 실패"

        print("\n[SHOP_01 Pass] 장보기 검색 화면 진입 성공")
        
        # ⭐ [중요 추가] 다음 테스트(SHOP_02)가 장보기 메인에서 계속될 수 있도록 뒤로가기 실행
        self.driver.back()
        time.sleep(2)

        self.driver.back()
        time.sleep(2)
        
        

    def test_SHOP_02_horizontal_scroll_to_all_view(self):
        """
        [SHOP_02] 추천 가게 목록 가로 스크롤 및 전체보기 화면 이동 기능 검증
        - 기대결과: 가로 스크롤 후 '전체보기' 클릭 시 가게 전체보기 화면으로 이동해야 함
        """
        

        print("\n[SHOP_02 단계 시작] 좌표 기반 가로 스크롤 시도")
    
        # 1. 가로 스크롤 영역(HorizontalScrollView) 요소를 먼저 찾습니다.
        scroll_container = self.driver.find_element(AppiumBy.XPATH, "//androidx.recyclerview.widget.RecyclerView/android.widget.FrameLayout/androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[1]/android.view.View[3]/android.view.View/android.view.View")
        
        # 영역의 크기와 시작 좌표 구하기
        location = scroll_container.location
        size = scroll_container.size
        
        # 가로로 쓸어 넘길 좌표 계산 (오른쪽 -> 왼쪽으로)
        start_x = int(location['x'] + (size['width'] * 0.9))  # 오른쪽 80% 지점
        end_x = int(location['x'] + (size['width'] * 0.1))    # 왼쪽 20% 지점
        y_coordinate = int(location['y'] + (size['height'] / 2)) # 스크롤 영역의 정중앙 세로축
        
        # 2. 임포트한 POINTER_TOUCH 상수를 직접 사용해 터치 인풋을 선언합니다.
        touch_input = PointerInput(POINTER_TOUCH, "touch")
        
        actions = ActionChains(self.driver)
        actions.w3c_actions.devices.append(touch_input) # 터치 디바이스 등록
        
        # W3C Touch 스크롤 표준 제스처 수행
        actions.w3c_actions.pointer_action.move_to_location(start_x, y_coordinate)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.move_to_location(end_x, y_coordinate)
        actions.w3c_actions.pointer_action.pointer_up()
        actions.perform()
        
        time.sleep(1.5) # 화면 렌더링 완료 대기
        
        # 2. 화면 안으로 드러난 '전체보기' 버튼을 XPath로 특정해서 클릭.
        try:
            view_all_btn = self.driver.find_element(AppiumBy.XPATH, "//androidx.recyclerview.widget.RecyclerView/android.widget.FrameLayout/androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[1]/android.view.View[3]/android.view.View/android.view.View/android.view.View[6]")
            view_all_btn.click()
            
            # 3. 화면이 완전히 전환되고 "가게 전체 보기" 텍스트가 노출될 때까지 최대 7초 대기
            # (네트워크 지연이나 애니메이션 속도를 고려해 명시적 대기를 주는 것이 좋습니다.)
            wait = WebDriverWait(self.driver, 7)
            
            target_xpath = '//android.widget.TextView[@text="가게 전체 보기"]'
            
            # 요소가 화면에 나타날 때까지 기다렸다가 가져옴
            title_element = wait.until(
                EC.presence_of_element_located((AppiumBy.XPATH, target_xpath))
            )
            
            # 4. 최종 검증 (Assertion) : 요소가 실제로 사용자 눈에 보이고(True) 작동하는지 체크
            assert title_element.is_displayed(), "화면에 '가게 전체 보기' 텍스트가 노출되지 않았습니다."
            
            print(f"[SHOP_02 단계 성공] '{title_element.text}' 화면 진입 검증 완료! 🎉")

        except Exception as e:
            print(f"[SHOP_02 단계 실패] 에러 발생: {e}")
            assert False, f"SHOP_02 검증 실패: 전체보기 화면 진입에 실패했거나 타이틀이 일치하지 않습니다. ({e})"

        # SHOP_02에서 전체보기 화면에 진입했으므로 다시 장보기 첫 화면으로 복귀
        self.driver.back()
        time.sleep(1)
        

    def test_SHOP_03_pull_to_refresh(self):
        """
        [SHOP_03] 당겨서 새로고침(Pull-to-Refresh) 및 토스트 메시지 확인
        - 기대결과: '땡겨서 OOO 리프레시' 토스트 메시지가 정상 노출되어야 함
        """
        

        driver = self.driver
    
        # 1. 화면 크기 구하기 및 좌표 설정
        size = driver.get_window_size()
        start_x = int(size['width'] / 2)
        start_y = int(size['height'] * 0.3)  # 상단 (30%)
        end_y = int(size['height'] * 0.8)    # 하단 (80%)까지 당김
        
        # 2. W3C Actions 생성
        actions = ActionChains(driver)
        touch_input = PointerInput(interaction.POINTER_TOUCH, "touch")
        
        # 누르고 ➔ 당기기
        touch_input.create_pointer_move(duration=0, x=start_x, y=start_y)
        touch_input.create_pointer_down(button=MouseButton.LEFT)
        touch_input.create_pointer_move(duration=1000, x=start_x, y=end_y)
        
        # 핵심: 손가락을 떼지 않고 화면을 누른 채로 1.5초간 유지 (Hold)
        touch_input.create_pause(1.5)
        
        actions.w3c_actions.devices.append(touch_input)
        actions.perform()
        
        # 3. try - except - finally를 통한 엄격한 예외 처리 구조
        try:
            print("💡 [SHOP_03] 화면을 당긴 상태 유지 중... 토스트 메시지 탐색 시작")
            
            # 새로고침 토스트 메시지 식별자 (텍스트나 클래스로 조준)
            toast_locator = (AppiumBy.XPATH, "//*[contains(@text, '땡겨서') or @class='android.widget.Toast']")
            
            # Hold 중인 시간 동안 짧고 강하게 대기 (3초)
            toast_element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located(toast_locator)
            )
            
            # 토스트 노출 성공 시
            print(f"✅ [SHOP_03 성공] 토스트 메시지 감지 완료: '{toast_element.text}'")
            assert toast_element is not None

        except TimeoutException:
            # ❌ 이전 테스트들처럼 타임아웃 예외가 발생했을 때 처리할 로직
            print("❌ [SHOP_03 실패] TimeoutException 발생: 드래그 중 새로고침 토스트 메시지를 찾지 못했습니다.")
            # pytest에서 명시적으로 실패를 발생.
            raise AssertionError("드래그 중에 새로고침 토스트 메시지가 화면에 표시되지 않았습니다.")
            
        finally:
            # 4. 손가락은 무조건 떼어주어야 에뮬레이터가 먹통이 안 됨.
            try:
                actions.release()  # 👈 현재 누르고 있는 포인터를 자연스럽게 해제
                actions.perform()
                print("💡 [SHOP_03] 드래그 제스처 종료 (actions.release() 완료)")
            except Exception as e:
                print(f"⚠️ 손가락 해제 중 예외 발생 (무시 가능): {e}")

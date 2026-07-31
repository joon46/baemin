import pytest
import time
import re
from appium import webdriver
from appium.options.common import AppiumOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

@pytest.fixture(scope="class")
def driver_setup(request):
    # Appium 서버 및 디바이스 설정
    options = AppiumOptions()
    options.set_capability("platformName", "Android")
    options.set_capability("automationName", "UiAutomator2")
    options.set_capability("deviceName", "Android Emulator")  # 또는 연결된 기기 이름
    options.set_capability("appPackage", "com.sampleapp") # 배민 패키지명 (실제 설정에 맞게 수정)
    options.set_capability("appActivity", "com.baemin.presentation.ui.root.ui.RootContainerActivity") # 실제 액티비티명
    options.set_capability("noReset", True)

    # Appium 서버 연결 (기본 포트: 4723)
    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    
    # 클래스 변수로 driver 전달 (self.driver 로 사용 가능하게 함)
    if request.cls is not None:
        request.cls.driver = driver
        
    yield driver
    
    # 테스트 완료 후 드라이버 종료
    driver.quit()

def parse_distance_to_meters(distance_str):
        """
        '817m', '1.2km' 등의 거리 텍스트를 미터(m) 단위의 숫자(float)로 변환
        """
        try:
            clean_str = distance_str.strip().lower()
            if 'km' in clean_str:
                num = float(re.sub(r'[^0-9.]', '', clean_str))
                return num * 1000  # 1.2km -> 1200m
            elif 'm' in clean_str:
                return float(re.sub(r'[^0-9.]', '', clean_str)) # 817m -> 817
        except Exception as e:
            print(f"거리 파싱 실패: {distance_str} ({e})")
        return float('inf')

@pytest.mark.usefixtures("driver_setup")
class TestBaeminShop:
    def swipe_horizontal(self, start_x_ratio, end_x_ratio, y_ratio):
        """카테고리 탭 영역 전용 가로 스크롤(Swipe) 헬퍼 함수"""
        size = self.driver.get_window_size()
        width = size["width"]
        height = size["height"]

        start_x = int(width * start_x_ratio)
        end_x = int(width * end_x_ratio)
        y = int(height * y_ratio)

        actions = ActionChains(self.driver)
        touch_input = PointerInput(interaction.POINTER_TOUCH, "touch")
        actions.w3c_actions = ActionBuilder(
            self.driver, mouse=touch_input
        )

        touch_input.create_pointer_move(x=start_x, y=y)
        touch_input.create_pointer_down(button=0)
        touch_input.create_pause(0.3)
        touch_input.create_pointer_move(x=end_x, y=y, duration=500)
        touch_input.create_pointer_up(button=0)

        actions.perform()

    def test_SHOP_07_no_store_exception_message(self):
        """SHOP_07: 주문 가능한 가게 미존재 시 예외 처리 안내 멘트 검증"""
        driver = self.driver
        wait = WebDriverWait(driver, 10)

        target_tab_xpath = "//*[contains(@text, '반찬') or contains(@content-desc, '반찬')]"

        # 1. 상단 카테고리 탭 영역에서 '반찬·식품' 탭이 보일 때까지 오른쪽 -> 왼쪽 가로 스크롤
        target_tab = None
        max_scroll_attempts = 5

        for attempt in range(max_scroll_attempts):
            tabs = driver.find_elements(By.XPATH, target_tab_xpath)
            # 화면 상에 실제로 노출되는 탭 요소 식별
            visible_tabs = [t for t in tabs if t.is_displayed()]

            if visible_tabs:
                target_tab = visible_tabs[0]
                break

            # 탭이 안 보이면 오른쪽에서 왼쪽으로 가로 스크롤 (화면 상단 Y축 15~20% 지점 제어)
            self.swipe_horizontal(
                start_x_ratio=0.85, end_x_ratio=0.15, y_ratio=0.18
            )
            time.sleep(1)

        assert target_tab is not None, (
            "❌ [SHOP_07 실패] 가로 스크롤을 시도했으나 '반찬·식품' 카테고리 탭을 찾을 수 없습니다."
        )

        # 2. '반찬·식품' 탭 클릭
        target_tab.click()

        # 3. 예외 안내 멘트 노출 검증 ("근처에 주문 가능한 가게가..." 문구 탐색)
        exception_text_xpath = "//*[contains(@text, '근처에 주문') or contains(@text, '가게가 없어요') or contains(@content-desc, '근처에 주문')]"

        try:
            exception_element = wait.until(
                EC.presence_of_element_located((By.XPATH, exception_text_xpath))
            )

            actual_text = (
                exception_element.text
                or exception_element.get_attribute("content-desc")
            )

            assert exception_element.is_displayed(), (
                "❌ [SHOP_07 실패] 예외 처리 멘트 요소가 화면에 표시되지 않습니다."
            )

            print(
                f"✅ [SHOP_07 성공] 예외 안내 문구가 정상 노출되었습니다. (확인된 문구: '{actual_text}')"
            )

        except Exception as e:
            pytest.fail(
                f"❌ [SHOP_07 실패] '근처에 주문 가능한 가게가 없어요' 안내 멘트를 찾을 수 없습니다. (에러: {e})"
            )

        time.sleep(2)

    

    def test_SHOP_08_sort_filter_change(self):
        """
        특정 편의점 상자 안의 지점거리만 추출하여 '가까운 순' 정렬 검증
        """
        wait = WebDriverWait(self.driver, 10)

        print("\n--- [SHOP_08] 편의점 이동(가로 스크롤) 및 '가까운 순' 거리 정렬 테스트 시작 ---")

        

        try:
            # 1. 사전 조건: '편의점' 탭이 보이지 않을 경우 카테고리 바를 오른쪽에서 왼쪽으로 스크롤
            convenience_tab_xpath = "//*[contains(@text, '편의점')]"
            
            # '편의점' 탭이 탐색될 때까지 가로 스크롤 시도 (최대 3회)
            for attempt in range(3):
                try:
                    convenience_tab = self.driver.find_element(By.XPATH, convenience_tab_xpath)
                    if convenience_tab.is_displayed():
                        convenience_tab.click()
                        print(" [사전 조건 완료] '편의점' 탭 클릭")
                        break
                except Exception:
                    print(f" '편의점' 탭이 화면에 없어 가로 스크롤을 진행합니다. (시도 {attempt + 1}/3)")
                    
                    # 화면 해상도 기반 오른쪽에서 왼쪽으로 스크롤 (스와이프)
                    window_size = self.driver.get_window_size()
                    start_x = int(window_size['width'] * 0.2)  # 화면 좌측 20% 지점 (터치 시작)
                    end_x = int(window_size['width'] * 0.8)    # 화면 우측 80% 지점 (드래그 종료)
                    start_y = int(window_size['height'] * 0.2) # 카테고리 탭 높이 (약 20% 위치)
                    
                    self.driver.swipe(start_x, start_y, end_x, start_y, 500)
                    time.sleep(1)
            else:
                # 3회 스크롤 후에도 찾지 못해 최종 wait 조회를 통한 클릭 시도
                convenience_tab = wait.until(EC.element_to_be_clickable((By.XPATH, convenience_tab_xpath)))
                convenience_tab.click()

            time.sleep(2) # 편의점 매장 목록 로딩 대기

            # 2. 정렬 필터 버튼 클릭
            sort_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(@text, '순') or contains(@text, '정렬')]"))
            )
            print(f" 현재 정렬 상태: [{sort_btn.text}]")
            sort_btn.click()
            time.sleep(1)

            # 3. 정렬 옵션 중 '가까운 순' 선택
            target_option = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(@text, '가까운 순')]"))
            )
            target_option.click()

            # 4. 검증 : 정렬 필터 버튼 텍스트가 '가까운 순'으로 노출되는지 확인
            current_sort_filter = wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(@text, '가까운 순')]"))
            )
            assert current_sort_filter is not None, " 정렬 필터가 '가까운 순'으로 표시되지 않습니다."
            print(" [검증 1] 필터 버튼이 '가까운 순'으로 변경됨을 확인했습니다.")

            print(" '가까운 순' 정렬 옵션 선택 완료")
            time.sleep(2)



            # 5. CU 편의점 영역 상자(부모) 찾기
            cu_xpath = "//androidx.recyclerview.widget.RecyclerView/android.widget.FrameLayout/androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View/android.view.View[3]"
            
            cu_section = wait.until(
                EC.presence_of_element_located((By.XPATH, cu_xpath))
            )
            print(" [성공] CU 영역 상자를 찾았습니다.", flush=True)

            # 6. CU 영역 상자 안에서만 거리 텍스트들 가져오기
            # ⚠️ XPath 시작 부분의 './/' (점-슬래시-슬래시)가 핵심입니다!
            distance_elements = cu_section.find_elements(
                By.XPATH, ".//*[contains(@text, 'm') or contains(@text, 'km')]"
            )

            cu_distances = []
            for elem in distance_elements:
                text = elem.text.strip()
                # '817m', '1.2km' 같은 데이터 형태만 걸러내기
                if re.search(r'\d+(\.\d+)?\s*(m|km)', text):
                    m_value = parse_distance_to_meters(text)
                    cu_distances.append((text, m_value))

            print(f" CU 상자 안에서 추출된 거리: {[d[0] for d in cu_distances]}", flush=True)

            # 7. 미터(m) 수치들만 뽑아서 오름차순(가까운 순) 검증
            meter_values = [d[1] for d in cu_distances if d[1] != float('inf')]
            
            assert len(meter_values) >= 2, " CU 영역 내에 비교할 거리가 2개 이상 존재하지 않습니다."
            assert meter_values == sorted(meter_values), f"❌ CU 지점들이 가까운 순으로 정렬되지 않았습니다! (수집된 거리: {[d[0] for d in cu_distances]})"

            print(f"🎉 [검증 성공] CU 내 매장들이 정상적으로 가까운 순({' < '.join([d[0] for d in cu_distances])})으로 정렬되어 있습니다!", flush=True)

        except Exception as e:
            print(f"❌ [CU 검증 실패]: {e}", flush=True)
            raise e
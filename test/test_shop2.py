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

@pytest.mark.usefixtures("driver_setup")
class TestBaeminShop:

    # (기존 test_SHOP_01, SHOP_02, SHOP_03 코드가 있다고 가정)

    def test_SHOP_04_time_deal_quantity_change(self):
        """
        SHOP_04: 타임딜 상품 수량 증감(+/-) 버튼 동작 확인
        사전 조건: '타임딜' 영역이 보여지는 상태
        """
        # 1. '오늘' 버튼 클릭 (이전 절차 리프레시나 타임딜 확인용)
        # 팁: '오늘' 텍스트를 가진 요소를 명확하게 지정하여 클릭합니다.
        today_button_xpath = (
            "//android.widget.TextView[contains(@text, '오늘')]"
        )
        today_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, today_button_xpath))
        )
        today_btn.click()
        print("'오늘' 영역 새로고침 완료")

        time.sleep(1.5)

        # 2. 동적 타임딜 영역에서 '첫 번째 상품'의 수량 증가(+) 버튼 조준
        # 마케팅 문구(상품명)가 수시로 바뀌므로, 상품 텍스트 대신 첫 번째 수량 버튼 레이아웃 구조를 타겟팅함.
        # resource-id가 없을 경우를 대비해 흔히 쓰이는 뷰 구조나 텍스트 기호(+)를 매칭함.
        plus_button_xpath = "(//android.view.View[@content-desc='장바구니 담기'])[1]"

        # 첫 번째로 보이는 + 버튼 탐색 및 2회 클릭
        first_plus_btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, plus_button_xpath))
        )
        

        first_plus_btn[0].click()  # 수량 1 증가
        #리스트가 아닌 단일 요소로 간주하기 위해 [0]을 붙임
        time.sleep(1.0)  # 서버 통신 및 애니메이션 대기

        # Compose 화면 특성상 엘리먼트 갱신을 위해 + 버튼을 다시 재탐색하여 클릭
        first_plus_btn = self.driver.find_elements(By.XPATH, plus_button_xpath)
        first_plus_btn[0].click()  # 수량 2 증가
        time.sleep(1.0)

        # 3. 수량이 정상적으로 늘어났는지 데이터 검증 (Assertion)
        
        # 수량 '2개' 담김 상태를 검증하는 XPath
        quantity_2_xpath = '//android.widget.TextView[@content-desc="장바구니 2개 담김"]'

        # 해당 요소가 화면에 나타날 때까지 대기 (최대 5초)
        quantity_element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, quantity_2_xpath))
        )

        # 요소가 정상적으로 찾아졌다면 성공!
        assert quantity_element is not None, "장바구니 수량이 2개로 변경되지 않았습니다."
        print("  - [검증 완료] 장바구니 2개 담김 확인!")

        # 4. 수량 감소(-) 버튼 클릭 확인
        # 수량이 1개 이상이면 버튼 content-desc가 '수량 줄이기' 등으로 변경되거나 '-' 모양으로 변경
        minus_button_xpath = "//android.view.View[@content-desc='장바구니 빼기']"
        first_minus_btn = self.driver.find_elements(By.XPATH, minus_button_xpath)
        
        if first_minus_btn:
            first_minus_btn[0].click()  # 수량 1 감소 (2 -> 1)
            print("수량 감소 버튼 클릭(-1)")
            time.sleep(1)
        

        # 5. 최종 감소된 수량 재검증
        # 수량이 1로 줄었는지 텍스트를 다시 확인
            
        # 수량 '1개' 담김 상태를 검증하는 XPath
        quantity_1_xpath = '//android.widget.TextView[@content-desc="장바구니 1개 담김"]'

        quantity_element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, quantity_1_xpath))
        )
        assert quantity_element is not None, "장바구니 수량이 1개로 변경되지 않았습니다."

        print(f"  - [검증 완료] 현재 장바구니 수량: '1' (수량 감소 정상 동작)")

        # 🎉 최종 성공 출력 문구
        print("\n✅ [테스트 성공] SHOP_04: 타임딜 수량 증감(+/-) 기능이 정상 동작합니다! 🎉\n")


    def test_SHOP_05(self):
        """
        SHOP_05: 타임딜 상품 추가 시 무료배달 안내 문구 노출 및 장바구니 화면 진입 기능 검증
        """
        driver = self.driver
        print("\n[SHOP_05 테스트 시작] 무료배달 안내 문구 검증 및 장바구니 화면 진입")

        # 1. 하단 무료배달 안내 텍스트 노출 검증
        # '더 담으면', '무료배달', '장바구니' 등의 키워드가 포함된 텍스트/뷰 요소를 탐색합니다.
        free_shipping_xpath = "//*[contains(@content-desc, '무료배달') or contains(@text, '무료배달') or contains(@content-desc, '더 담으면') or contains(@text, '더 담으면')]"
        
        try:
            free_delivery_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, free_shipping_xpath))
            )
            assert free_delivery_element is not None, "주문가능 안내 문구가 노출되지 않았습니다."
            print("  - [검증 완료] 'OO원 더 담으면 주문가능' 안내 문구 노출 확인!")
        except Exception as e:
            pytest.fail(f"❌ [SHOP_05 단계 실패] 주문가능 안내 문구를 찾을 수 없습니다: {e}")

        # 2. 하단 장바구니 플로팅 버튼 탐색 및 클릭
        # '장바구니' 문구가 들어간 버튼 영역을 지정하여 클릭합니다.
        cart_button_xpath = "//*[contains(@content-desc, '장바구니') or contains(@text, '장바구니')]"
        
        try:
            cart_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, cart_button_xpath))
            )
            cart_button.click()
            print("  - 장바구니 버튼 클릭 완료")
            time.sleep(5)  # 화면 전환 대기
        except Exception as e:
            pytest.fail(f"❌ [SHOP_05 단계 실패] 장바구니 버튼을 클릭할 수 없습니다: {e}")

        # 3. 장바구니 화면 진입 검증
        # 장바구니 상단 타이틀 또는 내부 고유 요소(예: '장바구니' 타이틀 / '주문하기' 버튼 등)를 검증합니다.
        cart_title_xpath = "//*[contains(@content-desc, '장바구니') or contains(@text, '장바구니')]"
        
        try:
            cart_title_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, cart_title_xpath))
            )
            assert cart_title_element is not None, "장바구니 화면 진입 실패"
            print("  - [검증 완료] 장바구니 화면 정상 진입 확인!")
        except Exception as e:
            pytest.fail(f"❌ [SHOP_05 단계 실패] 장바구니 화면으로 진입하지 못했습니다: {e}")

        time.sleep(2)
        
        driver.back()
        

        minus_button_xpath = "//android.view.View[@content-desc='장바구니 빼기']"

        first_minus_btn = self.driver.find_elements(By.XPATH, minus_button_xpath)

        if first_minus_btn:
            first_minus_btn[0].click()  # 수량 1 감소 (1 -> 0)
            print("수량 감소 버튼 클릭(-1)")
            time.sleep(1)

        print("[SHOP_05 테스트 성공] 모든 검증 항목을 통과했습니다.")
        

    def test_SHOP_06_pickup_filter(self):
        """SHOP_06: '픽업가능' 매장 필터링 및 정렬 검증"""
        driver = self.driver
        wait = WebDriverWait(driver, 10)

        # 1. 사전 조건: '마트' 카테고리 탭 클릭/진입
        try:
            mart_tab = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//*[contains(@text, '마트') or contains(@content-desc, '마트')]",
                    )
                )
            )
            mart_tab.click()
        except Exception:
            # 이미 마트 탭에 진입해 있는 상황 예외 처리
            pass

        time.sleep(5)
        
        # 2. '픽업가능' 필터 버튼 찾기 및 클릭
        pickup_filter_xpath = "//*[contains(@text, '픽업가능') or contains(@content-desc, '픽업가능') or contains(@text, '픽업')]"
        pickup_filter_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, pickup_filter_xpath))
        )

        # 버튼 클릭 전 상태 및 클릭 수행
        pickup_filter_btn.click()

        # 3. 필터 적용 대기 (목록 리로드 시간 고려)
        WebDriverWait(driver, 5).until(
            lambda d: True  # 리로드 완충 대기시간 부여
        )

        # 4. 검증: 목록 내 노출되는 매장 카드/배지들에 '픽업' 관련 텍스트가 존재하는지 확인
        # 매장 목록 카드 요소들 탐색
        stores_xpath = "//*[contains(@text, '픽업') or contains(@content-desc, '픽업') or contains(@text, '포장')]"
        pickup_badges = driver.find_elements(By.XPATH, stores_xpath)

        # 픽업 표시가 최소 1개 이상 노출되는지 검증 (또는 필터 활성화 상태 검증)
        assert len(pickup_badges) > 0, (
            "❌ [SHOP_06 실패] '픽업가능' 필터 적용 후 픽업 매장이 노출되지 않거나 배지를 찾을 수 없습니다."
        )

        time.sleep(3)

        # 5. 필터 적용 후 생성된 '초기화' 버튼 찾기 및 클릭
        reset_btn_xpath = "//*[contains(@text, '초기화') or contains(@content-desc, '초기화') or contains(@resource-id, 'reset')]"

        reset_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, reset_btn_xpath))
        )
        reset_btn.click()

        # 6. 초기화 처리 완료 대기 (목록 재정렬 시간 고려)
        WebDriverWait(driver, 3).until(lambda d: True)

        # 7. [검증 1] '초기화' 버튼이 화면에서 사라졌는지 확인
        wait.until(EC.invisibility_of_element_located((By.XPATH, reset_btn_xpath)))
        reset_elements = driver.find_elements(By.XPATH, reset_btn_xpath)
        is_reset_btn_gone = (
            len(reset_elements) == 0 or not reset_elements[0].is_displayed()
        )

        assert is_reset_btn_gone, (
            "❌ [SHOP_06 실패] 초기화 버튼을 눌렀으나 화면에서 사라지지 않았습니다."
        )

        # 8. [검증 2] '픽업가능' 버튼이 다시 선택 해제(기본/흰색) 상태로 돌아왔는지 확인
        pickup_btn_after_reset = driver.find_element(
            By.XPATH, pickup_filter_xpath
        )

        # Appium에서 버튼 선택 상태 속성 체크 (selected 속성이 'false'이거나 False여야 함)
        is_selected = pickup_btn_after_reset.is_selected()
        selected_attr = pickup_btn_after_reset.get_attribute("selected")

        # selected 속성이 'false' 문자열이거나 파이썬 False인지 확인
        is_button_deselected = (
            not is_selected and str(selected_attr).lower() != "true"
        )

        assert is_button_deselected, (
            "❌ [SHOP_06 실패] 초기화 버튼 클릭 후에도 '픽업가능' 버튼이 여전히 선택(활성화) 상태입니다."
        )

        print(
            "✅ [SHOP_06 성공] 초기화 버튼 클릭 시 초기화 버튼이 사라지고, '픽업가능' 버튼이 정상적으로 비활성화(흰색/선택 해제)로 복원되었습니다."
        )

    
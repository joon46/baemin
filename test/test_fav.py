import pytest
import time
from appium import webdriver
from appium.options.common import AppiumOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestBaeminFavorite:

    # 테스트 실행 전 드라이버 초기화
    def setup_method(self, method):
        options = AppiumOptions()
        options.set_capability("platformName", "Android")
        options.set_capability("automationName", "UiAutomator2")
        options.set_capability("deviceName", "Android Emulator")  # 또는 연결된 기기 이름
        options.set_capability("appPackage", "com.sampleapp") # 배민 패키지명 (실제 설정에 맞게 수정)
        options.set_capability("appActivity", "com.baemin.presentation.ui.root.ui.RootContainerActivity") # 실제 액티비티명
        options.set_capability("noReset", True)

        # Appium 서버 연결
        self.driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

    # 테스트 종료 후 드라이버 정리
    def teardown_method(self, method):
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()

    
    def test_HT_01_empty_favorite_go_to_shopping_store(self):
        """
        [HT_01] 찜한 가게 목록(장보기·쇼핑)이 비어있을 때 '가게 둘러보기' 클릭 시 장보기·쇼핑 페이지 이동 검증
        """
        driver = self.driver
        wait = WebDriverWait(driver, 10)

        # 1. '찜' 목록 화면 진입
        fav_tab = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//androidx.compose.ui.platform.ComposeView[@resource-id='com.sampleapp:id/bottomTabBar']/android.view.View/android.view.View/android.view.View[3]/android.widget.Button"))
        )
        fav_tab.click()

        # 2. '장보기·쇼핑' 카테고리 탭 선택
        shopping_tab = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//android.widget.TextView[@text='장보기·쇼핑' or contains(@content-desc, '장보기')]"))
        )
        shopping_tab.click()
        time.sleep(1)

        # 3. 가게 탭 클릭 
        store_tab = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//android.widget.TextView[@text='가게' or contains(@content-desc, '가게')]"))
        )
        store_tab.click()
        time.sleep(1)

        # 4. 빈 화면 내 '가게 둘러보기' 버튼 클릭
        explore_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@text='가게 둘러보기' or @text='상품 둘러보기' or contains(@text, '둘러보기')]"))
        )
        explore_button.click()

        # 5. 검증: 장보기·쇼핑 메인 페이지 진입 여부 확인
        shopping_main_element = wait.until(
            EC.visibility_of_element_located((
                By.XPATH, 
                "//android.widget.Button[@content-desc='장보기·쇼핑']"
            ))
        )

        assert shopping_main_element.is_displayed(), "❌ 실패: '가게 둘러보기' 클릭 후 장보기·쇼핑 페이지로 정상 이동하지 않았습니다."
        print("\n✅ 성공 [HT_03]: '가게 둘러보기' 클릭 시 장보기·쇼핑 페이지로 정상 이동했습니다.")

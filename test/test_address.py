import pytest
import time
from appium import webdriver
from appium.options.common import AppiumOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture(scope="class")
def driver_setup(request):
    options = AppiumOptions()
    options.set_capability("platformName", "Android")
    options.set_capability("automationName", "UiAutomator2")
    options.set_capability("deviceName", "Android Emulator")
    options.set_capability("appPackage", "com.sampleapp")
    options.set_capability("appActivity", "com.baemin.presentation.ui.root.ui.RootContainerActivity")
    options.set_capability("noReset", True)

    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    
    if request.cls is not None:
        request.cls.driver = driver
        
    yield driver
    driver.quit()


@pytest.mark.usefixtures("driver_setup")
class TestBaeminAddress:

    def test_ADDR_01_invalid_search_character(self):
        """
        ADDR_01: 잘못된 주소 형식 처리 (특수문자 '%%' 검색 예외 처리)
        사전 조건: '주소 설정' 화면으로 진입한 상태
        """
        driver = self.driver
        wait = WebDriverWait(driver, 10)
        print("\n[ADDR_01 테스트 시작] 특수문자('%%') 입력 시 예외 처리 문구 및 안정성 검증")

        # 1. 주소 검색창 클릭 및 이동
        search_bar_xpath = "//*[contains(@resource-id, 'search') or contains(@text, '검색') or contains(@content-desc, '검색')]"
        try:
            search_bar = wait.until(EC.element_to_be_clickable((By.XPATH, search_bar_xpath)))
            search_bar.click()
            print("  - [진행] 주소 검색창 클릭하여 입력 화면 진입")
            time.sleep(1)
        except Exception as e:
            pytest.fail(f"❌ [ADDR_01 단계 실패] 주소 검색창 진입 불가: {e}")

        # 2. 특수문자 '%%' 입력 및 검색 진행
        search_input_xpath = "//android.widget.EditText"
        try:
            search_input = wait.until(EC.presence_of_element_located((By.XPATH, search_input_xpath)))
            search_input.clear()
            search_input.send_keys("%%")
            print("  - [진행] 주소 검색창에 '%%' 특수문자 입력 완료")

            # 엔터/검색 버튼 클릭
            # 💡 [핵심] 키보드 돋보기/엔터 버튼 동작 처리
            # 방법 A: 키코드 66 (KEYCODE_ENTER) 전달
            driver.press_keycode(66)
            
            # (대안) 키보드의 검색 동작 완료 처리시:
            # driver.execute_script('mobile: performEditorAction', {'action': 'search'})
            print("  - [진행] 검색 버튼 클릭")
            time.sleep(1.5)
        except Exception as e:
            pytest.fail(f"❌ [ADDR_01 단계 실패] 검색어 입력 및 검색 실행 실패: {e}")

        # 3. 예외 안내 문구 노출 검증 ("검색 결과가 없습니다")
        empty_msg_xpath = "//*[contains(@text, '검색결과가 없습니다') or contains(@content-desc, '검색 결과가 없습니다')]"
        try:
            empty_msg_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, empty_msg_xpath))
            )
            assert empty_msg_element is not None, "검색 결과가 없다는 안내 문구가 노출되지 않았습니다."
            print("  - [검증 완료] '검색결과가 없습니다' 안내 메시지 정상 노출 확인!")
        except Exception as e:
            pytest.fail(f"❌ [ADDR_01 실패] 특수문자 입력 시 예외 안내 문구가 노출되지 않거나 크래시 발생: {e}")

        print("✅ [ADDR_01 테스트 성공] 잘못된 주소 형식 예외 처리가 정상 동작합니다! 🎉\n")

        time.sleep(2)

        


    def test_ADDR_02_missing_detail_address(self):
        """
        ADDR_02: 필수 데이터 입력 안 했을 경우 (상세 주소 미입력 경고)
        사전 조건: '주소 검색' 화면 진입 상태
        """
        driver = self.driver
        wait = WebDriverWait(driver, 10)
        print("\n[ADDR_02 테스트 시작] 상세 주소 미입력 시 경고 멘트 노출 검증")

        # 1. 특정 주소 검색 ('연세대 과학관')
        try:
            search_input = wait.until(EC.presence_of_element_located((By.XPATH, "(//android.widget.EditText)[1]")))
            search_input.clear()
            search_input.send_keys("연세대 과학관")
            time.sleep(1)

            # 💡 [핵심] 뒤로가기 버튼에 쏠린 포커스를 풀기 위해 EditText를 다시 한 번 터치
            search_input.click()
            print("  - [진행] 검색창 재터치하여 포커스 복구")
            time.sleep(0.5)

            # 포커스가 잡힌 상태에서 키보드 엔터(KeyCode 66) 실행
            driver.press_keycode(66)
            
            print("  - [진행] '연세대 과학관' 주소 검색 수행")
            time.sleep(1.5)
        except Exception as e:
            pytest.fail(f"❌ [ADDR_02 단계 실패] 주소 검색 실패: {e}")

        # 2. 검색 결과 항목 클릭하여 상세 주소 입력 화면으로 진입
        result_item_xpath = "//*[contains(@text, '연세대학교 과학관')]"
        try:
            result_item = wait.until(EC.element_to_be_clickable((By.XPATH, result_item_xpath)))
            result_item.click()
            print("  - [진행] 검색 결과 항목 클릭하여 상세 설정 화면 진입")
            time.sleep(1)
        except Exception as e:
            pytest.fail(f"❌ [ADDR_02 단계 실패] 주소 검색 결과 항목 선택 불가: {e}")

        # 3. 상세 주소 비워둔 채 다른 입력 영역(공동현관 등) 또는 완료 클릭하여 포커스 이동
        other_input_xpath = "//*[contains(@text, '공동현관') or contains(@content-desc, '공동현관')]"
        try:
            driver.back() # 키보드 치우기

            other_field = wait.until(EC.element_to_be_clickable((By.XPATH, other_input_xpath)))
            other_field.click()
            print("  - [진행] 상세 주소 미입력 상태로 다른 필드/완료 영역 터치")
            time.sleep(1)
        except Exception as e:
            pytest.fail(f"❌ [ADDR_02 단계 실패] 포커스 이동 조작 실패: {e}")

        # 4. 빨간 경고 멘트 노출 여부 검증
        warning_msg_xpath = "//*[contains(@text, '정확한 상세주소를 입력해주세요') or contains(@content-desc, '정확한 상세주소를 입력해주세요')]"
        try:
            warning_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, warning_msg_xpath))
            )
            assert warning_element is not None, "상세주소 입력 유효성 경고 멘트가 노출되지 않았습니다."
            print("  - [검증 완료] '정확한 상세주소를 입력해주세요' 빨간 멘트 노출 확인!")
        except Exception as e:
            pytest.fail(f"❌ [ADDR_02 실패] 필수 입력값 누락 시 경고 문구가 노출되지 않았습니다: {e}")

        print("✅ [ADDR_02 테스트 성공] 상세주소 유효성 검사 멘트가 정상적으로 표시됩니다! 🎉\n")


    def test_ADDR_03_add_new_address(self):
        """
        ADDR_03: 새로운 주소 추가
        사전 조건: '주소 상세' 입력 화면 진입 상태
        """
        driver = self.driver
        wait = WebDriverWait(driver, 10)
        print("\n[ADDR_03 테스트 시작] 신규 주소 등록 및 저장 상태 검증")

        # 1. 상세주소에 '1F' 작성
        detail_input_xpath = "//android.widget.EditText[contains(@text, '건물명') or contains(@content-desc, '상세') or position()=1]"
        try:
            detail_input = wait.until(EC.presence_of_element_located((By.XPATH, detail_input_xpath)))
            detail_input.clear()
            detail_input.send_keys("1F")
            print("  - [진행] 상세주소 필드에 '1F' 입력 완료")
            time.sleep(1)
        except Exception as e:
            pytest.fail(f"❌ [ADDR_03 단계 실패] 상세주소 텍스트 입력 실패: {e}")

        # 2. 주소등록(완료) 버튼 클릭
        submit_btn_xpath = "//*[contains(@text, '주소 등록') or contains(@content-desc, '주소 등록') or contains(@text, '완료')]"
        try:
            submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, submit_btn_xpath)))
            submit_btn.click()
            print("  - [진행] '주소등록' 버튼 클릭 완료")
            time.sleep(2)
        except Exception as e:
            pytest.fail(f"❌ [ADDR_03 단계 실패] 주소등록 버튼 클릭 불가: {e}")

        # 3. 신규 주소 등록 완료 확인 (주소 설정/목록 화면에서 '과학관 1F'가 포함되어 있는지 검증)
        added_address_xpath = "//*[contains(@text, '과학관 1F') or contains(@content-desc, '과학관 1F')]"
        try:
            # 등록 완료하면 홈 화면으로 돌아오므로 주소 상세화면 다시 들어가야 함
            address_information = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(@content-desc, '현재 위치를 변경할 수 있습니다.')]")))
            address_information.click()


            added_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, added_address_xpath))
            )
            assert added_element is not None, "주소 목록 화면에서 신규 등록된 주소를 확인할 수 없습니다."
            print("  - [검증 완료] 새로운 주소 등록 완료 (주소 목록 내 '1F' 확인!)")
        except Exception as e:
            pytest.fail(f"❌ [ADDR_03 실패] 신규 주소가 정상적으로 추가/등록되지 않았습니다: {e}")

        print("✅ [ADDR_03 테스트 성공] 새로운 주소 추가 기능이 정상 동작합니다! 🎉\n")


    def test_ADDR_04_delete_address(self):
        """
        ADDR_04: 등록된 주소 삭제
        사전 조건: 등록한 주소 목록 화면
        """
        driver = self.driver
        wait = WebDriverWait(driver, 10)
        print("\n[ADDR_04 테스트 시작] 등록된 주소 삭제 기능 검증")

        # 사전조건 : 현재 설정된 주소는 삭제를 못해서 다른 주소로 변경해야 함

        change = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(@content-desc, '인천대학교')]")))
        change.click()

        print("  - [사전 조건] 현재 설정된 주소가 아니어야 삭제 가능")

        # 1. 배달주소 수정/삭제 화면 들어가기
        
        address = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(@content-desc, '현재 위치를 변경할 수')]")))
        address.click()
        
        # 주소 수정/삭제 화면 진입 버튼
        update_delete_path = "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[3]/android.view.View/android.view.View[2]/android.view.View/android.widget.Button"
        try:
            update_delete = wait.until(EC.element_to_be_clickable((By.XPATH, update_delete_path)))
            update_delete.click()

            
            print("  - [진행] 주소 목록 수정/삭제 화면 접속 버튼 클릭")
            time.sleep(1.5)
        except Exception as e:
            pytest.fail(f"❌ [ADDR_04 단계 실패] 주소 수정/삭제 화면을 찾을 수 없거나 클릭 불가: {e}")


        # 2. 기존 주소의 '삭제' 버튼 위치 지정 및 클릭
            
        delete_btn_xpath = "(//*[contains(@text, '삭제') or contains(@content-desc, '삭제')])[1]"

        try:

            delete_btn = wait.until(EC.element_to_be_clickable((By.XPATH, delete_btn_xpath)))
            delete_btn.click()
            print("  - [진행] 목록 첫 번째 주소 항목의 '삭제' 버튼 클릭")
            time.sleep(1.5)

            # 버튼이 한 번 더 나옴
            real_delete = wait.until(EC.element_to_be_clickable((By.XPATH,"//android.view.ViewGroup/android.view.View/android.view.View/android.view.View/android.view.View[4]/android.widget.Button")))
            real_delete.click()

        except Exception as e:
            pytest.fail(f"❌ [ADDR_04 단계 실패] 주소 삭제 버튼을 찾을 수 없거나 클릭 불가: {e}")

        # 3. 삭제 처리 반영을 위한 대기
        WebDriverWait(driver, 3).until(lambda d: True)

        # 4. [검증] 삭제한 항목('연세대학교 과학관 1F')이 화면에 더 이상 노출되지 않는지 확인
        target_addr_xpath = "//*[contains(@text, '1F') or contains(@content-desc, '1F')]"
        try:
            wait.until(EC.invisibility_of_element_located((By.XPATH, target_addr_xpath)))
            remaining_elements = driver.find_elements(By.XPATH, target_addr_xpath)
            
            is_deleted = len(remaining_elements) == 0 or not remaining_elements[0].is_displayed()
            assert is_deleted, "삭제한 주소가 여전히 목록 화면에 남아있습니다."
            print("  - [검증 완료] 삭제된 주소가 목록에서 제거되었음을 확인!")
        except Exception as e:
            pytest.fail(f"❌ [ADDR_04 실패] 주소를 삭제했으나 목록 화면에서 제거되지 않았습니다: {e}")

        print("✅ [ADDR_04 테스트 성공] 등록된 주소 삭제 기능이 정상 동작합니다! 🎉\n")
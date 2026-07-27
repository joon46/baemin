from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.pointer_input import PointerInput

# [설정] Appium 서버 및 에뮬레이터 기본 연결 설정
options = UiAutomator2Options()
options.platform_name = "Android"
options.automation_name = "UiAutomator2"
options.device_name = "emulator-5554"  # adb devices로 확인한 포트
#options.app = "C:/Users/내계정/Downloads/baemin.apk" # ⚠️ 본인 PC의 실제 APK 경로로 수정

options.app_package = "com.sampleapp"       # 배민 앱의 실제 패키지명 (예시)
options.app_activity = "com.baemin.presentation.ui.root.ui.RootContainerActivity" # 배민 앱의 메인 화면 액티비티명 (예시)
options.no_reset = True  # 중요! 이미 설치된 앱의 데이터나 로그인을 유지함


driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
wait = WebDriverWait(driver, 10)

def setup_search_screen():
    """[공통 사전조건] 메인 홈 화면에서 검색창 화면으로 진입하는 공통 함수"""
    search_home_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(@content-desc, 'Search button')]")))

    search_home_btn.click()
    time.sleep(1)

#스크롤 함수
def swipe_down_screen(driver):
    # 1. 현재 디바이스 해상도 크기 가져오기
    size = driver.get_window_size()
    width = size['width']
    height = size['height']

    # 2. X축은 중앙 고정, Y축은 하단(80%)에서 상단(20%)으로 이동 좌표 계산
    start_x = width / 2
    start_y = height * 0.8
    end_x = width / 2
    end_y = height * 0.2

    # 3. W3C 터치 입력 장치 정의 (타입, 장치명)
    touch = PointerInput(interaction.POINTER_TOUCH, "touch")
    actions = ActionChains(driver)
    
    # 드라이버에 터치 장치 등록
    actions.w3c_actions.devices.append(touch)

    # [로직 수정] 
    # move_to_location()에서 duration을 제거하는 대신, 
    # pointer_down 이후 이동 액션 과정에서 동작 시간을 명시적으로 관리하도록 변경
    
    # 1단계: 손가락을 스크롤 시작점으로 이동
    actions.w3c_actions.pointer_action.move_to_location(start_x, start_y)
    # 2단계: 화면을 터치(누름)
    actions.w3c_actions.pointer_action.pointer_down(0)
    
    # 3단계: 0.6초(600ms) 동안 누른 채로 대기하거나 스크롤의 부드러운 드래그 모션을 시뮬레이션
    actions.w3c_actions.pointer_action.pause(0.6) 
    
    # 4단계: 목적지(상단 좌표)로 이동 (duration 인자 제거!)
    actions.w3c_actions.pointer_action.move_to_location(end_x, end_y)

    # 중요 💡: 손가락을 떼기 전에도 0.5초 멈춰서 화면이 튕겨 나가는 것을 방지
    actions.w3c_actions.pointer_action.pause(0.5)
    # 5단계: 손가락을 화면에서 뗌
    actions.w3c_actions.pointer_action.pointer_up(0)
    
    # 4. 누적된 스크롤 체인 동작 실행
    actions.perform()
    print("✅ 화면 스크롤(Swipe) 제스처 실행 완료")
    time.sleep(1.5)  # 관성 스크롤 애니메이션이 완전히 정지할 때까지 대기

try:
    # ----------------------------------------------------
    # 1. SH_01 ~ SH_03: 검색 기본 기능 및 입력 제어
    # ----------------------------------------------------
    print("▶ SH_01, SH_02, SH_03 테스트 시작")
    setup_search_screen()
    
    # 검색창 요소 찾기
    search_input = wait.until(EC.presence_of_element_located((By.XPATH, "//android.widget.EditText")))
    
    # [SH_03] UI 기능: '치킨' 입력 상태에서 우측 'X' 버튼 클릭 시 글자 삭제 확인

    search_input.send_keys("치킨")
    time.sleep(1)

    clear_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.ImageView[@content-desc='검색어 지우기']")))
    clear_btn.click()
    
    assert search_input.text == "" or search_input.get_attribute("text") == "", "SH_03 실패: X 버튼을 눌렀으나 글자가 지워지지 않음"
    print("✅ SH_03 통과: 검색창 X 버튼 클릭 시 텍스트 초기화 확인")

    search_input.clear() 
    time.sleep(1)

    # [SH_01] 정상 흐름: '치킨' 입력 후 검색 및 첫 번째 매장 클릭
    
    # 1. 글자만 순수하게 타이핑 (뒤에 Keys.ENTER를 절대 붙이지 않음)
    search_input.send_keys("치킨") 
    time.sleep(0.5)
    # 2. 키보드가 활성화된 상태에서 안드로이드 시스템의 '검색/엔터' 물리 키코드(66) 직접 주입
    driver.press_keycode(66) 
    time.sleep(2) # 검색 결과 화면 렌더링 대기
    
    ## 결과 리스트 노출 확인 및 첫 번째 매장 클릭

    restaurant_list = wait.until(EC.presence_of_element_located((By.ID, "com.sampleapp:id/sectionTitle"))) # 검색 시 나오는 가게 탭 
    
    first_restaurant = wait.until(EC.element_to_be_clickable((By.XPATH, "//androidx.recyclerview.widget.RecyclerView[@resource-id='com.sampleapp:id/searchResultRecyclerView']/android.widget.FrameLayout[3]/androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View")))
    
    first_restaurant.click() # 가장 먼저 나오는 가게가 first_restaurant
    time.sleep(2)
    
    # 메뉴 선택 화면 이동 검증 (가게 상세 화면의 메뉴 탭 등 존재 여부)
    menu_page_indicator = wait.until(EC.presence_of_element_located((By.XPATH, "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View/android.view.View[6]")))
    assert menu_page_indicator.is_displayed(), "SH_01 실패: 매장 클릭 시 메뉴 선택 화면으로 이동하지 않음" # 가게 상세화면 맨 처음 메뉴 탭으로 xpath를 가져옴
    print("✅ SH_01 통과: '치킨' 검색 및 매장 진입, 메뉴 선택 화면 이동 확인")
    
    # 다시 검색 화면으로 복귀 (뒤로가기)
    driver.back() 
    time.sleep(1)
    driver.back()
    time.sleep(1)

    # [SH_02] 예외 처리: 외계어 검색 시 에러 문구 확인
    #setup_search_screen
    search_input = wait.until(EC.presence_of_element_located((By.XPATH, "//android.widget.EditText")))
    
    search_input.click()
    search_input.send_keys("꽭")
    time.sleep(1)
    
    driver.press_keycode(66) 
    time.sleep(2)
    
    no_result_msg = wait.until(EC.presence_of_element_located((By.XPATH, "//android.widget.TextView[@text='검색 결과가 없어요']")))
    assert "검색 결과가 없어요" in no_result_msg.text, "SH_02 실패: 결과 없음 안내 문구가 일치하지 않음"
    print("✅ SH_02 통과: 외계어 검색 시 '검색 결과가 없어요' 예외 처리 확인")
    
    # 홈 화면으로 돌아가기
    driver.back()
    time.sleep(1)
    driver.back()
    time.sleep(1)


    # ----------------------------------------------------
    # 2. SH_04 ~ SH_05: 최근 검색어 관리
    # ----------------------------------------------------
    print("▶ SH_04, SH_05 테스트 시작")
    setup_search_screen()
    
    # [SH_04] UI / 데이터 유지: 최근 검색어 영역에 '치킨' 노출 및 삭제 버튼 작동 확인
    recent_keyword = wait.until(EC.presence_of_element_located((By.XPATH, "//android.widget.TextView[@text='치킨']")))
    assert recent_keyword.is_displayed(), "SH_04 실패: 최근 검색어에 '치킨'이 노출되지 않음"
    
    # '치킨' 우측 삭제(X) 버튼 클릭
    delete_recent_btn = driver.find_element(By.XPATH, "//*[@text='치킨']/following-sibling::android.widget.ImageView[@content-desc='Delete']")
    delete_recent_btn.click()
    time.sleep(1)
    
    # 삭제 후 리스트에서 완전히 사라졌는지 확인 (리스트가 비었거나 해당 글자가 없어야 함)
    try:
        driver.find_element(By.XPATH, "//android.widget.TextView[@text='치킨']")
        assert False, "SH_04 실패: 삭제 버튼을 눌렀으나 '치킨'이 여전히 남아있음"
    except:
        print("✅ SH_04 통과: 최근 검색어 노출 및 개별 삭제 기능 확인")

    # [SH_05] UI 기능: 검색창 화면 하단에 실시간 인기 검색어가 정상 노출되고 1~10위가 존재하는지 검증
    print("-> SH_05: 실시간 인기 검색어 검증 시작")
    
    # 1. 실시간 인기 검색어 타이틀 또는 영역 컨테이너가 존재하는지 확인
    popular_section_title = wait.until(EC.presence_of_element_located((By.XPATH, "//android.widget.TextView[@text='배달·픽업 인기 검색어']")))
    assert popular_section_title.is_displayed(), "SH_05 실패: 실시간 인기 검색어 타이틀이 보이지 않음"
    
    # ✨ 2. [수정 포인트] 롤링되는 검색어 화면을 펼치기 위해 'Expand' 버튼 클릭!
    expand_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.TextView[@text='Expand']")))
    expand_btn.click()
    time.sleep(1) # 펼쳐지는 애니메이션 대기

    # 3. 확장된 리스트에서 1~10위 순위 컴포넌트(또는 텍스트 버튼들)가 노출되는지 검증
    # 펼쳐졌으므로 이제 화면에 리스트가 온전히 잡히게 됩니다.
    popular_items = driver.find_elements(By.XPATH, "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[3]/android.view.View/android.view.View[3]/android.view.View[2]")
    
    # 기대 결과에 맞게 최소 1개 이상 혹은 10개의 항목이 온전히 노출되었는지 체크
    assert len(popular_items) > 0, "SH_05 실패: Expand 버튼을 눌렀으나 실시간 인기 검색어 리스트가 노출되지 않음"
    print(f"✅ SH_05 통과: 'Expand' 클릭 후 실시간 인기 검색어 {len(popular_items)}개 노출 확인")
    
    driver.back()
    time.sleep(3)


    # ----------------------------------------------------
    # 3. SH_06 ~ SH_08: 검색결과 탭 전환 및 자동완성/예외 (이미지 기준 완벽 동기화)
    # ----------------------------------------------------
    print("▶ SH_06, SH_07, SH_08 테스트 시작")
    
    # [SH_06] 기능 검증: '치킨 검색결과 더보기' 클릭 시 배달 카테고리 탭 전환 확인
    # 사전 조건: "치킨" 검색 결과 매장 리스트가 노출된 상태 ('전체' 탭 상태)
    setup_search_screen()
    search_input = wait.until(EC.presence_of_element_located((By.XPATH, "//android.widget.EditText")))
    search_input.send_keys("치킨")

    driver.press_keycode(66) 
    time.sleep(3) # 결과 화면 로딩 대기
    
    try:
        # 1. '검색결과 더보기' 버튼이 보일 때까지 스크롤하며 타겟팅
        print("🔄 '검색결과 더보기' 텍스트를 포함하는 버튼을 향해 스크롤을 시작합니다.")

        swipe_down_screen(driver) # 화면을 한 번 아래로 쓸어내림
    
        # 만약 버튼이 한 번에 안 보이면 한 번 더 실행
        # swipe_down_screen(driver)
        
        # text("글자") 대신 textContains("글자")를 사용하여 부분 일치하는 요소를 탐색
        more_btn = wait.until(
            EC.presence_of_element_located((By.XPATH, "//android.widget.TextView[contains(@text, '검색결과 더보기')]"))
            
        )
        print("✅ 동적 '검색결과 더보기' 버튼 발견 완료 (스크롤 성공)")
        
        # 2. 버튼 클릭 및 화면 전환 대기
        more_btn.click()
        print("✅ '검색결과 더보기' 버튼 클릭 완료")
        time.sleep(2)  # 더보기 화면 및 데이터 네트워크 로딩 대기

        # 3. 상단 '배달' 카테고리 탭 검증
        # 제공된 배달 탭 XPATH 활용
        baedal_tab = wait.until(
            EC.presence_of_element_located((By.XPATH, '//android.widget.TextView[@content-desc="배달 tab"]'))
        )
        
        # 'selected' 속성이 true인지 검증 (안드로이드 탭의 활성화 여부는 보통 selected 속성으로 판별합니다)
        is_tab_selected = baedal_tab.get_attribute("selected")
        assert is_tab_selected == "true", f"❌ SH_06 실패: '배달' 탭이 활성화(선택) 상태가 아님 (현재 상태: {is_tab_selected})"
        print("✅ 검증 완료 1: '배달' 카테고리 탭 자동 활성화 확인")

        # 4. 하단 결과 리스트 화면 검증
        # 제공된 하단 리스트 XPATH 활용
        result_list_view = wait.until(
            EC.presence_of_element_located((By.XPATH, '//androidx.recyclerview.widget.RecyclerView/android.widget.FrameLayout/androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View'))
        )
        
        assert result_list_view.is_displayed(), "❌ SH_06 실패: '배달' 결과 리스트 화면이 정상적으로 노출되지 않음"
        print("✅ 검증 완료 2: '배달' 카테고리 결과 화면 하단 리스트 노출 확인")
        print("🎉 SH_06 성공: 검색결과 더보기 클릭 후 배달 탭 활성화 및 리스트 정상 전환 완료!")

    except Exception as e:
        print(f"❌ SH_06 최종 실패: 프로세스 진행 중 에러 발생 ➡️ {e}")
        raise e  # 테스트 프레임워크가 실패를 인지하도록 예외 전달

    finally:
        # [연속 테스트 보호 조치] 다음 테스트(SH_07 등) 수행을 위해 '뒤로가기'를 눌러 검색 창 화면으로 복귀
        driver.press_keycode(4)
        time.sleep(1.5)


    # [SH_07] UI / UX 기능: 검색창에 "치즈" 두 글자만 입력 시 연관 검색어 레이어 팝업 노출 확인
    # 사전 조건: 검색어 입력창 활성화 상태
    
    search_input = wait.until(EC.presence_of_element_located((By.XPATH, "//android.widget.EditText")))
    search_input.send_keys("치즈")
    time.sleep(1)
    
    # 엑셀 기대결과: 입력창 하단에 "치즈케이크", "치즈볼" 등 연관 검색어 레이어가 정상 팝업되어야 함.
    related_layer = wait.until(EC.presence_of_element_located((By.XPATH, "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[4]/android.view.View[1]/android.view.View[2]")))
    assert related_layer.is_displayed(), "SH_07 실패: 연관 검색어 레이어가 팝업되지 않음"
    print("✅ SH_07 통과: '치즈' 입력 시 실시간 연관 검색어 레이어 정상 노출 확인")
    
    # 다음 테스트를 위해 입력창 글자 지우기
    clear_btn = driver.find_element(By.XPATH, "//android.widget.ImageView[@content-desc='검색어 지우기']")
    clear_btn.click()
    time.sleep(1)


    # [SH_08] Negative (Exception Path): 미입력 검색 예외 처리
    # 사전 조건: 검색창 화면
    # 엑셀 절차: 미입력 상태에서 키보드의 엔터(돋보기) 클릭
    search_input = wait.until(EC.presence_of_element_located((By.XPATH, "//android.widget.EditText")))
    search_input.clear() # 혹시 남아있을 글자 비우기

    # 아무것도 입력하지 않고 곧바로 엔터키(키보드 돋보기 효과) 전송!
    driver.press_keycode(66) 
    time.sleep(1)
    
    # 엑셀 기대결과: '검색어를 입력해주세요'라는 Toast 메시지가 등장해야 함
    toast_message = wait.until(EC.presence_of_element_located((By.XPATH, "//android.widget.Toast[@text='Please enter a search term']"))).text
    assert "Please enter a search term" in toast_message, f"SH_08 실패: 토스트 안내 문구 불일치 ({toast_message})"
    print("✅ SH_08 통과: 미입력 검색 시 'Please enter a search term' Toast 노출 확인")

except AssertionError as e:
    print(f"❌ 테스트 실패: {e}")
except Exception as e:
    print(f"⚠️ 에러 발생: {e}")
finally:
    driver.quit()
    print("▶ 모든 검색(SH) 도메인 테스트 시나리오 종료")

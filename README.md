> test case : https://docs.google.com/spreadsheets/d/14BiPmGkQDoOJl_PA2RA4Gsqe60mS13pW7oZk-md5fGQ/edit?usp=sharing

# 📱 모바일 앱(배달의민족) UI/기능 자동화 테스트 프로젝트

> **Appium**과 **Pytest**를 활용하여 모바일 앱의 핵심 기능 및 예외 시나리오를 검증하고, 동적 대기(Explicit Wait) 및 제스처 제어 기법을 적용한 테스트 자동화 스위트 구축 프로젝트입니다.

---

## 📌 프로젝트 개요

* **대상 애플리케이션**: 배달의민족 Android App (`com.sampleapp`)
* **목적**:
  * 주요 유저 동선(검색, 주소 설정, 찜 목록, 매장 필터링 및 정렬)의 기능 정상 작동 검증
  * 외계어 입력, 빈 값 검색 등 예외 상황 및 경계값에 대한 시스템 안정성 검증
  * 화면 스크롤, Hold(새로고침), 터치 액션 등 모바일 특화 제스처 자동화 구현
* **주요 특징**:
  * `Pytest` 기반의 테스트 모듈화 및 Class/Fixture 관리 (`driver_setup`)
  * `WebDriverWait`과 `Expected Conditions`를 활용한 비동기 UI 대응 (동적 대기)
  * `ActionChains` 및 `PointerInput`을 활용한 복합 제스처 제어

---

## 🛠 기술 스택 (Tech Stack)

| 구분 | 기술 / 도구 |
| :--- | :--- |
| **Language** | Python 3.x |
| **Framework** | Pytest, Appium Python Client |
| **Automation Tool** | Appium Server (UiAutomator2) |
| **Libraries** | Selenium (`WebDriverWait`, `ActionChains`, `By`) |
| **Environment** | Android Emulator (Android OS) |
| **Test Design** | Test Case (TC) 명세서 작성 및 관리 (CSV/Excel) |

---

## 🏗 프로젝트 구조 (Project Structure)

```text
├── Test Case 배민.xlsx - Sheet1.csv  # 명세화된 테스트 케이스 (TC_ID, 우선순위, 절차, 기대결과)
├── test_search.py                    # [SH_01~08] 검색창, 검색어 삭제, 연관검색어, 예외처리 검증
├── test_address.py                   # [ADDR_01~04] 주소 검색 특수문자 예외 처리 및 주소 삭제 검증
├── test_fav.py                       # [HT_03] 찜 목록 진입 및 빈 화면 내 둘러보기 동작 검증
├── test_shop1.py                     # [SHOP_01 ~ 03] 화면 드래그/Hold 제스처를 통한 새로고침 토스트 메시지 검증
├── test_shop2.py                     # [SHOP_04 ~ 06] '픽업가능' 필터링 선택/해제 및 초기화 동작 검증
├── test_shop3.py                     # [SHOP_07 ~ 08] 매장 정렬 필터(거리순 등) 데이터 파싱 및 정렬 검증
└── test_event.py                     # [EV_01 ~ 03] 이벤트 영역에서 권한 검증, 예외 처리 및 버튼 동작 검증


## 🧪 주요 테스트 시나리오 및 검증 내용
1. 검색 및 예외 처리 (test_search.py)
  기능 검증:
   - [SH_01] 검색어 입력후 매장 진입 (EC.presence_of_element_located로 DOM 생성을 확인, EC.element_to_be_clickable로 상호작용 가능 상태를 검증한 후 안전하게 진입 처리.)
   - [SH_06] 카테고리 탭 전환 검증 (EC.presence_of_element_located로 element 확인)
   - [SH_07] 연관 검색어 레이어 실시간 팝업 검증

  예외 처리 (Negative Test):
   - [SH_02] 외계어(꽭) 입력 시 앱 크래시 없이 '검색 결과 없음' 문구 노출 확인 (특정 TextView가 노출되는지 검증)
   - [SH_08] 미입력(빈 값) 상태에서 검색 시 예외 처리 확인

  UI/UX:
   - [SH_03] 입력어 일괄 삭제(X 버튼) (get_attribute 이용해서 검색창 내부 내용 확인)
   - [SH_04] 최근 검색어 노출 및 삭제 (TextView를 is_displayed()로 확인)
   - [SH_05] 검색창 하단 인기검색어 순위 (EC.presence_of_element_located로 DOM 생성을 확인, EC.element_to_be_clickable로 상호작용 가능 상태를 검증)

2. 주소 관리 (test_address.py)

  예외 처리 (Negative Test): 
    - [ADDR_01] 특수문자(%%) 검색 시 예외 처리 동작 검증
    - [ADDR_02] 필수 데이터 입력하지 않았을 경우 예외 처리

  기능 검증 :
    - [ADDR_03] 신규 주소 데이터 추가, 이후 추가 데이터 저장되었는지 검증
    - [ADDR_04] 주소 목록에서 삭제 버튼 클릭 및 2차 확인 팝업 대응 후 대상 항목의 비노출 상태(invisibility_of_element_located) 검증

3. 모바일 제스처 & 비동기 UI 대응 (test_shop1.py, test_shop2.py)
PointerInput과 ActionChains의 w3c를 이용하여 터치, 모션 등을 구현하고 기능 및 UI 검증
- [SHOP_01] 검색창 진입 (webdriverwait으로 대기)
- [SHOP_02] W3C Touch를 활용 스크롤 이후 화면 이동
- [SHOP_03]  PointerInput을 활용해 화면을 누른 채 1.5초간 유지(Hold)하는 동작 구현 후, 생성되는 새로고침 토스트 메시지 감지

수량 증감 동작, 장바구니 진입, 픽업 필터 적용 및 초기화 기능 검증
- [SHOP_04] 타임딜 상품 수량 증감(+/-) 버튼 동작 및 상태 검증
- [SHOP_05] 무료배달 안내 문구 노출 확인 및 장바구니 화면 진입/수량 원복 검증
- [SHOP_06] '픽업가능' 매장 필터링 적용 및 초기화(리셋) 기능 검증 (is_selected 활용)

동적 필터 검증: 필터 버튼 클릭 시 버튼 선택 상태(is_selected) 변경 및 목록 재정렬 반영 확인, '초기화' 버튼 동작 검증

4. 동적 데이터 파싱 및 정렬 검증 (test_shop3.py)
매장 리스트 내 거리 텍스트(817m, 1.2km 등)를 정규표현식(re)으로 추출하여 미터(m) 단위 변환

- [SHOP_07] is_displayed로 주문 가능한 가게 없는지 확인 후 예외처리 
- [SHOP_08] 추출된 데이터가 실제 거리 오름차순(가까운 순)으로 올바르게 정렬되어 있는지 파이썬 로직으로 자동 검증

5. 이벤트 및 혜택 제어 (test_event.py)
W3C 표준 터치 제스처(swipe_down_screen)로 이벤트 상세 페이지 스크롤 동작을 구현하고, WebDriverWait을 통해 비동기식 팝업/모달 노출 상태를 안정적으로 감지

- [EV_01] 배민클럽 미가입자 권한 제한: 미가입 상태에서 '혜택' 광고 진입 후 쿠폰 클릭 시 "발급 대상이 아니에요" 예외 팝업 노출 검증
- [EV_02] 쿠폰 중복 수령 방지: 이미 지급받은 쿠폰('BBQ') 탭 진입 시 다운로드 버튼 대신 "받기 완료" 텍스트/상태 변경 노출 검증
- [EV_03] 할인 정보 설명창 노출: '할인' 광고 페이지의 '할인가게' 탭 진입 후 Info(ℹ️) 아이콘 클릭 시 관련 안내 팝업/설명창 노출 검증

💡 핵심 트러블슈팅 및 기술적 경험
비동기 UI 요소를 위한 동적 대기(Explicit Wait) 적용

Static한 time.sleep() 사용을 최소화하고, WebDriverWait과 expected_conditions를 활용하여 네트워크 지연이나 애니메이션 동작 중에도 안정적으로 요소를 탐색하도록 구현했습니다.

모바일 특화 터치 액션 구현

Appium의 W3C Actions API(ActionChains, PointerInput)를 직접 구성하여 단순 클릭 외에도 Hold(1.5초 누르기) 등의 복합 제스처 스크립트를 작성했습니다.

정규표현식을 이용한 데이터 무결성 검증

화면에 표시되는 복잡한 UI 텍스트 중 필요한 거리 수치만 Regex로 추출/단위 일치화하여, 정렬 로직이 실제 데이터 차원에서 올바른지 검증했습니다.

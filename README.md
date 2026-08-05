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
├── test_shop1.py                     # [SHOP_03] 화면 드래그/Hold 제스처를 통한 새로고침 토스트 메시지 검증
├── test_shop2.py                     # [SHOP_06] '픽업가능' 필터링 선택/해제 및 초기화 동작 검증
└── test_shop3.py                     # [SHOP_08] 매장 정렬 필터(거리순 등) 데이터 파싱 및 정렬 검증

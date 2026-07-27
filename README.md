
구분,기술 스택 / 도구
- Language,Python 3.x
- Framework,Pytest
- Automation Tool,Appium (UiAutomator2 Engine)
- Library,"Selenium WebDriver, Appium Python Client"
- Target Platform,Android Emulator (or Physical Device)
<br>
✨Key Test Scenarios & Coverage <br> <br>

본 프로젝트는 서비스의 핵심 사용자 시나리오 및 예외 상황(Edge Cases)을 자동화하여 검증합니다. <br>

1. 검색 기능 (test_search.py)
- [SH_07] 실시간 연관 검색어 레이어 검증: 키워드 입력 시 화면 하단에 연관 검색어 레이어가 정상 노출되는지 검증

- [SH_08] 미입력 검색 예외 처리: 빈 검색어 상태에서 엔터(검색) 입력 시 앱이 정상 대응하는지 예외 시나리오 테스트

2. 스토어 & 홈 기능 (test_shop1.py)
- [SHOP_03] Pull-to-Refresh 및 토스트 메시지 감지: W3C Actions API(PointerInput) 기반 드래그 제스처로 화면을 당겨 새로고침 시 발생하는 토스트 메시지 수집 및 검증

3. 카테고리 & 예외 안내 (test_shop2.py)
- [SHOP_07] 가로 스크롤 & 미지원 영역 안내 검증: 상단 카테고리 탭 가로 스크롤 수행 후 특정 탭 클릭 시 "근처에 주문 가능한 가게가 없어요" 등의 예외 안내 문구 노출 검증<br>

✨ Key Technical Highlights
- Pytest Fixture 기반 테스트 관리: @pytest.fixture(scope="class")를 활용해 Appium 드라이버의 세션 및 에뮬레이터 연결 상태 관리

- 상태 유지 기능 (noReset & dontStopApp): no_reset=True 및 dontStopApp 옵션을 활용하여 이전 테스트 세션의 앱 화면 상태를 연속성 있게 이어받아 실행 시간 단축

- W3C Actions API 제스처 구현: PointerInput 및 ActionChains를 활용하여 화면 스와이프, Pull-to-Refresh, Hold 제스처 등 모바일 터치 액션 구현

- 동적 대기 및 예외 처리: WebDriverWait와 expected_conditions를 활용해 네트워크 지연이나 비동기 UI 렌더링 환경에서도 안정적인 테스트 수행

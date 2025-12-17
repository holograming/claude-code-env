# 3D PLY Viewer - 빌드 시스템 문제점 및 개선방안

## 1. 빌드 시스템 개요

**프로젝트:** 3D PLY Point Cloud Viewer
**프레임워크:** wxWidgets 3.3.1 (Qt에서 변경됨)
**빌드 도구:** CMake 3.15+
**컴파일러:** MSVC / Clang++
**의존성 관리:** vcpkg (manifest mode)

---

## 2. 주요 문제점

### 2.1 프레임워크 마이그레이션 문제

#### 문제
- **Qt 빌드 실패**: vcpkg에서 Qt5/Qt6 패키지 빌드 실패
  - Qt5는 존재하지만 빌드에 20분 이상 소요
  - Qt6는 vcpkg 포트에 없음
  - 경로 길이 제한 (Windows MAX_PATH 문제)

#### 영향
- 초기 개발 시간 낭비
- 프레임워크 선택 재검토 필요
- 코드 리팩토링 필요 (QMatrix4x4 → glm::mat4, QString → wxString 등)

#### 근본 원인
- Qt의 복잡한 의존성 트리
- vcpkg의 Qt 빌드 최적화 부족
- Windows 경로 길이 제한 (260자)

---

### 2.2 wxWidgets 호환성 문제

#### 문제 1: wxGLCanvas 생성자 호출 오류

**증상:**
```
error C2665: 'wxGLCanvas::wxGLCanvas': 모든 인수 형식을 변환할 수 있는 오버로드된 함수가 없습니다
```

**원인:**
- wxWidgets 3.3.1에서 생성자 시그니처 변경
- 기대: `wxGLCanvas(parent, wxID_ANY, pos, size)`
- 실제: `wxGLCanvas(parent, wxGLAttributes&, wxID_ANY, pos, size)`

**해결:**
```cpp
// Before (실패)
wxGLCanvas(parent, wxID_ANY, wxDefaultPosition, wxSize(1280, 720))

// After (성공)
wxGLCanvas(parent, wxGLAttributes(), wxID_ANY, wxDefaultPosition, wxSize(1280, 720))
```

**예방 방법:**
- 사용 중인 wxWidgets 버전 명시 (vcpkg.json)
- 버전별 호환성 문서 작성

#### 문제 2: Event Table 시스템 충돌

**증상:**
```
error C2491: 'wxGLCanvas::sm_eventTable': dllimport 정적 데이터 멤버를 정의할 수 없습니다
```

**원인:**
- wxGLCanvas가 이미 event table을 가짐
- 파생 클래스에서 event table을 재정의하면 충돌
- wxBEGIN_EVENT_TABLE / wxEND_EVENT_TABLE 매크로 중복 사용

**해결:**
```cpp
// Before (실패)
wxBEGIN_EVENT_TABLE(GLWidget, wxGLCanvas)
    EVT_PAINT(GLWidget::onPaint)
wxEND_EVENT_TABLE()

// After (성공) - Bind() 사용
Bind(wxEVT_PAINT, &GLWidget::onPaint, this);
```

**예방 방법:**
- 최신 wxWidgets에서는 event table 대신 Bind() 권장
- 모든 UI 클래스에 Bind() 방식 사용

---

### 2.3 메뉴 이벤트 바인딩 문제

#### 문제 1: Bind() 메소드 작동 실패

**증상:**
- 메뉴 클릭 후 아무 반응 없음
- 콘솔에 이벤트 로그 출력 안 됨

**원인:**
- Bind()가 메뉴 이벤트 전파에 실패
- wxFrame에서 메뉴 이벤트 라우팅 미지원

**해결:**
```cpp
// Before (실패)
Bind(wxEVT_MENU, &MainWindow::onOpenFile, this, wxID_OPEN);

// After (성공) - Connect() 사용
Connect(wxID_OPEN, wxEVT_MENU, wxCommandEventHandler(MainWindow::onOpenFile));
```

**원인 분석:**
- Bind()는 비교적 최신 메소드 (wxWidgets 2.9+)
- 일부 버전에서 메뉴 이벤트 전파 미지원
- Connect()는 더 오래되고 안정적 (호환성 우수)

#### 문제 2: 메뉴 아이템 ID 값 오류

**증상:**
- resetCameraId = -1 (wxID_ANY)로 설정됨
- 음수 ID는 메뉴 이벤트 바인딩 실패

**해결:**
```cpp
// Before
int resetCameraId = wxID_ANY;  // = -1

// After
int resetCameraId = 10001;  // 명시적 양수 ID
```

---

### 2.4 콘솔 창 표시 문제

#### 문제

**증상:**
- GUI 애플리케이션이 콘솔 창 없이 시작됨
- 디버그 출력 (std::cerr) 볼 수 없음
- 문제 진단 불가능

**원인:**
- CMakeLists.txt에서 WIN32_EXECUTABLE TRUE 설정
- Windows GUI 모드 = 콘솔 창 숨김

#### 해결

```cpp
// main.cpp에서 AllocConsole() 사용
#ifdef _WIN32
    if (AllocConsole()) {
        FILE* pFile = nullptr;
        freopen_s(&pFile, "CONOUT$", "w", stdout);
        freopen_s(&pFile, "CONOUT$", "w", stderr);
        std::cout.clear();
        std::cerr.clear();
    }
#endif
```

**장점:**
- GUI 앱이면서 콘솔 출력 가능
- 디버그 모드에서만 활성화 가능

---

### 2.5 OpenGL 헤더 포함 순서 문제

#### 문제

**증상:**
```
error: 'WINGDIAPI' 재정의
error: 'APIENTRY' 재정의
```

**원인:**
- Windows.h를 GL/gl.h 이후에 포함
- Windows.h와 GL.h의 매크로 정의 충돌

**해결:**
```cpp
// Before (실패)
#include <GL/gl.h>
#include <windows.h>

// After (성공)
#ifdef _WIN32
    #include <windows.h>
#endif
#include <GL/gl.h>
#include <GL/glext.h>
```

---

### 2.6 파일 시스템 및 빌드 캐시 문제

#### 문제 1: 실행 중인 프로세스가 exe 파일 잠금

**증상:**
```
fatal error LNK1104: 'C:\...\3d-viewer.exe' 파일을 열 수 없습니다
```

**원인:**
- 이전 버전의 애플리케이션이 메모리에서 실행 중
- 파일 시스템이 exe를 쓰기 위해 잠금해야 함

**해결:**
- 빌드 전 애플리케이션 종료 필수
- 자동화 스크립트에 프로세스 킬 로직 추가

#### 문제 2: happly 라이브러리 git 태그 오류

**증상:**
```
CMake Error: Failed to checkout tag: 'v0.1'
```

**원인:**
- happly 저장소에 v0.1 태그 없음
- FetchContent에서 잘못된 태그 지정

**해결:**
```cmake
# Before
GIT_TAG v0.1

# After
GIT_TAG master
```

---

## 3. 빌드 프로세스 개선방안

### 3.1 자동화 빌드 스크립트 생성

#### 현재 상태
- PowerShell 스크립트 존재하지만 미흡
- 수동으로 CMake 명령어 실행 필요
- 오류 처리 부재

#### 개선안

**setup.ps1 - 초기 환경 설정**
```powershell
# 기능:
# 1. vcpkg 설치 및 부트스트랩
# 2. CMake 구성
# 3. 프로젝트 구조 검증
```

**build.ps1 - 프로젝트 빌드**
```powershell
# 기능:
# 1. 실행 중인 3d-viewer.exe 프로세스 종료
# 2. 빌드 디렉토리 정리 (optional)
# 3. CMake 구성 및 빌드
# 4. 빌드 실패 시 오류 리포트
# 5. 성공 시 실행 파일 위치 표시
```

**run.ps1 - 애플리케이션 실행**
```powershell
# 기능:
# 1. 빌드된 exe 위치 확인
# 2. DLL 의존성 검증
# 3. 콘솔 창과 함께 실행
```

**clean.ps1 - 빌드 결과물 정리**
```powershell
# 기능:
# 1. build/ 디렉토리 삭제
# 2. CMake 캐시 제거
# 3. 중간 파일 정리
```

### 3.2 CMakeLists.txt 개선

#### 현재 문제
- 의존성 버전 명시 부족
- 컴파일러 호환성 검증 없음
- 오류 메시지 부족

#### 개선사항

```cmake
# 1. 최소 버전 및 정책 설정
cmake_minimum_required(VERSION 3.15)
cmake_policy(SET CMP0091 NEW)  # MSVC runtime 정책

# 2. 의존성 버전 명시
find_package(wxWidgets 3.3 REQUIRED COMPONENTS core base gl)

# 3. 컴파일러 검증
if(MSVC)
    # MSVC 특정 설정
elseif(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    # Clang 특정 설정
endif()

# 4. 상세한 오류 메시지
if(NOT wxWidgets_FOUND)
    message(FATAL_ERROR
        "wxWidgets not found. Install via vcpkg:\n"
        "  vcpkg install wxwidgets:x64-windows"
    )
endif()
```

### 3.3 vcpkg.json 개선

#### 현재 상태
```json
{
  "name": "3d-viewer",
  "version": "1.0.0",
  "dependencies": ["wxwidgets"]
}
```

#### 개선안
```json
{
  "name": "3d-viewer",
  "version": "1.0.0",
  "dependencies": [
    {
      "name": "wxwidgets",
      "version>=": "3.2.0"
    },
    {
      "name": "glm",
      "version>=": "0.9.9"
    }
  ],
  "builtin-baseline": "commit-hash"
}
```

---

## 4. 문제 해결 체크리스트

### 환경 설정 단계
- [ ] Clang++ 컴파일러 설치 (또는 MSVC)
- [ ] vcpkg 설치 및 부트스트랩
- [ ] CMake 3.15+ 설치
- [ ] PowerShell 실행 정책 설정: `Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process`

### 빌드 단계
- [ ] `setup.ps1` 실행 (초기 설정)
- [ ] `build.ps1` 실행 (빌드)
- [ ] 오류 메시지 확인 및 기록
- [ ] 빌드 로그 저장

### 실행 단계
- [ ] `run.ps1` 실행 (앱 시작)
- [ ] 콘솔 창 로그 확인
- [ ] 메뉴 클릭 반응 확인

---

## 5. 빌드 스크립트 생성 현황

### 5.1 생성된 파일

| 파일 | 상태 | 설명 |
|------|------|------|
| setup.ps1 | ✅ 생성됨 | vcpkg 설치 및 초기 설정 |
| build.ps1 | ✅ 생성됨 | CMake 빌드 스크립트 |
| run.ps1 | ✅ 생성됨 | 애플리케이션 실행 |
| clean.ps1 | ✅ 생성됨 | 빌드 결과물 정리 |

### 5.2 개선 필요 사항

#### setup.ps1
```powershell
# 개선 필요:
# 1. vcpkg 경로 자동 감지
# 2. 이미 설치되어 있는지 확인
# 3. 버전 호환성 검증
```

#### build.ps1
```powershell
# 개선 필요:
# 1. 이전 프로세스 자동 종료 (taskkill)
# 2. 빌드 실패 시 자동 재시도
# 3. 컴파일 타임 측정
# 4. 경고/오류 개수 집계
```

#### run.ps1
```powershell
# 개선 필요:
# 1. DLL 의존성 검증
# 2. 콘솔 윈도우 크기 설정
# 3. 작업 디렉토리 설정
```

---

## 6. 권장 워크플로우

### 첫 빌드
```powershell
# 1. 초기 설정
.\setup.ps1

# 2. 빌드
.\build.ps1

# 3. 실행
.\run.ps1
```

### 반복 빌드
```powershell
# 간단히 실행
.\build.ps1
.\run.ps1
```

### 클린 빌드
```powershell
.\clean.ps1
.\setup.ps1
.\build.ps1
```

---

## 7. 향후 개선 계획

### 단기 (1주)
- [ ] PowerShell 스크립트 오류 처리 강화
- [ ] 빌드 로그 파일 자동 저장
- [ ] 컴파일 오류 자동 분석 및 리포트

### 중기 (1개월)
- [ ] GitHub Actions CI/CD 설정
- [ ] 자동 테스트 스크립트 추가
- [ ] 빌드 성공 여부 자동 검증

### 장기 (3개월)
- [ ] vcpkg 버전 고정 (reproducible build)
- [ ] Docker 컨테이너 환경 구성
- [ ] 멀티 플랫폼 빌드 지원 (Linux, macOS)

---

## 8. 참고 자료

### 관련 파일
- `CMakeLists.txt` - 루트 CMake 설정
- `src/CMakeLists.txt` - 소스 빌드 설정
- `cmake/Dependencies.cmake` - 의존성 관리
- `vcpkg.json` - vcpkg 매니페스트

### 유용한 명령어

```powershell
# vcpkg 패키지 검색
.\3rdparty\vcpkg\vcpkg.exe search wxwidgets

# vcpkg 설치된 패키지 확인
.\3rdparty\vcpkg\vcpkg.exe list

# CMake 헬프
cmake --help
cmake --help-manual cmake.1

# 자세한 빌드 로그
cmake --build build --config Release --verbose
```

---

## 결론

### 현재 상황
- ✅ wxWidgets 프레임워크 성공적으로 전환
- ✅ UI 및 파일 로드 완전 작동
- ✅ 빌드 시스템 안정화
- ❌ 렌더링 구현 미완료 (다음 단계)

### 권장사항
1. PowerShell 스크립트 자동화로 빌드 프로세스 간소화
2. CMake 설정 재검토로 버전 호환성 강화
3. 에러 핸들링 및 로깅 메커니즘 개선
4. CI/CD 파이프라인 구축 고려


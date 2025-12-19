# 3D PLY Viewer - 빌드 스크립트 가이드

## 개요

3D PLY Viewer 프로젝트의 빌드 과정을 자동화하는 PowerShell 스크립트 모음입니다.

---

## 1. 생성된 스크립트 목록

| 스크립트 | 용도 | 상태 |
|---------|------|------|
| `setup.ps1` | vcpkg 설치 및 초기 환경 구성 | ✅ 존재 |
| `build.ps1` | CMake 구성 및 프로젝트 빌드 | ✅ **개선됨** |
| `run.ps1` | 빌드된 애플리케이션 실행 | ✅ 존재 |
| `clean.ps1` | 빌드 결과물 제거 | ✅ 존재 |
| `rebuild.ps1` | clean → build 자동 실행 | ✅ 존재 |

---

## 2. 스크립트별 개선 사항

### 2.1 build.ps1 (개선됨)

**개선 전 문제점:**
- ❌ 실행 중인 exe 파일 로킹 오류
- ❌ 오류 메시지 불명확
- ❌ 빌드 성능 측정 불가능

**개선 사항:**
- ✅ 실행 중인 3d-viewer.exe 자동 종료
- ✅ 단계별 진행 상황 표시
- ✅ 빌드 시간 자동 측정
- ✅ 빌드 결과 상세 리포트
- ✅ 색상 코드로 성공/실패 구분
- ✅ `-Clean` 옵션으로 깨끗한 빌드
- ✅ `-Verbose` 옵션으로 상세 로그

**사용 방법:**
```powershell
# 일반 빌드
.\build.ps1

# 깨끗한 빌드 (기존 빌드 결과 제거)
.\build.ps1 -Clean

# 상세 로그 출력
.\build.ps1 -Verbose

# Debug 빌드
.\build.ps1 -BuildType Debug
```

**출력 예시:**
```
======================================================
3D PLY Viewer - Build Script (Improved)
======================================================

📁 Project:  C:\Dev\cpp-test\3d-viewer
📦 Build:    C:\Dev\cpp-test\3d-viewer\build
🔧 Type:     Release

[1/5] 전제 조건 확인...
  ✓ vcpkg 툴체인 OK
  ✓ CMake 3.30.5 OK

[2/5] 프로세스 정리...
  ✓ 실행 중인 프로세스 없음

[3/5] 빌드 디렉토리 준비...
  ✓ 빌드 디렉토리 준비 완료

[4/5] CMake 구성...
  ✓ CMake 구성 완료

[5/5] 프로젝트 빌드...
  ✓ 빌드 완료 (3.2초)

======================================================
빌드 결과
======================================================
✓ 빌드 성공!
  📍 위치:   C:\Dev\cpp-test\3d-viewer\build\src\Release\3d-viewer.exe
  📦 크기:   200.5 KB
  ⏱ 시간:   2025-12-17 18:30:00

실행하려면: .\run.ps1
```

---

### 2.2 run.ps1 (현재 상태)

**기능:**
- 빌드된 exe 위치 확인
- 실행 파일 존재 검증
- 콘솔 창과 함께 애플리케이션 실행

**사용 방법:**
```powershell
# 기본 실행
.\run.ps1

# Debug 빌드 실행
.\run.ps1 -BuildType Debug
```

**개선 제안:**
- DLL 의존성 검증 추가
- 콘솔 윈도우 크기 설정
- 오류 로그 캡처

---

### 2.3 clean.ps1 (현재 상태)

**기능:**
- build/ 디렉토리 삭제
- CMake 캐시 제거
- 중간 파일 정리

**사용 방법:**
```powershell
# 기본 정리
.\clean.ps1

# 완전 정리 (vcpkg 빌드 결과도 제거)
.\clean.ps1 -All
```

---

### 2.4 rebuild.ps1 (현재 상태)

**기능:**
- clean.ps1 → build.ps1 자동 순차 실행

**사용 방법:**
```powershell
# 깨끗한 재빌드
.\rebuild.ps1
```

---

### 2.5 setup.ps1 (초기 설정)

**기능:**
- vcpkg 설치
- 부트스트랩
- 의존성 설치

**사용 방법:**
```powershell
# 초기 환경 설정
.\setup.ps1
```

---

## 3. 권장 워크플로우

### 첫 빌드

```powershell
# 1단계: 초기 환경 설정
.\setup.ps1

# 2단계: 빌드
.\build.ps1

# 3단계: 실행
.\run.ps1
```

### 반복 개발

```powershell
# 코드 수정 후 빌드
.\build.ps1

# 실행해서 테스트
.\run.ps1
```

### 깨끗한 빌드

```powershell
# 옵션 1: build.ps1의 -Clean 플래그 사용
.\build.ps1 -Clean

# 옵션 2: rebuild.ps1 사용
.\rebuild.ps1
```

### 전체 정리

```powershell
# 모든 빌드 결과 제거
.\clean.ps1 -All

# 새로 빌드
.\build.ps1
```

---

## 4. 오류 해결 가이드

### 문제: "vcpkg 툴체인을 찾을 수 없습니다"

**원인:**
- setup.ps1을 실행하지 않음
- vcpkg이 제대로 설치되지 않음

**해결:**
```powershell
.\setup.ps1
```

### 문제: "CMake를 찾을 수 없습니다"

**원인:**
- CMake가 설치되지 않음
- PATH에 등록되지 않음

**해결:**
1. CMake 설치: https://cmake.org/download/
2. PATH 재설정 후 PowerShell 재시작

### 문제: "실행 중인 프로세스 때문에 exe를 열 수 없습니다"

**원인:**
- 이전 애플리케이션이 여전히 메모리에 있음
- build.ps1이 프로세스 종료 실패

**해결:**
```powershell
# 수동으로 프로세스 종료
Stop-Process -Name 3d-viewer -Force

# 다시 빌드
.\build.ps1
```

### 문제: "빌드 실패"

**해결 단계:**
1. 상세 로그 확인:
   ```powershell
   .\build.ps1 -Verbose
   ```

2. 깨끗한 빌드 시도:
   ```powershell
   .\build.ps1 -Clean
   ```

3. 소스 코드 오류 확인 및 수정

---

## 5. 환경 변수 설정 (선택사항)

PowerShell 프로필에 다음을 추가하여 항상 빌드 스크립트를 실행 가능하게 설정:

```powershell
# $PROFILE 편집
notepad $PROFILE

# 다음 줄 추가:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 프로필 저장 후 PowerShell 재시작
```

---

## 6. 빌드 스크립트 사용 팁

### Tip 1: 빠른 빌드 반복

```powershell
# 두 개 명령 연달아 실행
.\build.ps1; .\run.ps1
```

### Tip 2: 빌드 로그 저장

```powershell
# 로그를 파일로 저장
.\build.ps1 -Verbose | Tee-Object -FilePath build.log
```

### Tip 3: 배치 모드 빌드

```powershell
# 여러 설정으로 빌드
"Release", "Debug" | ForEach-Object {
    .\build.ps1 -BuildType $_
}
```

### Tip 4: 초기화 후 빌드

```powershell
# 한 줄로 완전 초기화 및 빌드
.\clean.ps1; .\setup.ps1; .\build.ps1; .\run.ps1
```

---

## 7. 향후 개선 계획

### 단기 (1주)
- [ ] GitHub Actions 워크플로우 추가
- [ ] 자동 테스트 스크립트
- [ ] 빌드 시간 기록 및 비교

### 중기 (1개월)
- [ ] CI/CD 파이프라인 구축
- [ ] Docker 컨테이너 빌드
- [ ] 멀티 플랫폼 지원 (Linux, macOS)

### 장기 (3개월)
- [ ] vcpkg 버전 고정 (reproducible build)
- [ ] 자동 성능 벤치마크
- [ ] 배포 패키징 자동화

---

## 8. 참고 자료

### 관련 문서
- `BUILD_ISSUES_AND_SOLUTIONS.md` - 빌드 문제 및 해결 방안
- `CMakeLists.txt` - CMake 설정
- `vcpkg.json` - 의존성 매니페스트

### 유용한 명령어

```powershell
# PowerShell 프로필 확인
$PROFILE

# 실행 정책 확인
Get-ExecutionPolicy

# vcpkg 패키지 검색
.\3rdparty\vcpkg\vcpkg.exe search wxwidgets

# 빌드 디렉토리 정리
Remove-Item -Path build -Recurse -Force

# CMake 버전 확인
cmake --version
```

---

## 결론

개선된 PowerShell 스크립트를 사용하면:
- ✅ 빌드 프로세스가 자동화됨
- ✅ 오류 처리가 개선됨
- ✅ 성능 측정 가능
- ✅ 사용자 친화적 인터페이스

**빌드 전에 항상 다음을 확인하세요:**
1. PowerShell 실행 정책 설정
2. 의존성 설치 여부 (setup.ps1 실행)
3. 충돌하는 프로세스 종료


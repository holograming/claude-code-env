# Common dependencies management
# Place this file in cmake/ folder and include it from root CMakeLists.txt

include(FetchContent)

# ==============================================================================
# Strategy 1: FetchContent (소스에서 다운로드)
# 장점: 최신 버전 자동 획득, 크로스 플랫폼 일관성
# 단점: 빌드 시간 증가, 네트워크 의존성
# ==============================================================================

# FetchContent_Declare(fmt
#     GIT_REPOSITORY https://github.com/fmtlib/fmt.git
#     GIT_TAG 9.1.0
# )

# FetchContent_Declare(spdlog
#     GIT_REPOSITORY https://github.com/gabime/spdlog.git
#     GIT_TAG v1.11.0
# )

# FetchContent_MakeAvailable(fmt spdlog)

# ==============================================================================
# Strategy 2: find_package (시스템 설치 참조)
# 장점: 빠른 빌드, 시스템 패키지 재사용
# 단점: 플랫폼별 설치 필요
# ==============================================================================

# find_package(fmt REQUIRED)
# find_package(spdlog REQUIRED)

# ==============================================================================
# Strategy 3: vcpkg 통합 (자동으로 처리됨)
# CMake toolchain에서 VCPKG_ROOT 설정 필요
# ==============================================================================

# ==============================================================================
# 모든 타겟이 사용할 공통 함수
# ==============================================================================

function(link_common_dependencies target)
    # 아래 주석 해제 후 실제 의존성 추가
    # target_link_libraries(${target} PRIVATE fmt::fmt spdlog::spdlog)
endfunction()

# 사용 예제:
# add_executable(myapp main.cpp)
# link_common_dependencies(myapp)

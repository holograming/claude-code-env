# Compiler warnings setup
# Place this file in cmake/ folder and include it from root CMakeLists.txt

function(target_set_warnings target)
    """
    Apply comprehensive compiler warnings to a target.

    Usage: target_set_warnings(myapp)
    """

    target_compile_options(${target} PRIVATE
        # MSVC 특화 옵션
        $<$<CXX_COMPILER_ID:MSVC>:
            /W4                    # 경고 레벨 4 (최대)
            /permissive-           # 엄격한 표준 준수
            /WX                    # 경고를 오류로 (선택: /WX 제거하면 경고만)
        >

        # GCC 및 Clang 공통
        $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:
            -Wall                  # 일반적인 경고
            -Wextra                # 추가 경고
            -Wpedantic             # 엄격한 표준 준수
            -Wconversion           # 타입 변환 경고
            -Wsign-conversion      # 부호 변환 경고
            -Wnull-dereference     # NULL 역참조 경고
            -Wnon-virtual-dtor     # 가상 소멸자 부재 경고
            -Woverloaded-virtual   # 오버로드된 가상 함수
        >

        # Clang 추가
        $<$<CXX_COMPILER_ID:Clang>:
            -Wmost
            -fcolor-diagnostics
        >
    )
endfunction()

# 사용 예제:
# add_executable(myapp main.cpp)
# target_set_warnings(myapp)

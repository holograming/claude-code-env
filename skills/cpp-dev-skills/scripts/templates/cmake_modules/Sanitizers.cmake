# Sanitizer options
# Place this file in cmake/ folder and include it from root CMakeLists.txt

option(ENABLE_ASAN "Enable AddressSanitizer (memory errors)" OFF)
option(ENABLE_TSAN "Enable ThreadSanitizer (data races)" OFF)
option(ENABLE_UBSAN "Enable UndefinedBehaviorSanitizer" OFF)
option(ENABLE_ALL_SANITIZERS "Enable all sanitizers" OFF)

function(enable_sanitizers target)
    """
    Apply sanitizers to a target.

    Requires GCC or Clang (not supported on MSVC).
    Usage: enable_sanitizers(myapp)
    """

    if(MSVC)
        message(WARNING "Sanitizers are not fully supported on MSVC")
        return()
    endif()

    # All sanitizers mode
    if(ENABLE_ALL_SANITIZERS)
        target_compile_options(${target} PRIVATE -fsanitize=address,undefined,thread)
        target_link_options(${target} PRIVATE -fsanitize=address,undefined,thread)
        return()
    endif()

    # AddressSanitizer
    if(ENABLE_ASAN)
        message(STATUS "Enabling AddressSanitizer for ${target}")
        target_compile_options(${target} PRIVATE -fsanitize=address -g)
        target_link_options(${target} PRIVATE -fsanitize=address)
    endif()

    # ThreadSanitizer
    if(ENABLE_TSAN)
        message(STATUS "Enabling ThreadSanitizer for ${target}")
        target_compile_options(${target} PRIVATE -fsanitize=thread -g)
        target_link_options(${target} PRIVATE -fsanitize=thread)
    endif()

    # UndefinedBehaviorSanitizer
    if(ENABLE_UBSAN)
        message(STATUS "Enabling UndefinedBehaviorSanitizer for ${target}")
        target_compile_options(${target} PRIVATE -fsanitize=undefined -g)
        target_link_options(${target} PRIVATE -fsanitize=undefined)
    endif()
endfunction()

# 사용 예제 1: 명령줄에서 활성화
# cmake -B build -DENABLE_ASAN=ON
# ./build/myapp

# 사용 예제 2: CMakeLists.txt에서
# add_executable(myapp main.cpp)
# enable_sanitizers(myapp)

# 주요 환경 변수:
# ASAN_OPTIONS=detect_leaks=1:verbosity=2:halt_on_error=1
# LSAN_OPTIONS=verbosity=2:log_threads=1
# TSAN_OPTIONS=verbosity=2:halt_on_error=1
# UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1

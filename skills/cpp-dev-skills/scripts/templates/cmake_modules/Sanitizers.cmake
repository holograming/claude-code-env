# Sanitizer Configuration
# Place this file in cmake/ folder and include it from root CMakeLists.txt
# IMPORTANT: ASAN and TSAN are mutually exclusive and cannot be used together

option(ENABLE_ASAN "Enable AddressSanitizer (memory errors)" OFF)
option(ENABLE_TSAN "Enable ThreadSanitizer (data races)" OFF)
option(ENABLE_UBSAN "Enable UndefinedBehaviorSanitizer" OFF)

function(enable_sanitizers target)
    """
    Apply sanitizers to a target.

    Requires GCC or Clang (not supported on MSVC).
    CRITICAL: ASAN and TSAN are mutually exclusive (cannot use together)

    Usage: enable_sanitizers(myapp)

    Compatible combinations:
    ✅ ASAN + UBSAN (memory bugs + undefined behavior)
    ✅ TSAN + UBSAN (threading bugs + undefined behavior)
    ❌ ASAN + TSAN (mutually exclusive - will fail)
    """

    if(MSVC)
        message(WARNING "Sanitizers are not fully supported on MSVC")
        return()
    endif()

    # CRITICAL: Prevent ASAN + TSAN mutual exclusion
    if(ENABLE_ASAN AND ENABLE_TSAN)
        message(FATAL_ERROR "ASAN and TSAN are mutually exclusive and cannot be enabled together.\n"
            "Choose ONE of:\n"
            "  • Memory bugs: cmake -B build -DENABLE_ASAN=ON -DENABLE_UBSAN=ON\n"
            "  • Threading bugs: cmake -B build -DENABLE_TSAN=ON -DENABLE_UBSAN=ON"
        )
    endif()

    # AddressSanitizer (memory errors: buffer overflow, use-after-free, leaks)
    if(ENABLE_ASAN)
        message(STATUS "Enabling AddressSanitizer for ${target}")
        target_compile_options(${target} PRIVATE -fsanitize=address -g -fno-omit-frame-pointer)
        target_link_options(${target} PRIVATE -fsanitize=address)
    endif()

    # ThreadSanitizer (data races, deadlocks)
    if(ENABLE_TSAN)
        message(STATUS "Enabling ThreadSanitizer for ${target}")
        target_compile_options(${target} PRIVATE -fsanitize=thread -g -fno-omit-frame-pointer)
        target_link_options(${target} PRIVATE -fsanitize=thread)
    endif()

    # UndefinedBehaviorSanitizer (undefined behavior)
    if(ENABLE_UBSAN)
        message(STATUS "Enabling UndefinedBehaviorSanitizer for ${target}")
        target_compile_options(${target} PRIVATE -fsanitize=undefined -g)
        target_link_options(${target} PRIVATE -fsanitize=undefined)
    endif()
endfunction()

# Usage examples:
# cmake -B build -DENABLE_ASAN=ON
# cmake -B build -DENABLE_ASAN=ON -DENABLE_UBSAN=ON (recommended for memory checking)
# cmake -B build -DENABLE_TSAN=ON -DENABLE_UBSAN=ON (recommended for threading checking)

# Environment variables:
# ASAN_OPTIONS=detect_leaks=1:verbosity=2:halt_on_error=1
# TSAN_OPTIONS=verbosity=2:halt_on_error=1
# UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1

cmake_minimum_required(VERSION 3.15)
project(MyAppWithDeps VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Find system packages
find_package(Threads REQUIRED)

# Optional: Uncomment to fetch dependencies from source
# include(FetchContent)
#
# FetchContent_Declare(
#     fmt
#     GIT_REPOSITORY https://github.com/fmtlib/fmt.git
#     GIT_TAG 9.1.0
# )
#
# FetchContent_MakeAvailable(fmt)

# Create executable
add_executable(${PROJECT_NAME} src/main.cpp)

# Link dependencies
target_link_libraries(${PROJECT_NAME}
    PRIVATE
        Threads::Threads
        # fmt::fmt
)

target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)

target_compile_options(${PROJECT_NAME} PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:/W4>
    $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall -Wextra -Wpedantic>
)

# Enable testing
enable_testing()
add_test(NAME main COMMAND ${PROJECT_NAME})

cmake_minimum_required(VERSION 3.15)
project(MyLibrary VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Create library
add_library(${PROJECT_NAME}
    src/mylib.cpp
    src/internal.cpp
)

# Create alias for consistency
add_library(MyLibrary::${PROJECT_NAME} ALIAS ${PROJECT_NAME})

# Set target properties
target_include_directories(${PROJECT_NAME}
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# C++ standard visible to consumers
target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_17)

# Compiler options (private to implementation)
target_compile_options(${PROJECT_NAME} PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:/W4>
    $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall -Wextra -Wpedantic>
)

# Enable position-independent code (recommended for shared libraries)
set_target_properties(${PROJECT_NAME} PROPERTIES
    POSITION_INDEPENDENT_CODE ON
)

# Install rules
install(TARGETS ${PROJECT_NAME}
    EXPORT ${PROJECT_NAME}Targets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    INCLUDES DESTINATION include
)

install(DIRECTORY include/ DESTINATION include)

install(EXPORT ${PROJECT_NAME}Targets
    FILE ${PROJECT_NAME}Targets.cmake
    NAMESPACE MyLibrary::
    DESTINATION lib/cmake/${PROJECT_NAME}
)

# Optional: Config package for find_package support
# See documentation/packaging section for complete example

# Create executable for testing the library
add_executable(demo src/demo.cpp)
target_link_libraries(demo PRIVATE ${PROJECT_NAME})

# Enable testing
enable_testing()
add_test(NAME demo COMMAND demo)

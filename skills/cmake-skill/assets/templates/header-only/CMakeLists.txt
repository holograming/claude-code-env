cmake_minimum_required(VERSION 3.15)
project(MyHeaderLib VERSION 1.0.0 LANGUAGES CXX)

# Header-only library uses INTERFACE
add_library(${PROJECT_NAME} INTERFACE)
add_library(MyHeaderLib::${PROJECT_NAME} ALIAS ${PROJECT_NAME})

# Interface - only header directories (no implementation)
target_include_directories(${PROJECT_NAME} INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# C++ standard requirement visible to consumers
target_compile_features(${PROJECT_NAME} INTERFACE cxx_std_17)

# Optional: Link other dependencies that consumers need
# target_link_libraries(${PROJECT_NAME} INTERFACE SomeDependency::target)

# Installation rules (optional)
install(TARGETS ${PROJECT_NAME}
    EXPORT ${PROJECT_NAME}Targets
)

install(DIRECTORY include/ DESTINATION include)

# For header-only libraries, no compilation is needed
enable_testing()
add_test(NAME dummy COMMAND ${CMAKE_COMMAND} -E echo "Header-only library configured successfully")

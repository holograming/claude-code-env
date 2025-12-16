### Basic CMakeLists.txt
```
cmake_minimum_required(VERSION 3.15)
project(MyProject)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add executable
add_executable(my_program main.cpp utils.cpp)

# Add library
add_library(my_library STATIC src/lib.cpp)

# Link libraries
target_link_libraries(my_program PRIVATE my_library)

# Include directories
target_include_directories(my_library PUBLIC include)
```
### Building with CMake
```
# Create build directory
mkdir build && cd build

# Configure (generates Makefiles)
cmake ..

# Build
cmake --build . --config Release

# Install
cmake --install . --prefix /usr/local

# Clean
cmake --build . --target clean
```
### Multi-Target Project
```
cmake_minimum_required(VERSION 3.15)
project(GameEngine)

# Core library
add_library(game_core src/core.cpp)
target_include_directories(game_core PUBLIC include)

# Engine library
add_library(game_engine src/engine.cpp)
target_link_libraries(game_engine PUBLIC game_core)

# Executable
add_executable(game_app main.cpp)
target_link_libraries(game_app PRIVATE game_engine)

# Tests
enable_testing()
add_executable(test_game tests/test_game.cpp)
target_link_libraries(test_game PRIVATE game_engine)
add_test(NAME GameTests COMMAND test_game)
```

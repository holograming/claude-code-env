# Testing with Google Test

> 유저가 요구할 때만 필요에 따라서 작성됨을 원칙으로 한다.
> 프로젝트가 무거워지면 안되기 때문에, 테스트 툴을 필요로 하면 사용한다.

## Basic Test Setup

```cpp
#include <gtest/gtest.h>

// Simple test
TEST(CalculatorTest, Addition) {
    EXPECT_EQ(2 + 2, 4);
    EXPECT_EQ(1 + 1, 2);
}

// Test fixture
class CalculatorTest : public ::testing::Test {
protected:
    Calculator calc;
    void SetUp() override { /* setup code */ }
    void TearDown() override { /* cleanup code */ }
};

TEST_F(CalculatorTest, Subtraction) {
    EXPECT_EQ(calc.subtract(5, 3), 2);
}

// Parametrized test
class AdditionTest : public ::testing::TestWithParam<int> {};

TEST_P(AdditionTest, MultipleValues) {
    EXPECT_GT(GetParam() + 1, GetParam());
}

INSTANTIATE_TEST_SUITE_P(
    AdditionTests,
    AdditionTest,
    ::testing::Values(0, 1, -1, 100)
);

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
```

## Assertion Types

```cpp
// Equality
EXPECT_EQ(a, b);   // a == b
EXPECT_NE(a, b);   // a != b
EXPECT_LT(a, b);   // a < b
EXPECT_LE(a, b);   // a <= b
EXPECT_GT(a, b);   // a > b
EXPECT_GE(a, b);   // a >= b

// Boolean
EXPECT_TRUE(condition);
EXPECT_FALSE(condition);

// String
EXPECT_STREQ("hello", "hello");
EXPECT_STRNE("a", "b");

// Exception
EXPECT_THROW(expression, exception_type);
EXPECT_NO_THROW(expression);

// EXPECT vs ASSERT
// EXPECT_* continues after failure
// ASSERT_* stops test after failure
```

## CMake Integration

```cmake
include(FetchContent)
FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG v1.14.0
)
FetchContent_MakeAvailable(googletest)

enable_testing()

add_executable(my_tests tests/test_main.cpp)
target_link_libraries(my_tests PRIVATE GTest::gtest_main)

include(GoogleTest)
gtest_discover_tests(my_tests)
```

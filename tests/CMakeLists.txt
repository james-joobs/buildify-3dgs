# Tests for Buildify3DGS
include(FetchContent)

# Fetch GoogleTest
FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG v1.14.0
)
FetchContent_MakeAvailable(googletest)

# Enable testing
enable_testing()

# Add test executable
add_executable(buildify_tests
    test_main.cpp
)

# Link with GoogleTest and main library
target_link_libraries(buildify_tests
    gtest
    gtest_main
    buildify
)

# Register tests with CTest
include(GoogleTest)
gtest_discover_tests(buildify_tests)
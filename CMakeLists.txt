cmake_minimum_required(VERSION 3.20)
project(Buildify3DGS VERSION 1.0.0 LANGUAGES CXX)

# Set C++23 standard
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Export compile commands for better IDE support
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Build type configuration
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
    set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

# Set output directories
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# Options
option(BUILD_SHARED_LIBS "Build shared libraries" ON)
option(BUILD_TESTS "Build tests" ON)
option(BUILD_EXAMPLES "Build examples" ON)
option(WITH_BLENDER "Build with Blender support" ON)
option(WITH_PYTHON "Build with Python bindings" ON)
option(WITH_PYTORCH "Build with PyTorch support" ON)

# Find packages
find_package(Threads REQUIRED)

# Python and pybind11 setup
if(WITH_PYTHON)
    find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
    
    # Use pybind11 for Python bindings
    include(FetchContent)
    FetchContent_Declare(
        pybind11
        GIT_REPOSITORY https://github.com/pybind/pybind11.git
        GIT_TAG v2.11.1
    )
    FetchContent_MakeAvailable(pybind11)
endif()

# Blender setup
if(WITH_BLENDER)
    # Blender typically requires these libraries
    find_package(OpenGL REQUIRED)
    find_package(GLEW)
    find_package(OpenImageIO)
    find_package(OpenColorIO)
    find_package(OpenSubdiv)
    find_package(Alembic)
    
    # Set Blender include directories (adjust path as needed)
    if(DEFINED ENV{BLENDER_HOME})
        set(BLENDER_INCLUDE_DIR $ENV{BLENDER_HOME}/include)
        set(BLENDER_LIB_DIR $ENV{BLENDER_HOME}/lib)
    else()
        message(WARNING "BLENDER_HOME environment variable not set. Blender support may be limited.")
    endif()
endif()

# PyTorch setup
if(WITH_PYTORCH)
    # Find PyTorch using Python
    execute_process(
        COMMAND ${Python3_EXECUTABLE} -c "import torch; print(torch.utils.cmake_prefix_path)"
        OUTPUT_VARIABLE TORCH_CMAKE_PREFIX_PATH
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
    )
    
    if(TORCH_CMAKE_PREFIX_PATH)
        list(APPEND CMAKE_PREFIX_PATH ${TORCH_CMAKE_PREFIX_PATH})
        find_package(Torch REQUIRED)
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")
    else()
        message(WARNING "PyTorch not found. PyTorch support will be disabled.")
        set(WITH_PYTORCH OFF)
    endif()
endif()

# Compiler-specific settings
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(
        -Wall
        -Wextra
        -Wpedantic
        -Wno-unused-parameter
        -Wno-unused-variable
        $<$<CONFIG:Debug>:-g3>
        $<$<CONFIG:Debug>:-O0>
        $<$<CONFIG:Release>:-O3>
        $<$<CONFIG:Release>:-march=native>
    )
elseif(MSVC)
    add_compile_options(
        /W4
        /permissive-
        /Zc:__cplusplus
        $<$<CONFIG:Debug>:/Od>
        $<$<CONFIG:Release>:/O2>
    )
endif()

# Include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# Add subdirectories
add_subdirectory(src)

if(WITH_PYTHON)
    add_subdirectory(python)
endif()

if(BUILD_EXAMPLES)
    add_subdirectory(examples)
endif()

if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

# Installation
include(GNUInstallDirs)

install(DIRECTORY include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

# Package configuration
include(CMakePackageConfigHelpers)

configure_package_config_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/Buildify3DGSConfig.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/Buildify3DGSConfig.cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Buildify3DGS
)

write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/Buildify3DGSConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY AnyNewerVersion
)

install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/Buildify3DGSConfig.cmake
    ${CMAKE_CURRENT_BINARY_DIR}/Buildify3DGSConfigVersion.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Buildify3DGS
)

# Summary
message(STATUS "")
message(STATUS "=== Configuration Summary ===")
message(STATUS "Build type:        ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ Standard:      ${CMAKE_CXX_STANDARD}")
message(STATUS "Blender support:   ${WITH_BLENDER}")
message(STATUS "Python bindings:   ${WITH_PYTHON}")
message(STATUS "PyTorch support:   ${WITH_PYTORCH}")
message(STATUS "Build tests:       ${BUILD_TESTS}")
message(STATUS "Build examples:    ${BUILD_EXAMPLES}")
message(STATUS "")
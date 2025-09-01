# Core library
set(BUILDIFY_SOURCES
    core/context.cpp
    core/engine.cpp
    core/renderer.cpp
    core/scene.cpp
    utils/math.cpp
    utils/logger.cpp
)

# Add conditional sources
if(WITH_BLENDER)
    list(APPEND BUILDIFY_SOURCES core/blender_integration.cpp)
endif()

if(WITH_PYTORCH AND TORCH_FOUND)
    list(APPEND BUILDIFY_SOURCES core/pytorch_integration.cpp)
endif()

set(BUILDIFY_HEADERS
    ${CMAKE_SOURCE_DIR}/include/buildify/buildify.h
    ${CMAKE_SOURCE_DIR}/include/buildify/blender_integration.h
    ${CMAKE_SOURCE_DIR}/include/buildify/pytorch_integration.h
)

# Create the main library
add_library(buildify ${BUILDIFY_SOURCES})

target_include_directories(buildify
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
)

# Link libraries
target_link_libraries(buildify
    PUBLIC
        Threads::Threads
)

# Blender integration
if(WITH_BLENDER AND BLENDER_INCLUDE_DIR)
    target_include_directories(buildify PRIVATE ${BLENDER_INCLUDE_DIR})
    target_compile_definitions(buildify PRIVATE WITH_BLENDER=1)
    
    if(OpenGL_FOUND)
        target_link_libraries(buildify PUBLIC OpenGL::GL)
    endif()
endif()

# PyTorch integration
if(WITH_PYTORCH AND TORCH_FOUND)
    target_link_libraries(buildify PUBLIC ${TORCH_LIBRARIES})
    target_compile_definitions(buildify PRIVATE WITH_PYTORCH=1)
endif()

# Set properties
set_target_properties(buildify PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION ${PROJECT_VERSION_MAJOR}
    CXX_STANDARD 23
    CXX_STANDARD_REQUIRED ON
    POSITION_INDEPENDENT_CODE ON
)

# Installation
install(TARGETS buildify
    EXPORT Buildify3DGSTargets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

install(FILES ${BUILDIFY_HEADERS}
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/buildify
)

install(EXPORT Buildify3DGSTargets
    FILE Buildify3DGSTargets.cmake
    NAMESPACE Buildify3DGS::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Buildify3DGS
)
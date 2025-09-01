# Example applications

# Basic example
add_executable(basic_example basic_example.cpp)
target_link_libraries(basic_example PRIVATE buildify)
set_target_properties(basic_example PROPERTIES
    CXX_STANDARD 23
    CXX_STANDARD_REQUIRED ON
)

# Blender integration example
if(WITH_BLENDER)
    add_executable(blender_example blender_example.cpp)
    target_link_libraries(blender_example PRIVATE buildify)
    set_target_properties(blender_example PROPERTIES
        CXX_STANDARD 23
        CXX_STANDARD_REQUIRED ON
    )
endif()

# PyTorch integration example
if(WITH_PYTORCH)
    add_executable(pytorch_example pytorch_example.cpp)
    target_link_libraries(pytorch_example PRIVATE buildify ${TORCH_LIBRARIES})
    set_target_properties(pytorch_example PROPERTIES
        CXX_STANDARD 23
        CXX_STANDARD_REQUIRED ON
        CXX_VISIBILITY_PRESET hidden
    )
endif()
# Python bindings
if(NOT WITH_PYTHON)
    return()
endif()

# Create Python module
pybind11_add_module(pybuildify
    bindings.cpp
)

target_link_libraries(pybuildify
    PRIVATE
        buildify
)

# Set properties
set_target_properties(pybuildify PROPERTIES
    CXX_STANDARD 23
    CXX_STANDARD_REQUIRED ON
)

# Installation
install(TARGETS pybuildify
    LIBRARY DESTINATION ${Python3_SITELIB}/buildify
)
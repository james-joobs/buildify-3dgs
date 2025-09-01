#!/bin/bash
set -e

echo "Building Buildify 3DGS..."

# Create build directory
mkdir -p build
cd build

# Configure with CMake
echo "Configuring CMake..."
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DWITH_PYTHON=OFF \
    -DWITH_PYTORCH=OFF \
    -DWITH_BLENDER=OFF \
    -DBUILD_EXAMPLES=OFF \
    -DBUILD_TESTS=ON

# Build
echo "Building..."
cmake --build . --parallel

echo "Build complete!"
echo "To install Python bindings, run: pip install -e ."
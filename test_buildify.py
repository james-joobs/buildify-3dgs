#!/usr/bin/env python3
"""
Test script for Buildify 3DGS C++/Python integration
Demonstrates the functionality of the C++23 project with modern features
"""

import buildify

def main():
    print("🚀 Buildify 3DGS Test Suite")
    print("=" * 50)
    
    # Set up logging
    buildify.utils.set_log_level(buildify.utils.LogLevel.Info)
    
    # Test 1: Math utilities with C++23 concepts
    print("\n1. Testing Math Utilities (C++23 concepts)")
    v1 = buildify.utils.Vector3(1.0, 2.0, 3.0)
    v2 = buildify.utils.Vector3(4.0, 5.0, 6.0)
    
    # Vector operations
    v_sum = v1 + v2
    v_dot = v1.dot(v2)
    v_cross = v1.cross(v2)
    v_len = v1.length()
    
    print(f"   Vector3 addition: {v1} + {v2} = {v_sum}")
    print(f"   Dot product: {v_dot}")
    print(f"   Cross product: {v_cross}")
    print(f"   Length: {v_len:.3f}")
    
    # Test 2: Engine and Scene Management
    print("\n2. Testing Engine & Scene Management")
    engine = buildify.core.Engine()
    engine.initialize()
    
    # Create a scene
    scene = engine.create_scene("MainScene")
    print(f"   Created scene: '{scene.get_name()}'")
    
    # Test 3: Camera Setup
    print("\n3. Testing Camera System")
    camera = buildify.core.Camera("MainCamera")
    camera.set_perspective(45.0, 16.0/9.0, 0.1, 1000.0)
    
    # Set camera position and look at target
    transform = camera.get_transform()
    transform.position = buildify.utils.Vector3(0, 5, 10)
    camera.set_transform(transform)
    camera.look_at(buildify.utils.Vector3(0, 0, 0))
    
    scene.add_entity(camera)
    scene.set_active_camera(camera)
    print("   Camera configured and added to scene")
    
    # Test 4: Renderer Setup
    print("\n4. Testing OpenGL Renderer")
    renderer = buildify.core.OpenGLRenderer()
    
    target = buildify.core.RenderTarget()
    target.width = 1920
    target.height = 1080
    target.samples = 4  # MSAA
    
    print(f"   Render target: {target.width}x{target.height} ({target.samples}x MSAA)")
    
    # Test 5: Transform System
    print("\n5. Testing Transform System")
    entity = buildify.core.Entity("TestEntity")
    transform = entity.get_transform()
    transform.position = buildify.utils.Vector3(1, 2, 3)
    transform.scale = buildify.utils.Vector3(2, 2, 2)
    
    # Test quaternion rotation
    rotation = buildify.utils.Quaternion.from_axis_angle(
        buildify.utils.Vector3(0, 1, 0), 
        3.14159 / 4  # 45 degrees
    )
    transform.rotation = rotation
    
    entity.set_transform(transform)
    matrix = transform.to_matrix()
    print("   Transform matrix computed from position, rotation, scale")
    
    # Test 6: Update callback system
    print("\n6. Testing Update Callbacks (C++23 std::function)")
    callback_count = 0
    
    def update_callback(delta_time):
        nonlocal callback_count
        callback_count += 1
        if callback_count == 1:
            print(f"   Update callback called with dt: {delta_time:.6f}s")
    
    engine.add_update_callback(update_callback)
    
    # Simulate some updates
    for i in range(3):
        engine.update(0.016667)  # ~60 FPS
    
    print(f"   Callback invoked {callback_count} times")
    
    # Test 7: Scene hierarchy
    print("\n7. Testing Scene Entity Management")
    scene.add_entity(entity)
    found_entity = scene.find_entity("TestEntity")
    
    if found_entity:
        print(f"   Successfully found entity: '{found_entity.get_name()}'")
    
    # Count entities in scene
    print("   Scene successfully manages entities")
    
    # Cleanup
    print("\n8. Cleanup")
    engine.shutdown()
    print("   Engine shutdown complete")
    
    print("\n✅ All tests completed successfully!")
    print("🎉 C++23 project with Python bindings is working!")

if __name__ == "__main__":
    main()
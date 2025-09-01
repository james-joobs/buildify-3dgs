#!/usr/bin/env python3
"""
대화형 Buildify 데모
C++23 기능들을 Python에서 실시간으로 테스트해볼 수 있습니다.
"""

import buildify
import time

def demo_math_operations():
    """수학 연산 데모"""
    print("🧮 Math Operations Demo")
    print("-" * 30)
    
    # 벡터 생성
    v1 = buildify.utils.Vector3(1, 2, 3)
    v2 = buildify.utils.Vector3(4, 5, 6)
    
    print(f"벡터 1: {v1}")
    print(f"벡터 2: {v2}")
    print(f"덧셈: {v1 + v2}")
    print(f"내적: {v1.dot(v2)}")
    print(f"외적: {v1.cross(v2)}")
    print(f"길이: {v1.length():.3f}")
    print(f"정규화: {v1.normalized()}")
    
    # 쿼터니언 회전
    axis = buildify.utils.Vector3(0, 1, 0)  # Y축
    angle = 3.14159 / 4  # 45도
    rotation = buildify.utils.Quaternion.from_axis_angle(axis, angle)
    print(f"회전 쿼터니언: ({rotation.x:.3f}, {rotation.y:.3f}, {rotation.z:.3f}, {rotation.w:.3f})")
    
    # 변환 행렬
    transform = buildify.utils.Transform()
    transform.position = v1
    transform.rotation = rotation
    transform.scale = buildify.utils.Vector3(2, 2, 2)
    
    matrix = transform.to_matrix()
    print("변환 행렬 생성 완료")
    print()

def demo_scene_management():
    """씬 관리 데모"""
    print("🎬 Scene Management Demo")
    print("-" * 30)
    
    # 엔진 초기화
    engine = buildify.core.Engine()
    engine.initialize()
    print("✅ 엔진 초기화됨")
    
    # 씬 생성
    scene = engine.create_scene("DemoScene")
    print(f"✅ 씬 생성됨: '{scene.get_name()}'")
    
    # 카메라 설정
    camera = buildify.core.Camera("MainCamera")
    camera.set_perspective(45.0, 16.0/9.0, 0.1, 1000.0)
    
    # 카메라 위치 설정
    transform = camera.get_transform()
    transform.position = buildify.utils.Vector3(0, 5, 10)
    camera.set_transform(transform)
    
    scene.add_entity(camera)
    scene.set_active_camera(camera)
    print("✅ 카메라 설정 완료")
    
    # 엔티티 추가
    for i in range(3):
        entity = buildify.core.Entity(f"Entity_{i}")
        transform = entity.get_transform()
        transform.position = buildify.utils.Vector3(i * 2, 0, 0)
        entity.set_transform(transform)
        scene.add_entity(entity)
        print(f"✅ 엔티티 추가됨: '{entity.get_name()}'")
    
    # 엔티티 찾기
    found = scene.find_entity("Entity_1")
    if found:
        print(f"✅ 엔티티 검색 성공: '{found.get_name()}'")
    
    # 업데이트 콜백 추가
    update_count = 0
    def update_callback(dt):
        nonlocal update_count
        update_count += 1
        if update_count <= 3:
            print(f"🔄 업데이트 #{update_count}: dt={dt:.4f}s")
    
    engine.add_update_callback(update_callback)
    
    # 시뮬레이션 실행
    print("🏃 시뮬레이션 시작...")
    for i in range(5):
        engine.update(0.016667)  # 60 FPS
        time.sleep(0.1)
    
    engine.shutdown()
    print("✅ 엔진 종료됨")
    print()

def demo_renderer():
    """렌더러 데모"""
    print("🎨 Renderer Demo")
    print("-" * 30)
    
    # 렌더러 생성
    renderer = buildify.core.OpenGLRenderer()
    print("✅ OpenGL 렌더러 생성됨")
    
    # 렌더 타겟 설정
    target = buildify.core.RenderTarget()
    target.width = 1920
    target.height = 1080
    target.samples = 4  # MSAA
    
    print(f"✅ 렌더 타겟: {target.width}x{target.height} ({target.samples}x MSAA)")
    print("📝 참고: 실제 초기화는 OpenGL 컨텍스트가 필요합니다")
    print()

def interactive_menu():
    """대화형 메뉴"""
    while True:
        print("🎯 Buildify Interactive Demo")
        print("=" * 40)
        print("1. 수학 연산 데모")
        print("2. 씬 관리 데모")
        print("3. 렌더러 데모")
        print("4. 전체 데모 실행")
        print("5. 시스템 정보")
        print("0. 종료")
        print()
        
        try:
            choice = input("선택하세요 (0-5): ").strip()
            
            if choice == "0":
                print("👋 데모를 종료합니다!")
                break
            elif choice == "1":
                demo_math_operations()
            elif choice == "2":
                demo_scene_management()
            elif choice == "3":
                demo_renderer()
            elif choice == "4":
                demo_math_operations()
                demo_scene_management()
                demo_renderer()
            elif choice == "5":
                print(f"📦 Buildify 버전: {buildify.__version__}")
                print(f"🔧 Core 모듈: {buildify.core}")
                print(f"🛠️ Utils 모듈: {buildify.utils}")
                print()
            else:
                print("❌ 잘못된 선택입니다.")
                
        except KeyboardInterrupt:
            print("\n👋 데모를 종료합니다!")
            break
        except Exception as e:
            print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    print("🚀 Buildify C++23 Interactive Demo")
    print("Python에서 C++ 기능을 실시간으로 테스트해보세요!\n")
    
    # 로그 레벨 설정
    buildify.utils.set_log_level(buildify.utils.LogLevel.Info)
    
    interactive_menu()
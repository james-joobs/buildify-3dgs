#!/usr/bin/env python3
"""
Buildify 성능 벤치마크
C++23 최적화된 코드의 성능을 측정합니다.
"""

import buildify
import time
import statistics

def benchmark_vector_operations(iterations=100000):
    """벡터 연산 성능 테스트"""
    print(f"🧮 벡터 연산 벤치마크 ({iterations:,}회 반복)")
    
    # 벡터 생성
    vectors = []
    start_time = time.time()
    
    for i in range(iterations):
        v = buildify.utils.Vector3(i, i+1, i+2)
        vectors.append(v)
    
    creation_time = time.time() - start_time
    
    # 벡터 연산
    start_time = time.time()
    results = []
    
    for i in range(len(vectors) - 1):
        v1 = vectors[i]
        v2 = vectors[i + 1]
        
        # 다양한 연산 수행
        sum_v = v1 + v2
        dot = v1.dot(v2)
        cross = v1.cross(v2)
        length = v1.length()
        
        results.append((sum_v, dot, cross, length))
    
    operation_time = time.time() - start_time
    
    print(f"  벡터 생성: {creation_time:.3f}초 ({iterations/creation_time:.0f} 벡터/초)")
    print(f"  벡터 연산: {operation_time:.3f}초 ({len(results)/operation_time:.0f} 연산/초)")
    print()

def benchmark_transform_matrix(iterations=50000):
    """변환 행렬 성능 테스트"""
    print(f"📐 변환 행렬 벤치마크 ({iterations:,}회 반복)")
    
    transforms = []
    
    # Transform 객체 생성
    start_time = time.time()
    
    for i in range(iterations):
        transform = buildify.utils.Transform()
        transform.position = buildify.utils.Vector3(i, i*2, i*3)
        transform.scale = buildify.utils.Vector3(1.5, 1.5, 1.5)
        
        # 회전 설정
        axis = buildify.utils.Vector3(0, 1, 0)
        angle = (i % 360) * 3.14159 / 180
        transform.rotation = buildify.utils.Quaternion.from_axis_angle(axis, angle)
        
        transforms.append(transform)
    
    setup_time = time.time() - start_time
    
    # 행렬 계산
    start_time = time.time()
    matrices = []
    
    for transform in transforms:
        matrix = transform.to_matrix()
        matrices.append(matrix)
    
    matrix_time = time.time() - start_time
    
    print(f"  Transform 설정: {setup_time:.3f}초 ({iterations/setup_time:.0f} 설정/초)")
    print(f"  행렬 계산: {matrix_time:.3f}초 ({iterations/matrix_time:.0f} 행렬/초)")
    print()

def benchmark_scene_management(num_entities=1000):
    """씬 관리 성능 테스트"""
    print(f"🎬 씬 관리 벤치마크 ({num_entities:,}개 엔티티)")
    
    # 엔진 초기화
    engine = buildify.core.Engine()
    engine.initialize()
    scene = engine.create_scene("BenchmarkScene")
    
    # 엔티티 생성 및 추가
    start_time = time.time()
    entities = []
    
    for i in range(num_entities):
        entity = buildify.core.Entity(f"Entity_{i}")
        
        # 변환 설정
        transform = entity.get_transform()
        transform.position = buildify.utils.Vector3(i % 100, (i // 100) % 100, i // 10000)
        entity.set_transform(transform)
        
        scene.add_entity(entity)
        entities.append(entity)
    
    creation_time = time.time() - start_time
    
    # 엔티티 검색 성능
    search_times = []
    search_names = [f"Entity_{i}" for i in range(0, num_entities, num_entities//10)]
    
    for name in search_names:
        start_time = time.time()
        found = scene.find_entity(name)
        search_time = time.time() - start_time
        search_times.append(search_time)
        
        if not found:
            print(f"  ❌ 엔티티 '{name}' 찾지 못함")
    
    # 씬 업데이트 성능
    start_time = time.time()
    for _ in range(10):  # 10프레임
        scene.update(0.016667)
    update_time = time.time() - start_time
    
    engine.shutdown()
    
    avg_search_time = statistics.mean(search_times) * 1000  # ms
    
    print(f"  엔티티 생성: {creation_time:.3f}초 ({num_entities/creation_time:.0f} 엔티티/초)")
    print(f"  엔티티 검색: {avg_search_time:.3f}ms (평균)")
    print(f"  씬 업데이트: {update_time:.3f}초 (10프레임)")
    print()

def benchmark_camera_operations(iterations=10000):
    """카메라 연산 성능 테스트"""
    print(f"📷 카메라 연산 벤치마크 ({iterations:,}회 반복)")
    
    camera = buildify.core.Camera("BenchmarkCamera")
    camera.set_perspective(45.0, 16.0/9.0, 0.1, 1000.0)
    
    # 카메라 변환 설정
    start_time = time.time()
    
    for i in range(iterations):
        transform = camera.get_transform()
        transform.position = buildify.utils.Vector3(i % 100, 10, (i // 100) % 100)
        camera.set_transform(transform)
    
    transform_time = time.time() - start_time
    
    # 행렬 계산
    start_time = time.time()
    
    for _ in range(iterations):
        view_matrix = camera.get_view_matrix()
        projection_matrix = camera.get_projection_matrix()
    
    matrix_time = time.time() - start_time
    
    print(f"  카메라 변환: {transform_time:.3f}초 ({iterations/transform_time:.0f} 변환/초)")
    print(f"  행렬 계산: {matrix_time:.3f}초 ({iterations/matrix_time:.0f} 행렬/초)")
    print()

def benchmark_memory_usage():
    """메모리 사용량 측정"""
    print("💾 메모리 사용량 체크")
    
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # 대량의 객체 생성
        objects = []
        for i in range(10000):
            engine = buildify.core.Engine()
            scene = engine.create_scene(f"Scene_{i}")
            entity = buildify.core.Entity(f"Entity_{i}")
            camera = buildify.core.Camera(f"Camera_{i}")
            objects.append((engine, scene, entity, camera))
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before
        
        print(f"  생성 전 메모리: {memory_before:.1f} MB")
        print(f"  생성 후 메모리: {memory_after:.1f} MB")
        print(f"  사용된 메모리: {memory_used:.1f} MB")
        print(f"  객체당 메모리: {memory_used/len(objects)*1024:.1f} KB")
        
        # 정리
        del objects
        
    except ImportError:
        print("  ⚠️  psutil 모듈이 없어 메모리 측정을 건너뜁니다")
        print("  설치: pip install psutil")
    
    print()

def main():
    print("🚀 Buildify C++23 Performance Benchmark")
    print("=" * 50)
    
    # 로그 레벨을 Warning으로 설정 (성능 측정 방해 방지)
    buildify.utils.set_log_level(buildify.utils.LogLevel.Warning)
    
    start_time = time.time()
    
    benchmark_vector_operations(100000)
    benchmark_transform_matrix(50000)
    benchmark_scene_management(1000)
    benchmark_camera_operations(10000)
    benchmark_memory_usage()
    
    total_time = time.time() - start_time
    
    print("📊 벤치마크 완료")
    print(f"⏱️  총 소요 시간: {total_time:.2f}초")
    print("\n🎯 성능 최적화 팁:")
    print("  • 벡터 연산: C++23 SIMD 최적화 활용")
    print("  • 메모리: RAII와 스마트 포인터로 안전한 관리")
    print("  • 병렬성: std::execution 정책 활용 가능")
    print("  • 컴파일: -O3 -march=native 플래그 사용")

if __name__ == "__main__":
    main()
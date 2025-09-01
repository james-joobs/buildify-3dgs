"""
Example usage script for COLMAP and 3D Gaussian Splatting integration in Blender

이 스크립트는 Blender에서 실행하여 COLMAP 데이터와 Gaussian Splats를 로드하는 예제입니다.
"""

import bpy
from pathlib import Path
from main import main

def run_example():
    """실제 데이터 경로로 예제 실행"""
    
    # =================================================================
    # 여기서 실제 데이터 경로를 설정하세요!
    # =================================================================
    
    # COLMAP 워크스페이스 경로 (sparse/0/ 폴더를 포함하는 디렉토리)
    COLMAP_PATH = "/tmp/nerfstudio_outputs/colmap_output"
    
    # Gaussian Splatting PLY 파일 경로
    PLY_PATH = "/tmp/nerfstudio_outputs/splatfacto/splat.ply"
    
    # 원본 이미지들이 있는 폴더 경로 (선택사항)
    IMAGES_PATH = "/tmp/video_frames"
    
    # =================================================================
    
    print("=== COLMAP + 3DGS Integration Example ===")
    print(f"COLMAP path: {COLMAP_PATH}")
    print(f"PLY path: {PLY_PATH}")  
    print(f"Images path: {IMAGES_PATH}")
    
    # 경로 검증
    colmap_path = Path(COLMAP_PATH)
    ply_path = Path(PLY_PATH)
    images_path = Path(IMAGES_PATH) if IMAGES_PATH else None
    
    if not colmap_path.exists():
        print(f"❌ COLMAP path not found: {colmap_path}")
        print("Please update COLMAP_PATH in this script")
        return False
        
    if not ply_path.exists():
        print(f"❌ PLY file not found: {ply_path}")
        print("Please update PLY_PATH in this script")
        return False
    
    if images_path and not images_path.exists():
        print(f"⚠️  Images path not found: {images_path}")
        print("Continuing without image planes...")
        images_path = None
    
    # 필수 COLMAP 파일들 확인
    sparse_path = colmap_path / "sparse" / "0"
    required_files = ["cameras.bin", "images.bin", "points3D.bin"]
    missing_files = []
    
    for file_name in required_files:
        file_path = sparse_path / file_name
        if not file_path.exists():
            missing_files.append(str(file_path))
    
    if missing_files:
        print("❌ Missing required COLMAP files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ All required files found!")
    
    # 통합 실행
    try:
        success = main(
            colmap_path=str(colmap_path),
            ply_path=str(ply_path), 
            images_path=str(images_path) if images_path else None,
            use_kiri=True  # KIRI 3DGS Engine 사용 (False로 설정하면 수동 임포트)
        )
        
        if success:
            print("\n🎉 Integration completed successfully!")
            print("\n📖 사용 방법:")
            print("   - SPACEBAR: 애니메이션 재생/정지")
            print("   - NUM0: 카메라 뷰")
            print("   - NUM7/NUM1/NUM3: 위/앞/옆면 뷰")
            print("   - 마우스 중간 버튼: 뷰 회전")
            
        return success
        
    except Exception as e:
        print(f"❌ Integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def quick_test():
    """빠른 테스트를 위한 함수 (더미 데이터 사용)"""
    print("=== Quick Test Mode ===")
    print("이 모드는 실제 데이터 없이 Blender 씬만 설정합니다.")
    
    # Blender 씬 클리어
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # 테스트용 카메라 생성
    bpy.ops.object.camera_add(location=(0, -5, 2))
    camera = bpy.context.active_object
    camera.name = "Test_Camera"
    
    # 간단한 애니메이션 추가
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 50
    
    for frame in range(1, 51):
        bpy.context.scene.frame_set(frame)
        # 원형 궤도로 카메라 이동
        import math
        angle = (frame - 1) * 2 * math.pi / 50
        camera.location = (5 * math.sin(angle), 5 * math.cos(angle), 2)
        camera.rotation_euler = (math.radians(60), 0, angle + math.radians(90))
        camera.keyframe_insert(data_path="location", frame=frame)
        camera.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    # 테스트용 오브젝트들 추가
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    bpy.ops.mesh.primitive_uv_sphere_add(location=(2, 0, 1))
    bpy.ops.mesh.primitive_cylinder_add(location=(-2, 0, 0.5))
    
    # 카메라를 활성 카메라로 설정
    bpy.context.scene.camera = camera
    
    print("✅ 테스트 씬이 생성되었습니다!")
    print("   - SPACEBAR로 애니메이션을 확인해보세요")


if __name__ == "__main__":
    print("Blender COLMAP + 3DGS Integration Example")
    print("=" * 50)
    
    # 실제 데이터로 실행하려면 이 주석을 해제하세요
    # run_example()
    
    # 빠른 테스트용 (실제 데이터 없이)
    quick_test()
    
    print("\n💡 실제 데이터를 사용하려면:")
    print("   1. 이 스크립트에서 경로들을 수정하세요")
    print("   2. run_example() 함수 호출 주석을 해제하세요")
    print("   3. quick_test() 함수 호출을 주석처리하세요")
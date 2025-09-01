#!/usr/bin/env python3
"""
Complete simulation script for Blender integration
실제 데이터로 완전한 시뮬레이션을 실행합니다
"""

# Blender에서 실행하기 위한 설정
try:
    import bpy
    BLENDER_MODE = True
    print("🎬 Running in Blender mode")
except ImportError:
    BLENDER_MODE = False
    print("🖥️  Running in standalone mode (simulation only)")

import sys
import os
from pathlib import Path

# 프로젝트 경로 추가
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from blender_colmap_3dgs.colmap_parser import COLMAPLoader
from blender_colmap_3dgs.gaussian_splatting import GaussianSplattingIntegration, load_ply_gaussian_splats
if BLENDER_MODE:
    from blender_colmap_3dgs.blender_animation import BlenderCOLMAPIntegration

def main():
    """메인 시뮬레이션 함수"""
    
    print("=== COLMAP + 3DGS Blender 통합 시뮬레이션 ===")
    
    # 실제 데이터 경로 설정
    colmap_path = "/home/hwoo-joo/github/hloc-nerfstudio/outputs/daewoo_drone_003_hloc_2/colmap"
    ply_path = "/home/hwoo-joo/github/hloc-nerfstudio/exports/splatfacto_daewoo_drone_003/daewoo_drone_003_hloc/splatfacto_daewoo_drone_003_splat.ply"
    
    # 이미지 경로 (추정)
    images_path = "/home/hwoo-joo/github/hloc-nerfstudio/outputs/daewoo_drone_003_hloc_2/colmap/sparse/0/images"
    
    print(f"📁 COLMAP path: {colmap_path}")
    print(f"📄 PLY path: {ply_path}")
    print(f"🖼️  Images path: {images_path}")
    
    try:
        # 1단계: COLMAP 데이터 로드
        print("\n1️⃣ COLMAP 데이터 로딩...")
        colmap_loader = COLMAPLoader(colmap_path)
        colmap_loader.load_reconstruction()
        
        if not colmap_loader.images:
            print("❌ COLMAP 이미지를 찾을 수 없습니다")
            return False
        
        # 카메라 포즈와 포인트 클라우드 가져오기
        camera_poses = colmap_loader.get_camera_poses_for_blender()
        colmap_points, colmap_colors = colmap_loader.get_point_cloud()
        
        print(f"   ✅ {len(camera_poses)}개 카메라 포즈")
        print(f"   ✅ {len(colmap_points)}개 3D 포인트")
        
        # 2단계: Gaussian Splats 로드
        print("\n2️⃣ Gaussian Splats 로딩...")
        splat_positions, splat_colors, splat_properties = load_ply_gaussian_splats(ply_path)
        print(f"   ✅ {len(splat_positions)}개 Gaussian Splats")
        
        if not BLENDER_MODE:
            print("\n⚠️  Blender가 없으므로 여기서 시뮬레이션 종료")
            print("✅ 모든 데이터가 성공적으로 로드되었습니다!")
            return True
        
        # 3단계: Blender 씬 설정
        print("\n3️⃣ Blender 씬 설정...")
        
        # 카메라 파라미터 설정
        camera_params = {}
        if colmap_loader.cameras:
            first_camera = list(colmap_loader.cameras.values())[0]
            camera_params = {
                'width': first_camera.width,
                'height': first_camera.height,
                'focal_length': first_camera.params[0] if len(first_camera.params) > 0 else None
            }
            print(f"   📷 카메라: {camera_params['width']}x{camera_params['height']}")
        
        # Blender 통합
        blender_integration = BlenderCOLMAPIntegration()
        blender_integration.setup_scene(
            poses=camera_poses,
            points=colmap_points,
            colors=colmap_colors,
            images_path=str(images_path) if Path(images_path).exists() else "",
            camera_params=camera_params,
            clear_existing=True
        )
        
        print(f"   ✅ 애니메이션 카메라 생성 ({len(camera_poses)} 프레임)")
        if len(colmap_points) > 0:
            print(f"   ✅ COLMAP 포인트 클라우드 ({len(colmap_points)} 포인트)")
        
        # 4단계: Gaussian Splats 통합
        print("\n4️⃣ Gaussian Splats 통합...")
        gs_integration = GaussianSplattingIntegration()
        
        # PLY 파일 로드 (KIRI 시도 후 수동 로드)
        if gs_integration.load_gaussian_splats(ply_path, use_kiri=True):
            print("   ✅ KIRI 엔진으로 Gaussian Splats 임포트 성공")
        elif gs_integration.load_gaussian_splats(ply_path, use_kiri=False):
            print("   ✅ 수동 방식으로 Gaussian Splats 임포트 성공")
        else:
            print("   ⚠️ Gaussian Splats 임포트 실패, 수동 생성...")
            # 수동으로 포인트 클라우드 생성
            from blender_colmap_3dgs.gaussian_splatting import create_gaussian_splat_points
            splat_obj = create_gaussian_splat_points(
                splat_positions, splat_colors, splat_properties, "ManualGaussianSplats"
            )
            gs_integration.splat_object = splat_obj
            gs_integration.splat_positions = splat_positions
            gs_integration.splat_colors = splat_colors
        
        # 정렬 수행
        if gs_integration.splat_object and len(colmap_points) > 0:
            print("   🔄 COLMAP과 Gaussian Splats 정렬 중...")
            gs_integration.align_with_colmap(colmap_points)
        
        # 시각화 설정
        gs_integration.setup_visualization()
        
        # 5단계: 최종 씬 설정
        print("\n5️⃣ 최종 씬 설정...")
        
        # 애니메이션 범위 설정
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = len(camera_poses)
        bpy.context.scene.frame_current = 1
        
        # 렌더 설정
        scene = bpy.context.scene
        scene.render.resolution_x = camera_params.get('width', 1920)
        scene.render.resolution_y = camera_params.get('height', 1080)
        scene.render.fps = 24
        
        # 카메라 뷰로 설정
        if blender_integration.camera:
            bpy.context.scene.camera = blender_integration.camera
            
            # 뷰포트를 카메라 뷰로 설정
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.region_3d.view_perspective = 'CAMERA'
                            break
                    break
        
        print("   ✅ 애니메이션 범위:", f"{bpy.context.scene.frame_start} - {bpy.context.scene.frame_end}")
        print("   ✅ 해상도:", f"{scene.render.resolution_x}x{scene.render.resolution_y}")
        print("   ✅ FPS:", scene.render.fps)
        
        # 완료 메시지
        print("\n🎉 통합 완료!")
        print("\n📖 사용법:")
        print("   • SPACEBAR: 애니메이션 재생/정지")
        print("   • NUM0: 카메라 뷰 전환")
        print("   • NUM7/NUM1/NUM3: 위/앞/옆 뷰")
        print("   • 마우스 가운데 버튼: 뷰 회전")
        print("   • 마우스 휠: 줌")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 시뮬레이션 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 시뮬레이션 실행
    success = main()
    
    if success:
        if BLENDER_MODE:
            print("\n🎬 Blender 씬이 준비되었습니다!")
        else:
            print("\n✅ 시뮬레이션 성공! Blender에서 실행하세요:")
            print("   blender --python simulation_script.py")
    else:
        print("\n❌ 시뮬레이션 실패")
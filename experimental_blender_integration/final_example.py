#!/usr/bin/env python3
"""
최종 실사용 예제 스크립트
실제 데이터 경로가 설정된 완성된 예제입니다.
"""

import bpy
import sys
from pathlib import Path

# 프로젝트 경로 추가
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from main import main

def run_final_example():
    """실제 데이터로 최종 예제 실행"""
    
    print("🚀 최종 COLMAP + 3DGS Blender 통합 예제")
    print("=" * 50)
    
    # 실제 데이터 경로 (사용자가 제공한 경로)
    colmap_path = "/home/hwoo-joo/github/hloc-nerfstudio/outputs/daewoo_drone_003_hloc_2/colmap"
    ply_path = "/home/hwoo-joo/github/hloc-nerfstudio/exports/splatfacto_daewoo_drone_003/daewoo_drone_003_hloc/splatfacto_daewoo_drone_003_splat.ply"
    
    # 이미지 경로는 생략 (이미지 플레인 없이 실행)
    images_path = None
    
    print(f"📁 COLMAP 경로: {colmap_path}")
    print(f"📄 PLY 경로: {ply_path}")
    print("🖼️  이미지 경로: 생략 (포인트 클라우드와 카메라만)")
    
    try:
        # 메인 통합 함수 실행
        success = main(
            colmap_path=colmap_path,
            ply_path=ply_path, 
            images_path=images_path,
            use_kiri=True  # KIRI 3DGS Engine 사용 (설치됨)
        )
        
        if success:
            print("\n🎉 통합 성공!")
            print("\n📖 조작법:")
            print("   • SPACEBAR: 애니메이션 재생/정지")
            print("   • NUM0: 카메라 뷰")
            print("   • NUM7/NUM1/NUM3: 위/앞/옆 뷰")
            print("   • 마우스 가운데 버튼: 뷰 회전")
            print("   • 마우스 휠: 줌 인/아웃")
            
            print("\n📊 씬 정보:")
            print(f"   • 애니메이션 길이: {bpy.context.scene.frame_end} 프레임")
            print(f"   • 해상도: {bpy.context.scene.render.resolution_x}x{bpy.context.scene.render.resolution_y}")
            print(f"   • FPS: {bpy.context.scene.render.fps}")
            
            # 오브젝트 개수 출력
            mesh_count = len([obj for obj in bpy.data.objects if obj.type == 'MESH'])
            camera_count = len([obj for obj in bpy.data.objects if obj.type == 'CAMERA'])
            print(f"   • 메쉬 오브젝트: {mesh_count}개")
            print(f"   • 카메라: {camera_count}개")
            
        return success
        
    except Exception as e:
        print(f"\n❌ 통합 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


# Blender에서 직접 실행
if __name__ == "__main__":
    run_final_example()

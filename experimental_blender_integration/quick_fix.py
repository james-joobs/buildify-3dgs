#!/usr/bin/env python3
"""
빠른 수정 스크립트 - 3DGS 시각화 문제 해결
"""

import bpy
import sys
from pathlib import Path
import numpy as np

# 프로젝트 경로 추가
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from main import main

def quick_fix_visualization():
    """3DGS 시각화 문제를 빠르게 수정"""
    
    print("🔧 Quick Fix for 3DGS Visualization Issues")
    print("=" * 50)
    
    # 실제 데이터 경로
    colmap_path = "/home/hwoo-joo/github/hloc-nerfstudio/outputs/daewoo_drone_003_hloc_2/colmap"
    ply_path = "/home/hwoo-joo/github/hloc-nerfstudio/exports/splatfacto_daewoo_drone_003/daewoo_drone_003_hloc/splatfacto_daewoo_drone_003_splat.ply"
    
    try:
        # 메인 통합 함수 실행
        success = main(
            colmap_path=colmap_path,
            ply_path=ply_path, 
            images_path=None,
            use_kiri=False
        )
        
        if success:
            print("\n🎯 Applying quick fixes...")
            
            # 1. 3DGS 객체 찾기 및 수정
            gaussian_objects = [obj for obj in bpy.data.objects if 'Gaussian' in obj.name or 'Splat' in obj.name]
            
            if gaussian_objects:
                for obj in gaussian_objects:
                    print(f"   🔍 Found 3DGS object: {obj.name}")
                    
                    # 객체를 더 잘 보이게 만들기
                    obj.display_type = 'SOLID'
                    
                    # 머티리얼 수정
                    if obj.data.materials:
                        mat = obj.data.materials[0]
                        if mat and mat.use_nodes:
                            # 더 밝게 만들기
                            for node in mat.node_tree.nodes:
                                if node.type == 'EMISSION':
                                    node.inputs['Strength'].default_value = 5.0  # 더 밝게
                                elif node.type == 'BSDF_PRINCIPLED':
                                    node.inputs['Roughness'].default_value = 0.1
                                    node.inputs['Metallic'].default_value = 0.2
                            
                            print(f"   ✨ Enhanced material for {obj.name}")
            
            # 2. 뷰포트 설정 수정
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            # Rendered 모드로 변경
                            space.shading.type = 'RENDERED'
                            space.shading.use_scene_world = True
                            space.shading.use_scene_lights = True
                            print("   🎭 Set viewport to Rendered mode")
                            break
                    break
            
            # 3. 렌더 엔진 설정 (Blender 버전 호환)
            try:
                bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
                print("   💫 Using EEVEE Next (Blender 4.0+)")
                # EEVEE Next has different properties
            except:
                try:
                    bpy.context.scene.render.engine = 'EEVEE'
                    eevee = bpy.context.scene.eevee
                    eevee.use_bloom = True
                    eevee.bloom_intensity = 1.0
                    eevee.bloom_radius = 8.0
                    print("   💫 Using EEVEE (Blender 3.x) with bloom")
                except:
                    bpy.context.scene.render.engine = 'CYCLES'
                    print("   💫 Fallback to Cycles")
            
            # 4. 조명 추가
            # 밝은 sun light 추가
            bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
            sun = bpy.context.active_object
            sun.data.energy = 10.0
            sun.data.color = (1.0, 1.0, 1.0)
            print("   ☀️ Added bright sun light")
            
            # 5. 카메라 위치 조정 (첫 번째 프레임으로 이동 후 약간 뒤로)
            camera = bpy.context.scene.camera
            if camera:
                bpy.context.scene.frame_set(1)
                # 카메라를 약간 뒤로 이동
                camera.location = (
                    camera.location.x - 2,
                    camera.location.y - 2, 
                    camera.location.z + 2
                )
                print("   📷 Adjusted camera position for better view")
            
            # 6. 배경 밝기 조정
            world = bpy.context.scene.world
            if world and world.use_nodes:
                bg_node = world.node_tree.nodes.get('Background')
                if bg_node:
                    bg_node.inputs['Color'].default_value = (0.1, 0.1, 0.15, 1.0)  # 약간 밝은 파란색
                    bg_node.inputs['Strength'].default_value = 0.5
                    print("   🌍 Set brighter background")
            
            print("\n🎉 Quick fixes applied successfully!")
            print("\n📖 조작법:")
            print("   • SPACEBAR: 애니메이션 재생/정지")
            print("   • NUM0: 카메라 뷰")
            print("   • NUM7/NUM1/NUM3: 위/앞/옆 뷰")
            print("   • Z키 + 8: Rendered 뷰 토글")
            
        return success
        
    except Exception as e:
        print(f"\n❌ Quick fix 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    quick_fix_visualization()
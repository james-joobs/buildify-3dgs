#!/usr/bin/env python3
"""
초간단 버전 - 확실히 작동하는 3DGS 시각화
"""

import bpy
import sys
from pathlib import Path
import numpy as np
import mathutils

project_root = Path(__file__).parent
sys.path.append(str(project_root))

from blender_colmap_3dgs.colmap_parser import COLMAPLoader
from blender_colmap_3dgs.gaussian_splatting import load_ply_gaussian_splats

def ultra_simple_main():
    """최대한 간단한 통합"""
    
    print("🚀 Ultra Simple 3DGS + COLMAP Visualization")
    print("=" * 50)
    
    # 실제 경로
    colmap_path = "/home/hwoo-joo/github/hloc-nerfstudio/outputs/daewoo_drone_003_hloc_2/colmap"
    ply_path = "/home/hwoo-joo/github/hloc-nerfstudio/exports/splatfacto_daewoo_drone_003/daewoo_drone_003_hloc/splatfacto_daewoo_drone_003_splat.ply"
    
    try:
        # 1. 씬 클리어
        print("\n🧹 Clearing scene...")
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # 2. COLMAP 데이터 로드
        print("\n📁 Loading COLMAP data...")
        colmap_loader = COLMAPLoader(colmap_path)
        colmap_loader.load_reconstruction()
        
        if not colmap_loader.images:
            print("❌ No COLMAP images found")
            return False
        
        # 카메라 포즈와 포인트 클라우드
        camera_poses = colmap_loader.get_camera_poses_for_blender()
        colmap_points, colmap_colors = colmap_loader.get_point_cloud()
        
        print(f"   ✅ {len(camera_poses)} poses, {len(colmap_points)} points")
        
        # 3. 3DGS 데이터 로드
        print("\n📄 Loading 3DGS data...")
        splat_positions, splat_colors, _ = load_ply_gaussian_splats(ply_path)
        
        # 서브샘플링 (성능을 위해)
        if len(splat_positions) > 50000:
            indices = np.random.choice(len(splat_positions), 50000, replace=False)
            splat_positions = splat_positions[indices]
            splat_colors = splat_colors[indices]
            print(f"   📊 Subsampled to {len(splat_positions)} splats")
        
        # 좌표 변환 (COLMAP 맞추기)
        transform = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
        splat_positions = (transform @ splat_positions.T).T
        
        print(f"   ✅ {len(splat_positions)} splats loaded")
        
        # 4. 간단한 카메라 애니메이션
        print("\n📷 Creating camera...")
        bpy.ops.object.camera_add()
        camera = bpy.context.active_object
        camera.name = "AnimatedCamera"
        
        # 애니메이션 설정
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = min(len(camera_poses), 100)  # 최대 100프레임
        
        # 키프레임 추가 (간단히)
        for i, (name, rot_matrix, translation) in enumerate(camera_poses[:100]):
            frame = i + 1
            bpy.context.scene.frame_set(frame)
            
            # 위치 설정
            camera.location = mathutils.Vector(translation)
            
            # 회전 설정
            rot_euler = mathutils.Matrix(rot_matrix).to_euler()
            camera.rotation_euler = rot_euler
            
            # 키프레임 삽입
            camera.keyframe_insert(data_path="location")
            camera.keyframe_insert(data_path="rotation_euler")
        
        bpy.context.scene.camera = camera
        print(f"   ✅ Camera with {bpy.context.scene.frame_end} keyframes")
        
        # 5. COLMAP 포인트 클라우드 (간단한 큐브들)
        print("\n🔴 Creating COLMAP visualization...")
        
        # 서브샘플링
        if len(colmap_points) > 10000:
            indices = np.random.choice(len(colmap_points), 10000, replace=False)
            colmap_sample = colmap_points[indices]
            colmap_colors_sample = colmap_colors[indices]
        else:
            colmap_sample = colmap_points
            colmap_colors_sample = colmap_colors
        
        for i, (point, color) in enumerate(zip(colmap_sample, colmap_colors_sample)):
            if i % 1000 == 0:  # 더 적은 포인트만
                bpy.ops.mesh.primitive_cube_add(location=point, size=0.1)
                cube = bpy.context.active_object
                cube.name = f"COLMAP_Point_{i}"
                
                # 빨간색 머티리얼
                mat = bpy.data.materials.new(f"ColmapMat_{i}")
                mat.use_nodes = True
                nodes = mat.node_tree.nodes
                nodes.clear()
                
                output = nodes.new('ShaderNodeOutputMaterial')
                emission = nodes.new('ShaderNodeEmission')
                emission.inputs['Color'].default_value = (*color, 1.0)
                emission.inputs['Strength'].default_value = 2.0
                
                mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
                cube.data.materials.append(mat)
        
        print(f"   ✅ COLMAP points created (sampled)")
        
        # 6. 3DGS 포인트 클라우드 (구체들)
        print("\n🟡 Creating 3DGS visualization...")
        
        # 더 적은 샘플링
        if len(splat_positions) > 5000:
            indices = np.random.choice(len(splat_positions), 5000, replace=False)
            splat_sample = splat_positions[indices]
            splat_colors_sample = splat_colors[indices]
        else:
            splat_sample = splat_positions
            splat_colors_sample = splat_colors
        
        # 중심점 정렬
        if len(colmap_sample) > 0 and len(splat_sample) > 0:
            colmap_center = np.mean(colmap_sample, axis=0)
            splat_center = np.mean(splat_sample, axis=0)
            offset = colmap_center - splat_center
            
            for i, (point, color) in enumerate(zip(splat_sample, splat_colors_sample)):
                if i % 500 == 0:  # 매우 적은 포인트만
                    adjusted_point = point + offset
                    bpy.ops.mesh.primitive_uv_sphere_add(location=adjusted_point, radius=0.05)
                    sphere = bpy.context.active_object
                    sphere.name = f"Splat_{i}"
                    
                    # 노란색 머티리얼
                    mat = bpy.data.materials.new(f"SplatMat_{i}")
                    mat.use_nodes = True
                    nodes = mat.node_tree.nodes
                    nodes.clear()
                    
                    output = nodes.new('ShaderNodeOutputMaterial')
                    emission = nodes.new('ShaderNodeEmission')
                    emission.inputs['Color'].default_value = (*color, 1.0)
                    emission.inputs['Strength'].default_value = 3.0
                    
                    mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
                    sphere.data.materials.append(mat)
            
            print(f"   ✅ 3DGS points created with offset: {offset}")
        
        # 7. 조명과 설정
        print("\n💡 Setting up lighting...")
        
        # 밝은 조명
        bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
        sun = bpy.context.active_object
        sun.data.energy = 10.0
        
        # 간단한 렌더 설정
        available_engines = [item.identifier for item in bpy.types.Scene.bl_rna.properties['render'].fixed_type.properties['engine'].enum_items]
        
        if 'BLENDER_EEVEE_NEXT' in available_engines:
            bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
            print("   ✅ Using EEVEE Next")
        elif 'EEVEE' in available_engines:
            bpy.context.scene.render.engine = 'EEVEE'
            print("   ✅ Using EEVEE")
        else:
            bpy.context.scene.render.engine = 'CYCLES'
            print("   ✅ Using Cycles")
        
        # 뷰포트 설정
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        break
                break
        
        # 첫 프레임으로 이동
        bpy.context.scene.frame_set(1)
        
        print("\n🎉 Ultra Simple setup complete!")
        print("\n📖 Controls:")
        print("   • SPACEBAR: Play animation")
        print("   • NUM0: Camera view") 
        print("   • 🔴 Red cubes = COLMAP points")
        print("   • 🟡 Yellow spheres = 3DGS points")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    ultra_simple_main()
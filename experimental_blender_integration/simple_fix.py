#!/usr/bin/env python3
"""
간단한 수정 버전 - 3DGS를 간단한 포인트 클라우드로 시각화
"""

import bpy
import sys
from pathlib import Path
import numpy as np

project_root = Path(__file__).parent
sys.path.append(str(project_root))

from blender_colmap_3dgs.colmap_parser import COLMAPLoader
from blender_colmap_3dgs.gaussian_splatting import load_ply_gaussian_splats
from blender_colmap_3dgs.blender_animation import BlenderCOLMAPIntegration

def create_simple_point_cloud(positions, colors, name="SimplePointCloud"):
    """간단한 포인트 클라우드 생성 (성능 최적화)"""
    
    print(f"🔨 Creating simple point cloud with {len(positions)} points...")
    
    # 큰 데이터는 서브샘플링
    if len(positions) > 100000:
        print(f"   📊 Subsampling to 100k points for better performance...")
        indices = np.random.choice(len(positions), 100000, replace=False)
        positions = positions[indices]
        colors = colors[indices] if len(colors) > 0 else colors
    
    # 간단한 vertex mesh 생성
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # 단순 정점만 생성 (면 없음)
    mesh.from_pydata(positions.tolist(), [], [])
    mesh.update()
    
    # 정점 색상 적용
    if len(colors) > 0:
        mesh.vertex_colors.new(name='Color')
        color_layer = mesh.vertex_colors['Color']
        
        # 정점 색상 설정 (간단한 방식)
        for i, color in enumerate(colors):
            if i < len(mesh.vertices):
                # Vertex colors are applied per face-loop, but we need per-vertex
                # For point clouds, we create dummy faces
                pass
    
    # 간단한 에미시브 머티리얼
    mat = bpy.data.materials.new(name=f"{name}_Material")
    mat.use_nodes = True
    obj.data.materials.append(mat)
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # 단순 에미시브 셰이더
    output = nodes.new('ShaderNodeOutputMaterial')
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Strength'].default_value = 3.0
    emission.inputs['Color'].default_value = (1.0, 0.5, 0.2, 1.0)  # 주황색으로 잘 보이게
    
    links.new(emission.outputs['Emission'], output.inputs['Surface'])
    
    # 포인트 클라우드 표시 설정
    obj.display_type = 'SOLID'
    
    print(f"   ✅ Simple point cloud created: {len(mesh.vertices)} vertices")
    return obj

def simple_main():
    """간단한 통합 함수"""
    
    print("🚀 Simple 3DGS Visualization")
    print("=" * 40)
    
    # 실제 경로
    colmap_path = "/home/hwoo-joo/github/hloc-nerfstudio/outputs/daewoo_drone_003_hloc_2/colmap"
    ply_path = "/home/hwoo-joo/github/hloc-nerfstudio/exports/splatfacto_daewoo_drone_003/daewoo_drone_003_hloc/splatfacto_daewoo_drone_003_splat.ply"
    
    try:
        # 기존 오브젝트 삭제
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # 1. COLMAP 데이터 로드
        print("\n1️⃣ Loading COLMAP data...")
        colmap_loader = COLMAPLoader(colmap_path)
        colmap_loader.load_reconstruction()
        
        camera_poses = colmap_loader.get_camera_poses_for_blender()
        colmap_points, colmap_colors = colmap_loader.get_point_cloud()
        
        print(f"   ✅ {len(camera_poses)} camera poses, {len(colmap_points)} points")
        
        # 2. 3DGS 데이터 로드  
        print("\n2️⃣ Loading 3DGS data...")
        splat_positions, splat_colors, splat_properties = load_ply_gaussian_splats(ply_path)
        print(f"   ✅ {len(splat_positions)} Gaussian splats loaded")
        
        # 3. 카메라 애니메이션 생성
        print("\n3️⃣ Creating camera animation...")
        from blender_colmap_3dgs.blender_animation import create_camera_with_animation
        
        # 카메라 생성
        camera = create_camera_with_animation(camera_poses)
        print(f"   ✅ Camera animation: {len(camera_poses)} frames")
        
        # 4. COLMAP 포인트 클라우드 (간단히)
        print("\n4️⃣ Creating COLMAP point cloud...")
        colmap_obj = create_simple_point_cloud(colmap_points, colmap_colors, "COLMAP_Points")
        colmap_obj.location = (0, 0, 0)  # 원점에 위치
        
        # 5. 3DGS 포인트 클라우드 (간단히)
        print("\n5️⃣ Creating 3DGS point cloud...")
        
        # 좌표 변환 (COLMAP과 맞추기)
        transform_matrix = np.array([
            [1, 0, 0],
            [0, 0, -1],
            [0, 1, 0]
        ])
        splat_positions_transformed = (transform_matrix @ splat_positions.T).T
        
        splat_obj = create_simple_point_cloud(splat_positions_transformed, splat_colors, "Gaussian_Splats")
        
        # 간단한 정렬 (중심점 맞추기)
        colmap_center = np.mean(colmap_points, axis=0)
        splat_center = np.mean(splat_positions_transformed, axis=0)
        offset = colmap_center - splat_center
        
        splat_obj.location = tuple(offset)
        print(f"   ✅ 3DGS aligned with offset: {offset}")
        
        # 6. 씬 설정
        print("\n6️⃣ Setting up scene...")
        
        # 애니메이션 설정
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = len(camera_poses)
        bpy.context.scene.frame_current = 1
        
        # 카메라 설정
        if camera:
            bpy.context.scene.camera = camera
        
        # 밝은 조명 추가
        bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
        sun = bpy.context.active_object
        sun.data.energy = 5.0
        
        # 렌더 설정 (Blender 버전 호환)
        try:
            bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
            print("   ✅ Using EEVEE Next")
        except:
            try:
                bpy.context.scene.render.engine = 'EEVEE'
                print("   ✅ Using EEVEE")
            except:
                bpy.context.scene.render.engine = 'CYCLES'
                print("   ✅ Fallback to Cycles")
        
        # 뷰포트 설정
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        space.region_3d.view_perspective = 'CAMERA'
                        break
                break
        
        print("\n🎉 Simple setup complete!")
        print("\n📖 Controls:")
        print("   • SPACEBAR: Play/pause animation") 
        print("   • NUM0: Camera view")
        print("   • NUM7/1/3: Top/front/side views")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    simple_main()
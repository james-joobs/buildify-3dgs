#!/usr/bin/env python3
"""Test full integration without Blender"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from blender_colmap_3dgs.colmap_parser import COLMAPLoader
from blender_colmap_3dgs.gaussian_splatting import load_ply_gaussian_splats

def test_full_integration():
    """Test full integration pipeline (without Blender components)"""
    
    # Real paths
    colmap_path = "/home/hwoo-joo/github/hloc-nerfstudio/outputs/daewoo_drone_003_hloc_2/colmap"
    ply_path = "/home/hwoo-joo/github/hloc-nerfstudio/exports/splatfacto_daewoo_drone_003/daewoo_drone_003_hloc/splatfacto_daewoo_drone_003_splat.ply"
    
    print("=== Full Integration Test ===")
    print(f"COLMAP path: {colmap_path}")
    print(f"PLY path: {ply_path}")
    
    try:
        # Step 1: Load COLMAP data
        print("\n1. Loading COLMAP reconstruction...")
        colmap_loader = COLMAPLoader(colmap_path)
        colmap_loader.load_reconstruction()
        
        if not colmap_loader.images:
            print("❌ No COLMAP images loaded")
            return False
            
        print(f"✅ COLMAP: {len(colmap_loader.cameras)} cameras, {len(colmap_loader.images)} images, {len(colmap_loader.points3d)} points")
        
        # Step 2: Get camera poses
        print("\n2. Converting camera poses for Blender...")
        camera_poses = colmap_loader.get_camera_poses_for_blender()
        print(f"✅ Converted {len(camera_poses)} camera poses")
        
        # Step 3: Get point cloud
        print("\n3. Extracting COLMAP point cloud...")
        colmap_points, colmap_colors = colmap_loader.get_point_cloud()
        print(f"✅ Point cloud: {len(colmap_points)} points with colors")
        
        # Step 4: Load Gaussian splats
        print("\n4. Loading Gaussian splats...")
        splat_positions, splat_colors, splat_properties = load_ply_gaussian_splats(ply_path)
        print(f"✅ Gaussian splats: {len(splat_positions)} splats")
        
        # Step 5: Data analysis and alignment check
        print("\n5. Analyzing data alignment...")
        
        if len(colmap_points) > 0 and len(splat_positions) > 0:
            import numpy as np
            
            # Calculate centroids
            colmap_centroid = np.mean(colmap_points, axis=0)
            splat_centroid = np.mean(splat_positions, axis=0)
            
            print(f"COLMAP centroid: {colmap_centroid}")
            print(f"Splat centroid: {splat_centroid}")
            print(f"Centroid distance: {np.linalg.norm(colmap_centroid - splat_centroid):.3f}")
            
            # Calculate bounding boxes
            colmap_bbox = np.ptp(colmap_points, axis=0)
            splat_bbox = np.ptp(splat_positions, axis=0)
            
            print(f"COLMAP bounding box: {colmap_bbox}")
            print(f"Splat bounding box: {splat_bbox}")
        
        # Step 6: Camera properties analysis
        print("\n6. Analyzing camera properties...")
        if colmap_loader.cameras:
            first_camera = list(colmap_loader.cameras.values())[0]
            print(f"Camera model: {first_camera.model}")
            print(f"Resolution: {first_camera.width}x{first_camera.height}")
            print(f"Focal length: {first_camera.params[0]:.1f} pixels")
            
            # Estimate FOV
            fov_h = 2 * np.arctan(first_camera.width / (2 * first_camera.params[0])) * 180 / np.pi
            fov_v = 2 * np.arctan(first_camera.height / (2 * first_camera.params[0])) * 180 / np.pi
            print(f"Estimated FOV: {fov_h:.1f}° horizontal, {fov_v:.1f}° vertical")
        
        # Step 7: Animation analysis
        print("\n7. Analyzing camera animation...")
        if len(camera_poses) > 1:
            # Calculate camera path length
            path_length = 0
            prev_pos = camera_poses[0][2]
            for _, _, pos in camera_poses[1:]:
                path_length += np.linalg.norm(pos - prev_pos)
                prev_pos = pos
            
            print(f"Camera path length: {path_length:.2f} units")
            print(f"Animation frames: {len(camera_poses)}")
            print(f"Recommended frame rate: 24-30 fps")
            
            # Check for smooth motion
            positions = np.array([pos for _, _, pos in camera_poses])
            velocities = np.diff(positions, axis=0)
            avg_velocity = np.mean(np.linalg.norm(velocities, axis=1))
            print(f"Average camera velocity: {avg_velocity:.3f} units/frame")
        
        print("\n✅ Full integration test completed successfully!")
        print("\nReady for Blender integration!")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_integration()
    
    if success:
        print("\n🎉 All tests passed! Integration is ready.")
        print("\nNext steps:")
        print("1. Run the integration in Blender using main.py")
        print("2. Or use example_usage.py with your paths")
    else:
        print("\n❌ Integration test failed. Check errors above.")
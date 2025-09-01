#!/usr/bin/env python3
"""Test COLMAP parser with real data"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from blender_colmap_3dgs.colmap_parser import COLMAPLoader

def test_colmap_loading():
    """Test loading COLMAP data with actual paths"""
    
    # Real paths from the user
    colmap_path = "/home/hwoo-joo/github/hloc-nerfstudio/outputs/daewoo_drone_003_hloc_2/colmap"
    
    print(f"Testing COLMAP loader with path: {colmap_path}")
    
    try:
        # Initialize loader
        loader = COLMAPLoader(colmap_path)
        
        # Load reconstruction
        loader.load_reconstruction()
        
        # Print summary
        print("\n=== COLMAP Loading Results ===")
        print(f"Cameras loaded: {len(loader.cameras)}")
        print(f"Images loaded: {len(loader.images)}")
        print(f"3D Points loaded: {len(loader.points3d)}")
        
        if loader.cameras:
            print("\n=== Camera Info ===")
            for cam_id, camera in loader.cameras.items():
                print(f"Camera {cam_id}: {camera.model} ({camera.width}x{camera.height})")
                print(f"  Parameters: {camera.params}")
        
        if loader.images:
            print(f"\n=== Sample Images ===")
            sample_images = list(loader.images.items())[:5]  # First 5 images
            for img_id, image in sample_images:
                print(f"Image {img_id}: {image.name}")
                print(f"  Camera ID: {image.camera_id}")
                print(f"  Quaternion: {image.qvec}")
                print(f"  Translation: {image.tvec}")
        
        # Test coordinate conversion
        print(f"\n=== Testing Blender Coordinate Conversion ===")
        poses = loader.get_camera_poses_for_blender()
        print(f"Converted {len(poses)} camera poses for Blender")
        
        if poses:
            sample_pose = poses[0]
            print(f"Sample pose: {sample_pose[0]}")
            print(f"  Rotation matrix shape: {sample_pose[1].shape}")
            print(f"  Translation vector: {sample_pose[2]}")
        
        # Test point cloud
        print(f"\n=== Testing Point Cloud ===")
        points, colors = loader.get_point_cloud()
        print(f"Point cloud: {len(points)} points")
        if len(points) > 0:
            print(f"  Point range X: {points[:, 0].min():.3f} to {points[:, 0].max():.3f}")
            print(f"  Point range Y: {points[:, 1].min():.3f} to {points[:, 1].max():.3f}")
            print(f"  Point range Z: {points[:, 2].min():.3f} to {points[:, 2].max():.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing COLMAP loader: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_colmap_loading()
    if success:
        print("\n✅ COLMAP parsing test completed successfully!")
    else:
        print("\n❌ COLMAP parsing test failed!")
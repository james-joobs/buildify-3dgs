"""COLMAP data parsing utilities"""
import struct
from pathlib import Path
from typing import Dict, List, NamedTuple, Tuple, Iterable
import numpy as np


class Camera(NamedTuple):
    id: int
    model: str
    width: int
    height: int
    params: np.ndarray


class Image(NamedTuple):
    id: int
    qvec: np.ndarray  # quaternion (w, x, y, z)
    tvec: np.ndarray  # translation vector
    camera_id: int
    name: str
    point3d_ids: np.ndarray


class Point3D(NamedTuple):
    id: int
    xyz: np.ndarray
    rgb: np.ndarray
    error: float
    image_ids: np.ndarray
    point2d_idxs: np.ndarray


def read_next_bytes(fid, num_bytes: int, format_char_sequence: str, endian_character: str = "<"):
    """Read and unpack next bytes from file"""
    data = fid.read(num_bytes)
    return struct.unpack(endian_character + format_char_sequence, data)


def read_cameras_binary(path_to_model_file: str) -> Dict[int, Camera]:
    """Read COLMAP cameras.bin file"""
    cameras = {}
    with open(path_to_model_file, "rb") as fid:
        num_cameras = read_next_bytes(fid, 8, "Q")[0]
        for _ in range(num_cameras):
            camera_properties = read_next_bytes(fid, 24, "iiQQ")
            camera_id = camera_properties[0]
            model_id = camera_properties[1]
            model_name = {
                0: "SIMPLE_PINHOLE",
                1: "PINHOLE", 
                2: "SIMPLE_RADIAL",
                3: "RADIAL",
                4: "OPENCV",
                5: "OPENCV_FISHEYE",
                6: "FULL_OPENCV",
                7: "FOV",
                8: "SIMPLE_RADIAL_FISHEYE",
                9: "RADIAL_FISHEYE",
                10: "THIN_PRISM_FISHEYE"
            }.get(model_id, "UNKNOWN")
            
            width = camera_properties[2]
            height = camera_properties[3]
            
            num_params = {
                0: 3, 1: 4, 2: 4, 3: 5, 4: 8, 5: 8, 6: 12, 7: 5, 8: 4, 9: 5, 10: 12
            }.get(model_id, 0)
            
            params = read_next_bytes(fid, 8*num_params, "d"*num_params)
            cameras[camera_id] = Camera(
                id=camera_id,
                model=model_name,
                width=int(width),
                height=int(height),
                params=np.array(params)
            )
    return cameras


def read_images_binary(path_to_model_file: str) -> Dict[int, Image]:
    """Read COLMAP images.bin file"""
    images = {}
    with open(path_to_model_file, "rb") as fid:
        num_reg_images = read_next_bytes(fid, 8, "Q")[0]
        for _ in range(num_reg_images):
            binary_image_properties = read_next_bytes(fid, 64, "idddddddi")
            image_id = binary_image_properties[0]
            qvec = np.array(binary_image_properties[1:5])
            tvec = np.array(binary_image_properties[5:8])
            camera_id = binary_image_properties[8]
            
            image_name = ""
            current_char = read_next_bytes(fid, 1, "c")[0]
            while current_char != b"\x00":
                image_name += current_char.decode("utf-8")
                current_char = read_next_bytes(fid, 1, "c")[0]
            
            num_points2d = read_next_bytes(fid, 8, "Q")[0]
            x_y_id_s = read_next_bytes(fid, 24*num_points2d, "ddq"*num_points2d)
            point3d_ids = np.array(tuple(map(int, x_y_id_s[2::3])))
            
            images[image_id] = Image(
                id=image_id,
                qvec=qvec,
                tvec=tvec,
                camera_id=camera_id,
                name=image_name,
                point3d_ids=point3d_ids
            )
    return images


def read_points3d_binary(path_to_model_file: str) -> Dict[int, Point3D]:
    """Read COLMAP points3D.bin file"""
    points3d = {}
    with open(path_to_model_file, "rb") as fid:
        num_points = read_next_bytes(fid, 8, "Q")[0]
        for _ in range(num_points):
            binary_point_line_properties = read_next_bytes(fid, 43, "QdddBBBd")
            point3d_id = binary_point_line_properties[0]
            xyz = np.array(binary_point_line_properties[1:4])
            rgb = np.array(binary_point_line_properties[4:7])
            error = binary_point_line_properties[7]
            
            track_length = read_next_bytes(fid, 8, "Q")[0]
            track_elems = read_next_bytes(fid, 8*track_length, "ii"*track_length)
            image_ids = np.array(tuple(map(int, track_elems[0::2])))
            point2d_idxs = np.array(tuple(map(int, track_elems[1::2])))
            
            points3d[point3d_id] = Point3D(
                id=point3d_id,
                xyz=xyz,
                rgb=rgb,
                error=error,
                image_ids=image_ids,
                point2d_idxs=point2d_idxs
            )
    return points3d


def quat_to_rotation_matrix(qvec: np.ndarray) -> np.ndarray:
    """Convert quaternion to rotation matrix"""
    qvec = qvec / np.linalg.norm(qvec)
    w, x, y, z = qvec
    
    R = np.array([
        [1 - 2*y*y - 2*z*z, 2*x*y - 2*z*w, 2*x*z + 2*y*w],
        [2*x*y + 2*z*w, 1 - 2*x*x - 2*z*z, 2*y*z - 2*x*w],
        [2*x*z - 2*y*w, 2*y*z + 2*x*w, 1 - 2*x*x - 2*y*y]
    ])
    return R


def colmap_to_blender_transform(qvec: np.ndarray, tvec: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Convert COLMAP camera pose (world-to-camera) to Blender camera pose (camera-to-world).

    COLMAP stores [R | t] that maps world to camera: x_cam = R x_world + t
    Camera-to-world transform is: R_c2w = R.T, t_c2w = -R.T @ t

    Then convert coordinates from COLMAP (x right, y down, z forward)
    to Blender (x right, y forward, z up): (x, y, z) -> (x, -z, y)
    """
    R = quat_to_rotation_matrix(qvec)

    colmap_to_blender = np.array(
        [
            [1, 0, 0],
            [0, 0, -1],
            [0, 1, 0],
        ]
    )

    R_c2w = R.T
    t_c2w = -R_c2w @ tvec

    R_blender = colmap_to_blender @ R_c2w
    t_blender = colmap_to_blender @ t_c2w

    return R_blender, t_blender


class COLMAPLoader:
    """COLMAP data loader"""
    
    def __init__(self, colmap_path: str):
        self.colmap_path = Path(colmap_path)
        self.cameras = {}
        self.images = {}
        self.points3d = {}
        
    def load_reconstruction(self):
        """Load COLMAP reconstruction data"""
        # Try multiple possible locations for COLMAP files
        possible_paths = [
            self.colmap_path / "sparse" / "0",  # Standard location
            self.colmap_path / "sparse",        # Alternative location
            self.colmap_path,                   # Direct in colmap_path
        ]
        
        cameras_path = None
        images_path = None
        points3d_path = None
        
        # Find the correct paths
        for base_path in possible_paths:
            test_cameras = base_path / "cameras.bin"
            test_images = base_path / "images.bin"
            test_points3d = base_path / "points3D.bin"
            
            if test_cameras.exists() and test_images.exists() and test_points3d.exists():
                cameras_path = test_cameras
                images_path = test_images
                points3d_path = test_points3d
                print(f"Found COLMAP files in: {base_path}")
                break
        
        if not cameras_path:
            print("Warning: Could not find complete COLMAP reconstruction files")
            return
            
        # Load the files
        try:
            self.cameras = read_cameras_binary(str(cameras_path))
            print(f"Loaded {len(self.cameras)} cameras")
        except Exception as e:
            print(f"Error loading cameras: {e}")
            
        try:
            self.images = read_images_binary(str(images_path))
            print(f"Loaded {len(self.images)} images")
        except Exception as e:
            print(f"Error loading images: {e}")
            
        try:
            self.points3d = read_points3d_binary(str(points3d_path))
            print(f"Loaded {len(self.points3d)} 3D points")
        except Exception as e:
            print(f"Error loading 3D points: {e}")
            
    def get_camera_poses_for_blender(self, sort: str = "id") -> List[Tuple[str, np.ndarray, np.ndarray]]:
        """Get camera poses converted to Blender coordinate system.

        sort: 'id' (default) sorts by image id, 'name' sorts by image filename.
        """
        if not self.images:
            return []

        if sort == "name":
            images: Iterable[Image] = sorted(self.images.values(), key=lambda im: im.name)
        else:
            images = sorted(self.images.values(), key=lambda im: im.id)

        poses: List[Tuple[str, np.ndarray, np.ndarray]] = []
        for image in images:
            R_blender, t_blender = colmap_to_blender_transform(image.qvec, image.tvec)
            poses.append((image.name, R_blender, t_blender))
        return poses
        
    def get_point_cloud(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get 3D point cloud in Blender coordinates"""
        if not self.points3d:
            return np.array([]), np.array([])
            
        points = []
        colors = []
        
        # Convert to Blender coordinate system
        colmap_to_blender = np.array([
            [1, 0, 0],
            [0, 0, -1],
            [0, 1, 0]
        ])
        
        for point3d in self.points3d.values():
            point_blender = colmap_to_blender @ point3d.xyz
            points.append(point_blender)
            colors.append(point3d.rgb / 255.0)  # Normalize to [0, 1]

        return np.array(points), np.array(colors)

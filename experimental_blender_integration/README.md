# Blender COLMAP 3D Gaussian Splatting Integration

COLMAP 재구성 데이터와 3D Gaussian Splatting PLY 파일을 Blender에서 자동으로 정합하고 시각화하는 Python 프로젝트입니다.

## 기능

- ✅ COLMAP binary 파일 (.bin) 파싱 및 로드
- ✅ Blender에서 COLMAP 카메라 궤적을 따르는 애니메이션 카메라 생성
- ✅ COLMAP sparse 포인트 클라우드 시각화
- ✅ 3D Gaussian Splatting PLY 파일 임포트 및 시각화
- ✅ KIRI 3DGS Engine 애드온과의 자동 연동
- ✅ COLMAP과 Gaussian Splats 간 자동 정렬
- ✅ 원본 이미지들을 따라 움직이는 이미지 플레인 생성

## 요구사항

### Python 환경
- Python 3.10 또는 3.11 (Blender 호환성)
- uv 패키지 매니저

### Blender 애드온
- **Photogrammetry** 애드온 (이미 설치됨)
- **KIRI 3DGS Engine** 애드온 (이미 설치됨)

### 필수 데이터
- COLMAP 재구성 결과:
  - `sparse/0/cameras.bin`
  - `sparse/0/images.bin`
  - `sparse/0/points3D.bin`
- Nerfstudio splatfacto로 생성한 `splat.ply` 파일
- 원본 비디오 프레임 이미지들

## 설치

1. 프로젝트 클론 및 의존성 설치:
```bash
cd buildify-3dgs
uv sync
```

2. Blender Python 환경에서 패키지 설치:
```bash
# Blender의 Python 경로에 따라 달라질 수 있음
uv pip install -e .
```

## 사용법

### 1. 빠른 시작 (실제 데이터 사용)

```python
# Blender 내에서 final_example.py 실행 또는
# Text Editor에서 다음 코드 실행:

import sys
sys.path.append('/home/hwoo-joo/github/buildify-3dgs')
from main import main

# 실제 데이터 경로
colmap_path = "/home/hwoo-joo/github/hloc-nerfstudio/outputs/daewoo_drone_003_hloc_2/colmap"
ply_path = "/home/hwoo-joo/github/hloc-nerfstudio/exports/splatfacto_daewoo_drone_003/daewoo_drone_003_hloc/splatfacto_daewoo_drone_003_splat.ply"

# 통합 실행
main(colmap_path, ply_path, None, use_kiri=False)
```

### 2. 기본 사용법 (다른 데이터)

```python
# 사용자 데이터로 실행
colmap_path = '/your/colmap/workspace'     # sparse/0/ 폴더를 포함
ply_path = '/your/splat.ply'              # Gaussian splats PLY 파일
images_path = '/your/images'              # 원본 이미지 폴더 (선택사항)

main(colmap_path, ply_path, images_path, use_kiri=True)
```

### 3. Blender Text Editor에서 실행

1. Blender를 실행합니다
2. Text Editor에서 `final_example.py`를 불러옵니다
3. 스크립트를 실행합니다 (Alt+P)

### 4. 명령줄에서 Blender 실행

```bash
# 실제 데이터로 실행
blender --python final_example.py

# 또는 일반적인 사용
blender --python main.py
```

## 테스트된 실제 데이터 정보

프로젝트는 다음 실제 데이터로 테스트되었습니다:

- **드론 영상**: 312 프레임
- **카메라**: OPENCV 모델 (3840x2160, FOV ~66°)
- **COLMAP**: 104,236개 3D 포인트
- **3D Gaussian Splats**: 1,457,679개 스플랫
- **애니메이션 길이**: 312 프레임 (24fps 기준 13초)

## 프로젝트 구조

```
buildify-3dgs/
├── blender_colmap_3dgs/
│   ├── __init__.py
│   ├── colmap_parser.py          # COLMAP 데이터 파싱
│   ├── blender_animation.py      # Blender 카메라 애니메이션
│   └── gaussian_splatting.py     # 3DGS PLY 임포트 및 KIRI 연동
├── main.py                       # 메인 통합 스크립트
├── pyproject.toml               # 프로젝트 설정
└── README.md
```

## 주요 모듈

### COLMAPLoader
COLMAP binary 파일들을 파싱하고 Blender 좌표계로 변환합니다.

### BlenderCOLMAPIntegration
- 애니메이션 카메라 생성
- 포인트 클라우드 메쉬 생성
- 이미지 플레인 생성
- 씬 설정 자동화

### GaussianSplattingIntegration
- PLY 파일에서 Gaussian Splats 로드
- KIRI 3DGS Engine과의 연동
- COLMAP 데이터와 자동 정렬

## 시각화 컨트롤

통합이 완료되면 다음과 같이 사용할 수 있습니다:

- **SPACEBAR**: 카메라 애니메이션 재생/정지
- **NUM0**: 카메라 뷰로 전환
- **NUM7/NUM1/NUM3**: 위/앞/옆면 뷰
- **마우스 휠**: 줌 인/아웃
- **마우스 중간 버튼**: 뷰 회전

## 좌표계 변환

이 프로젝트는 COLMAP과 Blender 간의 좌표계 차이를 자동으로 처리합니다:

- **COLMAP**: Y-down, Z-forward
- **Blender**: Z-up, Y-forward

변환 매트릭스가 자동으로 적용되어 올바른 시각화를 제공합니다.

## 문제해결

### KIRI 3DGS Engine 연동 실패
```python
# KIRI 없이 수동 임포트 사용
main(colmap_path, ply_path, images_path, use_kiri=False)
```

### 메모리 부족
- 큰 포인트 클라우드의 경우 포인트 수를 제한할 수 있습니다
- `colmap_parser.py`에서 포인트 서브샘플링 추가 가능

### 좌표 정렬 문제
- `gaussian_splatting.py`의 `align_gaussian_splats_with_colmap()` 함수 수정
- ICP 알고리즘으로 더 정확한 정렬 가능

## 개발 환경

```bash
# 개발 의존성 설치
uv sync --dev

# 코드 포매팅
black .

# 타입 체크
mypy .
```

## 라이선스

MIT License
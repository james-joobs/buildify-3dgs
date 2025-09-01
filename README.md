# Buildify 3DGS - 3D Gaussian Splatting Framework

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![C++23](https://img.shields.io/badge/c%2B%2B-23-blue.svg)](https://en.cppreference.com/w/cpp/23)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 개요

Buildify 3DGS는 3D Gaussian Splatting을 위한 고성능 C++23 프레임워크로, Python 바인딩, Blender 통합, PyTorch 지원을 제공합니다. 현대적인 C++23 기능과 효율적인 Python API를 통해 3D 렌더링과 머신러닝 워크플로우를 원활하게 통합할 수 있습니다.

## 주요 기능

- **3D Gaussian Splatting**: 고품질 실시간 3D 렌더링
- **C++23 표준**: 최신 C++ 기능 활용 (concepts, ranges, std::expected 등)
- **Python 바인딩**: pybind11을 통한 완벽한 Python API 지원
- **Blender 통합**: Blender와의 원활한 통합으로 3D 콘텐츠 제작 지원
- **PyTorch 지원**: 딥러닝 워크플로우와의 통합
- **OpenGL 렌더러**: 하드웨어 가속 렌더링
- **모듈식 아키텍처**: 깔끔하고 확장 가능한 코드 구조

## 시스템 요구사항

- C++23 호환 컴파일러 (GCC 12+, Clang 15+, MSVC 2022+)
- CMake 3.20 이상
- Python 3.10 이상
- PyTorch 2.0+ (선택사항)
- Blender 3.0+ (선택사항)

## 설치

### Python 패키지로 설치

```bash
# 개발 환경 설정
pip install -e .

# 또는 빌드 후 설치
python setup.py install
```

### CMake로 직접 빌드

```bash
# 빌드 디렉토리 생성
mkdir build && cd build

# CMake 설정
cmake .. -DCMAKE_BUILD_TYPE=Release \
         -DWITH_PYTHON=ON \
         -DWITH_BLENDER=ON \
         -DWITH_PYTORCH=ON

# 빌드
make -j$(nproc)

# 테스트 실행 (선택사항)
ctest
```

### 빌드 옵션

- `WITH_PYTHON`: Python 바인딩 빌드 (기본값: ON)
- `WITH_BLENDER`: Blender 지원 포함 (기본값: ON)
- `WITH_PYTORCH`: PyTorch 통합 포함 (기본값: ON)
- `BUILD_TESTS`: 테스트 빌드 (기본값: ON)
- `BUILD_EXAMPLES`: 예제 빌드 (기본값: ON)

## 사용 예제

### Python에서 사용

```python
import buildify

# 엔진 초기화
engine = buildify.core.Engine()
engine.initialize()

# 씬 생성
scene = engine.create_scene("MainScene")

# 카메라 설정
camera = buildify.core.Camera("MainCamera")
camera.set_perspective(45.0, 16.0/9.0, 0.1, 1000.0)

# 카메라 위치 설정
transform = camera.get_transform()
transform.position = buildify.utils.Vector3(0, 5, 10)
camera.set_transform(transform)
camera.look_at(buildify.utils.Vector3(0, 0, 0))

scene.add_entity(camera)
scene.set_active_camera(camera)

# OpenGL 렌더러 설정
renderer = buildify.core.OpenGLRenderer()
target = buildify.core.RenderTarget()
target.width = 1920
target.height = 1080
target.samples = 4  # MSAA

# 업데이트 루프
def update_callback(delta_time):
    # 여기에 업데이트 로직 추가
    pass

engine.add_update_callback(update_callback)

# 렌더링 루프 시작
while True:
    engine.update(0.016667)  # 60 FPS
    # 렌더링 및 기타 작업
```

### C++에서 사용

```cpp
#include <buildify/buildify.hpp>

int main() {
    // 엔진 생성 및 초기화
    auto engine = std::make_unique<buildify::core::Engine>();
    engine->initialize();
    
    // 씬 생성
    auto scene = engine->createScene("MainScene");
    
    // 카메라 설정
    auto camera = std::make_shared<buildify::core::Camera>("MainCamera");
    camera->setPerspective(45.0f, 16.0f/9.0f, 0.1f, 1000.0f);
    
    // 렌더러 설정
    buildify::core::OpenGLRenderer renderer;
    buildify::core::RenderTarget target{
        .width = 1920,
        .height = 1080,
        .samples = 4
    };
    
    // 메인 루프
    while (engine->isRunning()) {
        engine->update(0.016667f);
        renderer.render(*scene, target);
    }
    
    engine->shutdown();
    return 0;
}
```

## 프로젝트 구조

```
buildify-3dgs/
├── include/buildify/     # C++ 헤더 파일
│   ├── core/             # 코어 엔진 컴포넌트
│   │   ├── engine.hpp
│   │   ├── renderer.hpp
│   │   └── scene.hpp
│   └── utils/            # 유틸리티 클래스
│       ├── math.hpp
│       └── logger.hpp
├── src/                  # C++ 소스 파일
│   ├── core/             # 코어 구현
│   └── utils/            # 유틸리티 구현
├── python/               # Python 바인딩
│   └── bindings.cpp     # pybind11 바인딩
├── buildify/             # Python 패키지
│   └── __init__.py
├── examples/             # 예제 코드
│   ├── basic_example.cpp
│   ├── interactive_demo.py
│   └── buildify_tutorial.ipynb
├── tests/                # 테스트 코드
└── CMakeLists.txt        # CMake 설정
```

## 예제 실행

### Python 데모
```bash
python examples/interactive_demo.py
```

### 벤치마크
```bash
python examples/benchmark.py
```

### Jupyter 노트북 튜토리얼
```bash
jupyter notebook examples/buildify_tutorial.ipynb
```

### C++ 예제
```bash
./build/bin/basic_example
./build/bin/blender_example  # Blender 지원 필요
./build/bin/pytorch_example  # PyTorch 지원 필요
```

## 테스트

```bash
# Python 테스트
python test_buildify.py

# C++ 테스트
cd build
ctest --verbose
```

## 개발

### 의존성 설치

```bash
# 개발 의존성
pip install -e ".[dev]"

# 전체 의존성
pip install torch numpy pybind11
```

### 코드 포맷팅

```bash
# Python 코드
black buildify/ examples/ tests/
ruff check buildify/

# C++ 코드
clang-format -i src/**/*.cpp include/**/*.hpp
```

## 기여하기

프로젝트에 기여하고 싶으시다면 Pull Request를 보내주세요. 다음 사항을 확인해 주세요:

1. 코드 스타일 가이드라인 준수
2. 테스트 작성 및 통과 확인
3. 문서 업데이트
4. 명확한 커밋 메시지 작성

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 문의

- 이슈: [GitHub Issues](https://github.com/yourusername/buildify-3dgs/issues)
- 이메일: your.email@example.com

## 감사의 말

이 프로젝트는 다음 오픈소스 프로젝트들을 활용합니다:
- [pybind11](https://github.com/pybind/pybind11) - Python 바인딩
- [PyTorch](https://pytorch.org/) - 딥러닝 프레임워크
- [Blender](https://www.blender.org/) - 3D 제작 도구
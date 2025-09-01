#pragma once

#include <memory>
#include <vector>
#include <array>

namespace buildify {

struct Gaussian {
    std::array<float, 3> position;
    std::array<float, 3> scale;
    std::array<float, 4> rotation;  // quaternion
    std::array<float, 4> color;     // RGBA
};

class Scene {
public:
    virtual ~Scene() = default;
    
    virtual void addGaussian(const Gaussian& gaussian) = 0;
    virtual size_t getGaussianCount() const = 0;
    virtual void exportTo3DGS(const std::string& filename) = 0;
    virtual float computeRenderingLoss() = 0;
    virtual std::vector<void*> parameters() = 0;
};

class Context {
public:
    Context();
    ~Context();
    
    void initialize();
    std::shared_ptr<Scene> createScene();
    
private:
    class Impl;
    std::unique_ptr<Impl> pImpl;
};

} // namespace buildify
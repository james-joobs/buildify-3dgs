#pragma once

#include <memory>
#include <torch/torch.h>
#include "buildify.h"

namespace buildify {

class PyTorchIntegration {
public:
    virtual ~PyTorchIntegration() = default;
    
    static std::unique_ptr<PyTorchIntegration> create();
    
    virtual void addGaussiansFromTensors(
        std::shared_ptr<Scene> scene,
        const torch::Tensor& positions,
        const torch::Tensor& scales,
        const torch::Tensor& rotations,
        const torch::Tensor& colors
    ) = 0;
    
    virtual torch::Tensor getPositionsTensor(const std::shared_ptr<Scene>& scene) = 0;
    virtual torch::Tensor getScalesTensor(const std::shared_ptr<Scene>& scene) = 0;
    virtual torch::Tensor getRotationsTensor(const std::shared_ptr<Scene>& scene) = 0;
    virtual torch::Tensor getColorsTensor(const std::shared_ptr<Scene>& scene) = 0;
};

} // namespace buildify
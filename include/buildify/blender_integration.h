#pragma once

#include <memory>
#include <string>
#include "buildify.h"

namespace buildify {

class BlenderIntegration {
public:
    virtual ~BlenderIntegration() = default;
    
    static std::unique_ptr<BlenderIntegration> create();
    
    virtual std::shared_ptr<Scene> importScene(const std::string& filename) = 0;
    virtual bool exportScene(const std::shared_ptr<Scene>& scene, const std::string& filename) = 0;
};

} // namespace buildify
#include <buildify/blender_integration.h>
#include <iostream>

namespace buildify {

class BlenderIntegrationImpl : public BlenderIntegration {
public:
    std::shared_ptr<Scene> importScene(const std::string& filename) override {
        std::cout << "Importing from Blender file: " << filename << std::endl;
        // TODO: Implement actual Blender import
        return nullptr;
    }
    
    bool exportScene(const std::shared_ptr<Scene>& scene, const std::string& filename) override {
        std::cout << "Exporting to Blender file: " << filename << std::endl;
        // TODO: Implement actual Blender export
        return false;
    }
};

std::unique_ptr<BlenderIntegration> BlenderIntegration::create() {
    return std::make_unique<BlenderIntegrationImpl>();
}

} // namespace buildify
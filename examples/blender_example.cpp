#include <iostream>
#include <buildify/buildify.h>
#include <buildify/blender_integration.h>

int main() {
    std::cout << "Buildify 3DGS Blender Integration Example" << std::endl;
    
    // Initialize Buildify with Blender support
    buildify::Context context;
    context.initialize();
    
    // Create a Blender integration instance
    auto blender = buildify::BlenderIntegration::create();
    
    // Import a scene from Blender format
    auto scene = blender->importScene("sample.blend");
    
    if (scene) {
        std::cout << "Successfully imported Blender scene" << std::endl;
        std::cout << "Scene contains " << scene->getGaussianCount() << " gaussians" << std::endl;
        
        // Export to 3DGS format
        scene->exportTo3DGS("output.ply");
        std::cout << "Exported to output.ply" << std::endl;
    } else {
        std::cerr << "Failed to import Blender scene" << std::endl;
    }
    
    return 0;
}
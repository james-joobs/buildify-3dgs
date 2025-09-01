#include <iostream>
#include <buildify/buildify.h>

int main() {
    std::cout << "Buildify 3DGS Basic Example" << std::endl;
    
    // Initialize Buildify
    buildify::Context context;
    context.initialize();
    
    // Create a simple 3D Gaussian Splatting scene
    auto scene = context.createScene();
    
    // Add some sample gaussians
    buildify::Gaussian g1;
    g1.position = {0.0f, 0.0f, 0.0f};
    g1.scale = {1.0f, 1.0f, 1.0f};
    g1.rotation = {0.0f, 0.0f, 0.0f, 1.0f};
    g1.color = {1.0f, 0.0f, 0.0f, 1.0f};
    
    scene->addGaussian(g1);
    
    std::cout << "Scene created with " << scene->getGaussianCount() << " gaussians" << std::endl;
    
    return 0;
}
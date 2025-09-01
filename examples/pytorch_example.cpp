#include <iostream>
#include <torch/torch.h>
#include <buildify/buildify.h>
#include <buildify/pytorch_integration.h>

int main() {
    std::cout << "Buildify 3DGS PyTorch Integration Example" << std::endl;
    
    // Initialize Buildify
    buildify::Context context;
    context.initialize();
    
    // Create a scene
    auto scene = context.createScene();
    
    // Create PyTorch tensors for gaussian parameters
    auto positions = torch::randn({100, 3});  // 100 gaussians, 3D positions
    auto scales = torch::ones({100, 3}) * 0.1f;
    auto rotations = torch::zeros({100, 4});
    rotations.select(1, 3).fill_(1.0f);  // Set w component to 1
    auto colors = torch::rand({100, 4});
    
    // Convert tensors to gaussians
    auto integration = buildify::PyTorchIntegration::create();
    integration->addGaussiansFromTensors(scene, positions, scales, rotations, colors);
    
    std::cout << "Created scene with " << scene->getGaussianCount() << " gaussians from PyTorch tensors" << std::endl;
    
    // Optimize gaussians using PyTorch
    auto optimizer = torch::optim::Adam(scene->parameters(), 0.01);
    
    for (int i = 0; i < 10; ++i) {
        optimizer.zero_grad();
        
        // Compute loss (simplified example)
        auto loss = scene->computeRenderingLoss();
        
        loss.backward();
        optimizer.step();
        
        std::cout << "Iteration " << i << ", Loss: " << loss.item<float>() << std::endl;
    }
    
    return 0;
}
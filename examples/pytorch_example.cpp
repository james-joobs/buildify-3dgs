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
    
    std::cout << "Added gaussians to scene from PyTorch tensors" << std::endl;
    
    // Get tensors back from the scene
    auto scene_positions = integration->getPositionsTensor(scene);
    auto scene_scales = integration->getScalesTensor(scene);
    auto scene_rotations = integration->getRotationsTensor(scene);
    auto scene_colors = integration->getColorsTensor(scene);
    
    // Make tensors require gradients for optimization
    scene_positions.set_requires_grad(true);
    scene_scales.set_requires_grad(true);
    scene_rotations.set_requires_grad(true);
    scene_colors.set_requires_grad(true);
    
    // Create optimizer with the tensors
    std::vector<torch::Tensor> parameters = {scene_positions, scene_scales, scene_rotations, scene_colors};
    auto optimizer = torch::optim::Adam(parameters, torch::optim::AdamOptions(0.01));
    
    for (int i = 0; i < 10; ++i) {
        optimizer.zero_grad();
        
        // Compute a simple loss (L2 norm of positions as example)
        auto loss = torch::mean(torch::pow(scene_positions, 2));
        
        loss.backward();
        optimizer.step();
        
        std::cout << "Iteration " << i << ", Loss: " << loss.item<float>() << std::endl;
    }
    
    return 0;
}
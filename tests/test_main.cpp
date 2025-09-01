#include <gtest/gtest.h>
#include <buildify/buildify.h>

// Test context initialization
TEST(BuildifyTest, ContextInitialization) {
    buildify::Context context;
    ASSERT_NO_THROW(context.initialize());
}

// Test scene creation
TEST(BuildifyTest, SceneCreation) {
    buildify::Context context;
    context.initialize();
    
    auto scene = context.createScene();
    ASSERT_NE(scene, nullptr);
    ASSERT_EQ(scene->getGaussianCount(), 0);
}

// Test gaussian addition
TEST(BuildifyTest, GaussianAddition) {
    buildify::Context context;
    context.initialize();
    
    auto scene = context.createScene();
    
    buildify::Gaussian g;
    g.position = {1.0f, 2.0f, 3.0f};
    g.scale = {0.5f, 0.5f, 0.5f};
    g.rotation = {0.0f, 0.0f, 0.0f, 1.0f};
    g.color = {1.0f, 0.0f, 0.0f, 1.0f};
    
    scene->addGaussian(g);
    ASSERT_EQ(scene->getGaussianCount(), 1);
}

// Test multiple gaussian operations
TEST(BuildifyTest, MultipleGaussians) {
    buildify::Context context;
    context.initialize();
    
    auto scene = context.createScene();
    
    // Add 100 gaussians
    for (int i = 0; i < 100; ++i) {
        buildify::Gaussian g;
        g.position = {float(i), 0.0f, 0.0f};
        g.scale = {1.0f, 1.0f, 1.0f};
        g.rotation = {0.0f, 0.0f, 0.0f, 1.0f};
        g.color = {1.0f, 1.0f, 1.0f, 1.0f};
        scene->addGaussian(g);
    }
    
    ASSERT_EQ(scene->getGaussianCount(), 100);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
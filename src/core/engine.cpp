#include "buildify/core/engine.hpp"
#include "buildify/core/scene.hpp"
#include "buildify/core/renderer.hpp"
#include "buildify/utils/logger.hpp"

#include <unordered_map>
#include <chrono>

namespace buildify::core {

struct Engine::Impl {
    std::unordered_map<std::string, std::shared_ptr<Scene>> scenes;
    std::shared_ptr<Scene> active_scene;
    std::unique_ptr<Renderer> renderer;
    std::chrono::steady_clock::time_point last_update_time;
};

Engine::Engine() : impl_(std::make_unique<Impl>()) {
    utils::log_info("Buildify Engine v{} initialized", "1.0.0");
}

Engine::~Engine() {
    if (running_) {
        shutdown();
    }
}

Engine::Engine(Engine&&) noexcept = default;
Engine& Engine::operator=(Engine&&) noexcept = default;

bool Engine::initialize(const std::string& config_path) {
    if (running_) {
        utils::log_warning("Engine already initialized");
        return true;
    }

    impl_->last_update_time = std::chrono::steady_clock::now();
    running_ = true;

    utils::log_info("Engine initialized successfully");
    return true;
}

void Engine::shutdown() {
    if (!running_) {
        return;
    }

    running_ = false;
    
    if (impl_->renderer) {
        impl_->renderer->shutdown();
    }

    impl_->scenes.clear();
    impl_->active_scene.reset();

    utils::log_info("Engine shutdown complete");
}

void Engine::update(double delta_time) {
    if (!running_) {
        return;
    }

    if (impl_->active_scene) {
        impl_->active_scene->update(delta_time);
    }

    for (const auto& callback : update_callbacks_) {
        callback(delta_time);
    }
}

void Engine::render() {
    if (!running_ || !impl_->renderer || !impl_->active_scene) {
        return;
    }

    impl_->renderer->begin_frame();
    impl_->renderer->render_scene(*impl_->active_scene);
    impl_->renderer->end_frame();
}

std::shared_ptr<Scene> Engine::create_scene(const std::string& name) {
    auto scene = std::make_shared<Scene>(name);
    impl_->scenes[name] = scene;
    
    if (!impl_->active_scene) {
        impl_->active_scene = scene;
    }

    utils::log_info("Created scene: {}", name);
    return scene;
}

std::shared_ptr<Scene> Engine::get_scene(const std::string& name) const {
    auto it = impl_->scenes.find(name);
    return (it != impl_->scenes.end()) ? it->second : nullptr;
}

void Engine::set_active_scene(std::shared_ptr<Scene> scene) {
    impl_->active_scene = scene;
    if (scene) {
        utils::log_info("Active scene set to: {}", scene->get_name());
    }
}

void Engine::set_renderer(std::unique_ptr<Renderer> renderer) {
    impl_->renderer = std::move(renderer);
}

Renderer* Engine::get_renderer() const {
    return impl_->renderer.get();
}

}
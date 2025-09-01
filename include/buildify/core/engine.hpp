#ifndef BUILDIFY_CORE_ENGINE_HPP
#define BUILDIFY_CORE_ENGINE_HPP

#include <memory>
#include <string>
#include <vector>
#include <functional>
#include <concepts>

namespace buildify::core {

class Scene;
class Renderer;

class Engine {
public:
    Engine();
    ~Engine();

    Engine(const Engine&) = delete;
    Engine& operator=(const Engine&) = delete;
    Engine(Engine&&) noexcept;
    Engine& operator=(Engine&&) noexcept;

    bool initialize(const std::string& config_path = "");
    void shutdown();

    void update(double delta_time);
    void render();

    std::shared_ptr<Scene> create_scene(const std::string& name);
    std::shared_ptr<Scene> get_scene(const std::string& name) const;
    void set_active_scene(std::shared_ptr<Scene> scene);

    void set_renderer(std::unique_ptr<Renderer> renderer);
    Renderer* get_renderer() const;

    template<typename T>
        requires std::invocable<T, double>
    void add_update_callback(T&& callback) {
        update_callbacks_.emplace_back(std::forward<T>(callback));
    }

    bool is_running() const { return running_; }
    void stop() { running_ = false; }

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
    
    bool running_ = false;
    std::vector<std::function<void(double)>> update_callbacks_;
};

}

#endif
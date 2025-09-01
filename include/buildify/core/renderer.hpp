#ifndef BUILDIFY_CORE_RENDERER_HPP
#define BUILDIFY_CORE_RENDERER_HPP

#include <memory>
#include <span>
#include <array>
#include <cstdint>

#ifdef WITH_PYTORCH
#include <torch/torch.h>
#endif

namespace buildify::core {

class Scene;

struct RenderTarget {
    std::uint32_t width;
    std::uint32_t height;
    std::uint32_t samples = 1;
    void* native_handle = nullptr;
};

class Renderer {
public:
    Renderer() = default;
    virtual ~Renderer() = default;

    virtual bool initialize(const RenderTarget& target) = 0;
    virtual void shutdown() = 0;

    virtual void begin_frame() = 0;
    virtual void end_frame() = 0;

    virtual void render_scene(const Scene& scene) = 0;

    virtual void set_viewport(std::uint32_t x, std::uint32_t y, 
                             std::uint32_t width, std::uint32_t height) = 0;

    virtual void clear(std::array<float, 4> color = {0.0f, 0.0f, 0.0f, 1.0f}) = 0;

#ifdef WITH_PYTORCH
    virtual torch::Tensor render_to_tensor(const Scene& scene) {
        return torch::empty({0});
    }
#endif

protected:
    RenderTarget target_;
};

class OpenGLRenderer : public Renderer {
public:
    OpenGLRenderer();
    ~OpenGLRenderer() override;

    bool initialize(const RenderTarget& target) override;
    void shutdown() override;

    void begin_frame() override;
    void end_frame() override;

    void render_scene(const Scene& scene) override;

    void set_viewport(std::uint32_t x, std::uint32_t y,
                     std::uint32_t width, std::uint32_t height) override;

    void clear(std::array<float, 4> color) override;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}

#endif
#include "buildify/core/renderer.hpp"
#include "buildify/core/scene.hpp"
#include "buildify/utils/logger.hpp"

#ifdef WITH_BLENDER
#include <GL/glew.h>
#endif

namespace buildify::core {

struct OpenGLRenderer::Impl {
    bool initialized = false;
#ifdef WITH_BLENDER
    GLuint framebuffer = 0;
    GLuint color_texture = 0;
    GLuint depth_renderbuffer = 0;
#endif
};

OpenGLRenderer::OpenGLRenderer() : impl_(std::make_unique<Impl>()) {}

OpenGLRenderer::~OpenGLRenderer() {
    if (impl_->initialized) {
        shutdown();
    }
}

bool OpenGLRenderer::initialize(const RenderTarget& target) {
    target_ = target;

#ifdef WITH_BLENDER
    GLenum err = glewInit();
    if (err != GLEW_OK) {
        utils::log_error("Failed to initialize GLEW: {}", reinterpret_cast<const char*>(glewGetErrorString(err)));
        return false;
    }

    glGenFramebuffers(1, &impl_->framebuffer);
    glBindFramebuffer(GL_FRAMEBUFFER, impl_->framebuffer);

    glGenTextures(1, &impl_->color_texture);
    glBindTexture(GL_TEXTURE_2D, impl_->color_texture);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, target.width, target.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, impl_->color_texture, 0);

    glGenRenderbuffers(1, &impl_->depth_renderbuffer);
    glBindRenderbuffer(GL_RENDERBUFFER, impl_->depth_renderbuffer);
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, target.width, target.height);
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, impl_->depth_renderbuffer);

    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) {
        utils::log_error("Framebuffer is not complete");
        return false;
    }

    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    
    glEnable(GL_DEPTH_TEST);
    glEnable(GL_CULL_FACE);
    glCullFace(GL_BACK);
    glFrontFace(GL_CCW);
#endif

    impl_->initialized = true;
    utils::log_info("OpenGL Renderer initialized ({}x{}, {} samples)", 
                    target.width, target.height, target.samples);
    return true;
}

void OpenGLRenderer::shutdown() {
    if (!impl_->initialized) {
        return;
    }

#ifdef WITH_BLENDER
    if (impl_->framebuffer) {
        glDeleteFramebuffers(1, &impl_->framebuffer);
    }
    if (impl_->color_texture) {
        glDeleteTextures(1, &impl_->color_texture);
    }
    if (impl_->depth_renderbuffer) {
        glDeleteRenderbuffers(1, &impl_->depth_renderbuffer);
    }
#endif

    impl_->initialized = false;
    utils::log_info("OpenGL Renderer shutdown");
}

void OpenGLRenderer::begin_frame() {
#ifdef WITH_BLENDER
    glBindFramebuffer(GL_FRAMEBUFFER, impl_->framebuffer);
#endif
}

void OpenGLRenderer::end_frame() {
#ifdef WITH_BLENDER
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
#endif
}

void OpenGLRenderer::render_scene(const Scene& scene) {
    auto camera = scene.get_active_camera();
    if (!camera) {
        utils::log_warning("No active camera in scene");
        return;
    }

#ifdef WITH_BLENDER
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
#endif
}

void OpenGLRenderer::set_viewport(std::uint32_t x, std::uint32_t y,
                                 std::uint32_t width, std::uint32_t height) {
#ifdef WITH_BLENDER
    glViewport(x, y, width, height);
#endif
}

void OpenGLRenderer::clear(std::array<float, 4> color) {
#ifdef WITH_BLENDER
    glClearColor(color[0], color[1], color[2], color[3]);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
#endif
}

}
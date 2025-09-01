#ifndef BUILDIFY_CORE_SCENE_HPP
#define BUILDIFY_CORE_SCENE_HPP

#include <memory>
#include <string>
#include <vector>
#include <optional>
#include <concepts>
#include <ranges>

#include "buildify/utils/math.hpp"

namespace buildify::core {

class Entity;
class Camera;
class Light;
class Mesh;

template<typename T>
concept SceneObject = std::derived_from<T, Entity>;

class Scene {
public:
    explicit Scene(const std::string& name);
    ~Scene();

    Scene(const Scene&) = delete;
    Scene& operator=(const Scene&) = delete;
    Scene(Scene&&) noexcept;
    Scene& operator=(Scene&&) noexcept;

    const std::string& get_name() const { return name_; }
    void set_name(const std::string& name) { name_ = name; }

    template<SceneObject T, typename... Args>
    std::shared_ptr<T> create_entity(Args&&... args) {
        auto entity = std::make_shared<T>(std::forward<Args>(args)...);
        add_entity(entity);
        return entity;
    }

    void add_entity(std::shared_ptr<Entity> entity);
    void remove_entity(std::shared_ptr<Entity> entity);
    
    std::shared_ptr<Entity> find_entity(const std::string& name) const;
    
    template<SceneObject T>
    std::vector<std::shared_ptr<T>> find_entities_of_type() const {
        std::vector<std::shared_ptr<T>> result;
        for (const auto& entity : entities_) {
            if (auto typed = std::dynamic_pointer_cast<T>(entity)) {
                result.push_back(typed);
            }
        }
        return result;
    }

    void set_active_camera(std::shared_ptr<Camera> camera);
    std::shared_ptr<Camera> get_active_camera() const;

    void update(double delta_time);

    auto get_entities() const { 
        return entities_ | std::views::all;
    }

    void load_from_file(const std::string& path);
    void save_to_file(const std::string& path) const;

#ifdef WITH_BLENDER
    void import_from_blender(const std::string& blend_file);
    void export_to_blender(const std::string& blend_file) const;
#endif

private:
    std::string name_;
    std::vector<std::shared_ptr<Entity>> entities_;
    std::shared_ptr<Camera> active_camera_;
    
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

class Entity {
public:
    explicit Entity(const std::string& name = "");
    virtual ~Entity() = default;

    const std::string& get_name() const { return name_; }
    void set_name(const std::string& name) { name_ = name; }

    const utils::Transform& get_transform() const { return transform_; }
    utils::Transform& get_transform() { return transform_; }
    void set_transform(const utils::Transform& transform) { transform_ = transform; }

    virtual void update(double delta_time) {}

protected:
    std::string name_;
    utils::Transform transform_;
};

class Camera : public Entity {
public:
    Camera(const std::string& name = "Camera");

    void set_perspective(float fov, float aspect_ratio, float near, float far);
    void set_orthographic(float left, float right, float bottom, float top, float near, float far);

    utils::Matrix4<float> get_view_matrix() const;
    utils::Matrix4<float> get_projection_matrix() const;

    void look_at(const utils::Vector3<float>& target, const utils::Vector3<float>& up = {0, 1, 0});

private:
    enum class ProjectionType { Perspective, Orthographic };
    ProjectionType projection_type_ = ProjectionType::Perspective;
    
    float fov_ = 45.0f;
    float aspect_ratio_ = 16.0f / 9.0f;
    float near_ = 0.1f;
    float far_ = 1000.0f;
    
    float ortho_left_ = -1.0f;
    float ortho_right_ = 1.0f;
    float ortho_bottom_ = -1.0f;
    float ortho_top_ = 1.0f;
};

}

#endif
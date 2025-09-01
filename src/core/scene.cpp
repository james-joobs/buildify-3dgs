#include "buildify/core/scene.hpp"
#include "buildify/utils/logger.hpp"

#include <algorithm>
#include <fstream>

namespace buildify::core {

struct Scene::Impl {
};

Scene::Scene(const std::string& name) 
    : name_(name), impl_(std::make_unique<Impl>()) {
    utils::log_debug("Scene created: {}", name);
}

Scene::~Scene() = default;
Scene::Scene(Scene&&) noexcept = default;
Scene& Scene::operator=(Scene&&) noexcept = default;

void Scene::add_entity(std::shared_ptr<Entity> entity) {
    entities_.push_back(entity);
    utils::log_debug("Entity '{}' added to scene '{}'", entity->get_name(), name_);
}

void Scene::remove_entity(std::shared_ptr<Entity> entity) {
    auto it = std::find(entities_.begin(), entities_.end(), entity);
    if (it != entities_.end()) {
        entities_.erase(it);
        utils::log_debug("Entity '{}' removed from scene '{}'", entity->get_name(), name_);
    }
}

std::shared_ptr<Entity> Scene::find_entity(const std::string& name) const {
    auto it = std::find_if(entities_.begin(), entities_.end(),
        [&name](const auto& entity) { return entity->get_name() == name; });
    
    return (it != entities_.end()) ? *it : nullptr;
}

void Scene::set_active_camera(std::shared_ptr<Camera> camera) {
    active_camera_ = camera;
}

std::shared_ptr<Camera> Scene::get_active_camera() const {
    return active_camera_;
}

void Scene::update(double delta_time) {
    for (auto& entity : entities_) {
        entity->update(delta_time);
    }
}

void Scene::load_from_file(const std::string& path) {
    utils::log_info("Loading scene from: {}", path);
}

void Scene::save_to_file(const std::string& path) const {
    utils::log_info("Saving scene to: {}", path);
}

#ifdef WITH_BLENDER
void Scene::import_from_blender(const std::string& blend_file) {
    utils::log_info("Importing from Blender file: {}", blend_file);
}

void Scene::export_to_blender(const std::string& blend_file) const {
    utils::log_info("Exporting to Blender file: {}", blend_file);
}
#endif

Entity::Entity(const std::string& name) : name_(name) {}

Camera::Camera(const std::string& name) : Entity(name) {}

void Camera::set_perspective(float fov, float aspect_ratio, float near, float far) {
    projection_type_ = ProjectionType::Perspective;
    fov_ = fov;
    aspect_ratio_ = aspect_ratio;
    near_ = near;
    far_ = far;
}

void Camera::set_orthographic(float left, float right, float bottom, float top, float near, float far) {
    projection_type_ = ProjectionType::Orthographic;
    ortho_left_ = left;
    ortho_right_ = right;
    ortho_bottom_ = bottom;
    ortho_top_ = top;
    near_ = near;
    far_ = far;
}

utils::Matrix4<float> Camera::get_view_matrix() const {
    auto& t = transform_;
    auto pos = t.position;
    auto forward = t.rotation.to_matrix() * utils::Vector4<float>(0, 0, -1, 0);
    auto up = t.rotation.to_matrix() * utils::Vector4<float>(0, 1, 0, 0);
    
    utils::Vector3<float> f(forward.x, forward.y, forward.z);
    utils::Vector3<float> u(up.x, up.y, up.z);
    utils::Vector3<float> r = f.cross(u).normalized();
    u = r.cross(f).normalized();

    utils::Matrix4<float> view;
    view.m[0][0] = r.x; view.m[0][1] = r.y; view.m[0][2] = r.z; view.m[0][3] = -r.dot(pos);
    view.m[1][0] = u.x; view.m[1][1] = u.y; view.m[1][2] = u.z; view.m[1][3] = -u.dot(pos);
    view.m[2][0] = -f.x; view.m[2][1] = -f.y; view.m[2][2] = -f.z; view.m[2][3] = f.dot(pos);
    view.m[3][0] = 0; view.m[3][1] = 0; view.m[3][2] = 0; view.m[3][3] = 1;

    return view;
}

utils::Matrix4<float> Camera::get_projection_matrix() const {
    if (projection_type_ == ProjectionType::Perspective) {
        return utils::Matrix4<float>::perspective(fov_, aspect_ratio_, near_, far_);
    } else {
        utils::Matrix4<float> ortho;
        ortho.m[0][0] = 2.0f / (ortho_right_ - ortho_left_);
        ortho.m[1][1] = 2.0f / (ortho_top_ - ortho_bottom_);
        ortho.m[2][2] = -2.0f / (far_ - near_);
        ortho.m[0][3] = -(ortho_right_ + ortho_left_) / (ortho_right_ - ortho_left_);
        ortho.m[1][3] = -(ortho_top_ + ortho_bottom_) / (ortho_top_ - ortho_bottom_);
        ortho.m[2][3] = -(far_ + near_) / (far_ - near_);
        return ortho;
    }
}

void Camera::look_at(const utils::Vector3<float>& target, const utils::Vector3<float>& up) {
    utils::Vector3<float> forward = (target - transform_.position).normalized();
    utils::Vector3<float> right = forward.cross(up).normalized();
    utils::Vector3<float> new_up = right.cross(forward);

    utils::Matrix4<float> rotation_matrix;
    rotation_matrix.m[0][0] = right.x;
    rotation_matrix.m[0][1] = right.y;
    rotation_matrix.m[0][2] = right.z;
    rotation_matrix.m[1][0] = new_up.x;
    rotation_matrix.m[1][1] = new_up.y;
    rotation_matrix.m[1][2] = new_up.z;
    rotation_matrix.m[2][0] = -forward.x;
    rotation_matrix.m[2][1] = -forward.y;
    rotation_matrix.m[2][2] = -forward.z;
}

}
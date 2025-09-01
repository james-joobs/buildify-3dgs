#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/numpy.h>

#include "buildify/buildify.hpp"

#ifdef WITH_PYTORCH
#include <torch/extension.h>
#endif

namespace py = pybind11;
using namespace buildify;

PYBIND11_MODULE(pybuildify, m) {
    m.doc() = "Buildify 3D Gaussian Splatting Python bindings";

    m.attr("__version__") = VERSION;

    py::module_ utils = m.def_submodule("utils", "Utility functions and classes");
    
    py::class_<utils::Vector3<float>>(utils, "Vector3")
        .def(py::init<>())
        .def(py::init<float, float, float>())
        .def_readwrite("x", &utils::Vector3<float>::x)
        .def_readwrite("y", &utils::Vector3<float>::y)
        .def_readwrite("z", &utils::Vector3<float>::z)
        .def("__add__", &utils::Vector3<float>::operator+)
        .def("__sub__", &utils::Vector3<float>::operator-)
        .def("__mul__", &utils::Vector3<float>::operator*)
        .def("dot", &utils::Vector3<float>::dot)
        .def("cross", &utils::Vector3<float>::cross)
        .def("length", &utils::Vector3<float>::length)
        .def("normalized", &utils::Vector3<float>::normalized)
        .def("__repr__", [](const utils::Vector3<float>& v) {
            return std::format("Vector3({}, {}, {})", v.x, v.y, v.z);
        });

    py::class_<utils::Transform>(utils, "Transform")
        .def(py::init<>())
        .def_readwrite("position", &utils::Transform::position)
        .def_readwrite("rotation", &utils::Transform::rotation)
        .def_readwrite("scale", &utils::Transform::scale)
        .def("to_matrix", &utils::Transform::to_matrix);

    py::class_<utils::Quaternion<float>>(utils, "Quaternion")
        .def(py::init<>())
        .def(py::init<float, float, float, float>())
        .def_readwrite("x", &utils::Quaternion<float>::x)
        .def_readwrite("y", &utils::Quaternion<float>::y)
        .def_readwrite("z", &utils::Quaternion<float>::z)
        .def_readwrite("w", &utils::Quaternion<float>::w)
        .def_static("from_axis_angle", &utils::Quaternion<float>::from_axis_angle)
        .def("to_matrix", &utils::Quaternion<float>::to_matrix);

    py::class_<utils::Matrix4<float>>(utils, "Matrix4")
        .def(py::init<>())
        .def_static("identity", &utils::Matrix4<float>::identity)
        .def_static("translation", &utils::Matrix4<float>::translation)
        .def_static("rotation_x", &utils::Matrix4<float>::rotation_x)
        .def_static("rotation_y", &utils::Matrix4<float>::rotation_y)
        .def_static("rotation_z", &utils::Matrix4<float>::rotation_z)
        .def_static("scale", &utils::Matrix4<float>::scale)
        .def_static("perspective", &utils::Matrix4<float>::perspective)
        .def("__mul__", static_cast<utils::Matrix4<float>(utils::Matrix4<float>::*)(const utils::Matrix4<float>&) const>(&utils::Matrix4<float>::operator*));

    py::enum_<utils::LogLevel>(utils, "LogLevel")
        .value("Trace", utils::LogLevel::Trace)
        .value("Debug", utils::LogLevel::Debug)
        .value("Info", utils::LogLevel::Info)
        .value("Warning", utils::LogLevel::Warning)
        .value("Error", utils::LogLevel::Error)
        .value("Critical", utils::LogLevel::Critical);

    utils.def("set_log_level", [](utils::LogLevel level) {
        utils::Logger::instance().set_level(level);
    });

    py::module_ core = m.def_submodule("core", "Core engine classes");

    py::class_<core::Engine>(core, "Engine")
        .def(py::init<>())
        .def("initialize", &core::Engine::initialize, py::arg("config_path") = "")
        .def("shutdown", &core::Engine::shutdown)
        .def("update", &core::Engine::update)
        .def("render", &core::Engine::render)
        .def("create_scene", &core::Engine::create_scene)
        .def("get_scene", &core::Engine::get_scene)
        .def("set_active_scene", &core::Engine::set_active_scene)
        .def("is_running", &core::Engine::is_running)
        .def("stop", &core::Engine::stop)
        .def("add_update_callback", [](core::Engine& engine, py::function callback) {
            engine.add_update_callback([callback](double dt) {
                py::gil_scoped_acquire acquire;
                callback(dt);
            });
        });

    py::class_<core::Entity, std::shared_ptr<core::Entity>>(core, "Entity")
        .def(py::init<const std::string&>(), py::arg("name") = "")
        .def("get_name", &core::Entity::get_name)
        .def("set_name", &core::Entity::set_name)
        .def("get_transform", static_cast<const utils::Transform&(core::Entity::*)() const>(&core::Entity::get_transform), py::return_value_policy::reference)
        .def("set_transform", &core::Entity::set_transform)
        .def("update", &core::Entity::update);

    py::class_<core::Camera, core::Entity, std::shared_ptr<core::Camera>>(core, "Camera")
        .def(py::init<const std::string&>(), py::arg("name") = "Camera")
        .def("set_perspective", &core::Camera::set_perspective)
        .def("set_orthographic", &core::Camera::set_orthographic)
        .def("get_view_matrix", &core::Camera::get_view_matrix)
        .def("get_projection_matrix", &core::Camera::get_projection_matrix)
        .def("look_at", &core::Camera::look_at, py::arg("target"), py::arg("up") = utils::Vector3<float>{0, 1, 0});

    py::class_<core::Scene, std::shared_ptr<core::Scene>>(core, "Scene")
        .def(py::init<const std::string&>())
        .def("get_name", &core::Scene::get_name)
        .def("set_name", &core::Scene::set_name)
        .def("add_entity", &core::Scene::add_entity)
        .def("remove_entity", &core::Scene::remove_entity)
        .def("find_entity", &core::Scene::find_entity)
        .def("set_active_camera", &core::Scene::set_active_camera)
        .def("get_active_camera", &core::Scene::get_active_camera)
        .def("update", &core::Scene::update)
        .def("load_from_file", &core::Scene::load_from_file)
        .def("save_to_file", &core::Scene::save_to_file)
#ifdef WITH_BLENDER
        .def("import_from_blender", &core::Scene::import_from_blender)
        .def("export_to_blender", &core::Scene::export_to_blender)
#endif
        ;

    py::class_<core::RenderTarget>(core, "RenderTarget")
        .def(py::init<>())
        .def_readwrite("width", &core::RenderTarget::width)
        .def_readwrite("height", &core::RenderTarget::height)
        .def_readwrite("samples", &core::RenderTarget::samples);

    py::class_<core::Renderer>(core, "Renderer");

    py::class_<core::OpenGLRenderer, core::Renderer>(core, "OpenGLRenderer")
        .def(py::init<>())
        .def("initialize", &core::OpenGLRenderer::initialize)
        .def("shutdown", &core::OpenGLRenderer::shutdown)
        .def("begin_frame", &core::OpenGLRenderer::begin_frame)
        .def("end_frame", &core::OpenGLRenderer::end_frame)
        .def("render_scene", &core::OpenGLRenderer::render_scene)
        .def("set_viewport", &core::OpenGLRenderer::set_viewport)
        .def("clear", &core::OpenGLRenderer::clear, py::arg("color") = std::array<float, 4>{0.0f, 0.0f, 0.0f, 1.0f});

#ifdef WITH_PYTORCH
    m.def("render_to_tensor", [](core::Renderer* renderer, const core::Scene& scene) {
        return renderer->render_to_tensor(scene);
    }, "Render scene to PyTorch tensor");
#endif
}
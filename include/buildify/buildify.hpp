#ifndef BUILDIFY_HPP
#define BUILDIFY_HPP

#include <cstdint>
#include <string>
#include <string_view>

namespace buildify {

constexpr std::string_view VERSION = "1.0.0";
constexpr std::uint32_t VERSION_MAJOR = 1;
constexpr std::uint32_t VERSION_MINOR = 0;
constexpr std::uint32_t VERSION_PATCH = 0;

}

#include "buildify/core/engine.hpp"
#include "buildify/core/renderer.hpp"
#include "buildify/core/scene.hpp"
#include "buildify/utils/math.hpp"
#include "buildify/utils/logger.hpp"

#endif
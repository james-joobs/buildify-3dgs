#ifndef BUILDIFY_UTILS_MATH_HPP
#define BUILDIFY_UTILS_MATH_HPP

#include <cmath>
#include <array>
#include <numbers>
#include <algorithm>
#include <concepts>

namespace buildify::utils {

template<typename T>
concept Arithmetic = std::integral<T> || std::floating_point<T>;

template<Arithmetic T = float>
struct Vector3 {
    T x, y, z;

    constexpr Vector3() : x(0), y(0), z(0) {}
    constexpr Vector3(T x, T y, T z) : x(x), y(y), z(z) {}

    Vector3 operator+(const Vector3& other) const {
        return Vector3(x + other.x, y + other.y, z + other.z);
    }

    Vector3 operator-(const Vector3& other) const {
        return Vector3(x - other.x, y - other.y, z - other.z);
    }

    Vector3 operator*(T scalar) const {
        return Vector3(x * scalar, y * scalar, z * scalar);
    }

    T dot(const Vector3& other) const {
        return x * other.x + y * other.y + z * other.z;
    }

    Vector3 cross(const Vector3& other) const {
        return Vector3(
            y * other.z - z * other.y,
            z * other.x - x * other.z,
            x * other.y - y * other.x
        );
    }

    T length() const {
        return std::sqrt(x * x + y * y + z * z);
    }

    Vector3 normalized() const {
        T len = length();
        return len > 0 ? (*this) * (1 / len) : Vector3();
    }
};

template<Arithmetic T = float>
struct Vector4 {
    T x, y, z, w;

    constexpr Vector4() : x(0), y(0), z(0), w(0) {}
    constexpr Vector4(T x, T y, T z, T w) : x(x), y(y), z(z), w(w) {}
    constexpr Vector4(const Vector3<T>& v3, T w) : x(v3.x), y(v3.y), z(v3.z), w(w) {}
};

template<Arithmetic T = float>
struct Matrix4 {
    std::array<std::array<T, 4>, 4> m;

    constexpr Matrix4() : m{} {
        for (int i = 0; i < 4; ++i) {
            m[i][i] = 1;
        }
    }

    static Matrix4 identity() {
        return Matrix4();
    }

    static Matrix4 translation(const Vector3<T>& v) {
        Matrix4 result;
        result.m[0][3] = v.x;
        result.m[1][3] = v.y;
        result.m[2][3] = v.z;
        return result;
    }

    static Matrix4 rotation_x(T angle) {
        Matrix4 result;
        T c = std::cos(angle);
        T s = std::sin(angle);
        result.m[1][1] = c;
        result.m[1][2] = -s;
        result.m[2][1] = s;
        result.m[2][2] = c;
        return result;
    }

    static Matrix4 rotation_y(T angle) {
        Matrix4 result;
        T c = std::cos(angle);
        T s = std::sin(angle);
        result.m[0][0] = c;
        result.m[0][2] = s;
        result.m[2][0] = -s;
        result.m[2][2] = c;
        return result;
    }

    static Matrix4 rotation_z(T angle) {
        Matrix4 result;
        T c = std::cos(angle);
        T s = std::sin(angle);
        result.m[0][0] = c;
        result.m[0][1] = -s;
        result.m[1][0] = s;
        result.m[1][1] = c;
        return result;
    }

    static Matrix4 scale(const Vector3<T>& v) {
        Matrix4 result;
        result.m[0][0] = v.x;
        result.m[1][1] = v.y;
        result.m[2][2] = v.z;
        return result;
    }

    static Matrix4 perspective(T fov, T aspect, T near, T far) {
        Matrix4 result{};
        T tan_half_fov = std::tan(fov * 0.5f * std::numbers::pi_v<T> / 180.0f);
        
        result.m[0][0] = 1.0f / (aspect * tan_half_fov);
        result.m[1][1] = 1.0f / tan_half_fov;
        result.m[2][2] = -(far + near) / (far - near);
        result.m[2][3] = -(2.0f * far * near) / (far - near);
        result.m[3][2] = -1.0f;
        result.m[3][3] = 0.0f;
        
        return result;
    }

    Matrix4 operator*(const Matrix4& other) const {
        Matrix4 result{};
        for (int i = 0; i < 4; ++i) {
            for (int j = 0; j < 4; ++j) {
                result.m[i][j] = 0;
                for (int k = 0; k < 4; ++k) {
                    result.m[i][j] += m[i][k] * other.m[k][j];
                }
            }
        }
        return result;
    }

    Vector4<T> operator*(const Vector4<T>& v) const {
        return Vector4<T>(
            m[0][0] * v.x + m[0][1] * v.y + m[0][2] * v.z + m[0][3] * v.w,
            m[1][0] * v.x + m[1][1] * v.y + m[1][2] * v.z + m[1][3] * v.w,
            m[2][0] * v.x + m[2][1] * v.y + m[2][2] * v.z + m[2][3] * v.w,
            m[3][0] * v.x + m[3][1] * v.y + m[3][2] * v.z + m[3][3] * v.w
        );
    }
};

template<Arithmetic T = float>
struct Quaternion {
    T x, y, z, w;

    constexpr Quaternion() : x(0), y(0), z(0), w(1) {}
    constexpr Quaternion(T x, T y, T z, T w) : x(x), y(y), z(z), w(w) {}

    static Quaternion from_axis_angle(const Vector3<T>& axis, T angle) {
        T half_angle = angle * 0.5f;
        T s = std::sin(half_angle);
        return Quaternion(
            axis.x * s,
            axis.y * s,
            axis.z * s,
            std::cos(half_angle)
        );
    }

    Matrix4<T> to_matrix() const {
        Matrix4<T> result;
        
        T xx = x * x;
        T xy = x * y;
        T xz = x * z;
        T xw = x * w;
        T yy = y * y;
        T yz = y * z;
        T yw = y * w;
        T zz = z * z;
        T zw = z * w;

        result.m[0][0] = 1 - 2 * (yy + zz);
        result.m[0][1] = 2 * (xy - zw);
        result.m[0][2] = 2 * (xz + yw);
        
        result.m[1][0] = 2 * (xy + zw);
        result.m[1][1] = 1 - 2 * (xx + zz);
        result.m[1][2] = 2 * (yz - xw);
        
        result.m[2][0] = 2 * (xz - yw);
        result.m[2][1] = 2 * (yz + xw);
        result.m[2][2] = 1 - 2 * (xx + yy);

        return result;
    }
};

struct Transform {
    Vector3<float> position;
    Quaternion<float> rotation;
    Vector3<float> scale{1, 1, 1};

    Matrix4<float> to_matrix() const {
        return Matrix4<float>::translation(position) * 
               rotation.to_matrix() * 
               Matrix4<float>::scale(scale);
    }
};

// Type aliases for common types
using Vector3f = Vector3<float>;
using Vector4f = Vector4<float>;
using Matrix4f = Matrix4<float>;
using Quaternionf = Quaternion<float>;

}

#endif
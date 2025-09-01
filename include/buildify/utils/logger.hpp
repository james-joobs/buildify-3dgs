#ifndef BUILDIFY_UTILS_LOGGER_HPP
#define BUILDIFY_UTILS_LOGGER_HPP

#include <string>
#include <format>
#include <iostream>
#include <chrono>
#include <source_location>

namespace buildify::utils {

enum class LogLevel {
    Trace,
    Debug,
    Info,
    Warning,
    Error,
    Critical
};

class Logger {
public:
    static Logger& instance() {
        static Logger logger;
        return logger;
    }

    void set_level(LogLevel level) { level_ = level; }
    LogLevel get_level() const { return level_; }

    template<typename... Args>
    void log(LogLevel level, std::format_string<Args...> fmt, Args&&... args) {
        if (level < level_) return;

        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        
        std::string message = std::format(fmt, std::forward<Args>(args)...);
        
        std::cout << std::format("[{:%Y-%m-%d %H:%M:%S}] [{}] {}\n",
                                 std::chrono::floor<std::chrono::seconds>(now),
                                 level_to_string(level),
                                 message);
    }

private:
    Logger() = default;
    LogLevel level_ = LogLevel::Info;

    static constexpr const char* level_to_string(LogLevel level) {
        switch (level) {
            case LogLevel::Trace: return "TRACE";
            case LogLevel::Debug: return "DEBUG";
            case LogLevel::Info: return "INFO";
            case LogLevel::Warning: return "WARN";
            case LogLevel::Error: return "ERROR";
            case LogLevel::Critical: return "CRITICAL";
        }
        return "UNKNOWN";
    }
};

template<typename... Args>
void log_trace(std::format_string<Args...> fmt, Args&&... args) {
    Logger::instance().log(LogLevel::Trace, fmt, std::forward<Args>(args)...);
}

template<typename... Args>
void log_debug(std::format_string<Args...> fmt, Args&&... args) {
    Logger::instance().log(LogLevel::Debug, fmt, std::forward<Args>(args)...);
}

template<typename... Args>
void log_info(std::format_string<Args...> fmt, Args&&... args) {
    Logger::instance().log(LogLevel::Info, fmt, std::forward<Args>(args)...);
}

template<typename... Args>
void log_warning(std::format_string<Args...> fmt, Args&&... args) {
    Logger::instance().log(LogLevel::Warning, fmt, std::forward<Args>(args)...);
}

template<typename... Args>
void log_error(std::format_string<Args...> fmt, Args&&... args) {
    Logger::instance().log(LogLevel::Error, fmt, std::forward<Args>(args)...);
}

template<typename... Args>
void log_critical(std::format_string<Args...> fmt, Args&&... args) {
    Logger::instance().log(LogLevel::Critical, fmt, std::forward<Args>(args)...);
}

}

#endif
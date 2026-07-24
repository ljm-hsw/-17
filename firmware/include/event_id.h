#pragma once

#include <array>
#include <cstdint>
#include <string>

#ifdef ARDUINO
#include <Arduino.h>
String makeEventId();
#endif

std::string formatEventId(const std::array<uint32_t, 4>& words);

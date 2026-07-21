#include <cstdio>

#include "event_id.h"

#ifdef ARDUINO
#include <esp_system.h>
#endif

std::string formatEventId(const std::array<uint32_t, 4>& words) {
  char value[33];
  for (int index = 0; index < 4; ++index) {
    std::snprintf(value + index * 8, 9, "%08lx", static_cast<unsigned long>(words[index]));
  }
  value[32] = '\0';
  return std::string(value);
}

#ifdef ARDUINO
String makeEventId() {
  const std::array<uint32_t, 4> words = {esp_random(), esp_random(), esp_random(), esp_random()};
  return String(formatEventId(words).c_str());
}
#endif

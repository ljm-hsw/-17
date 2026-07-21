#include <array>
#include <string>

#include <unity.h>

#include "event_id.h"

void test_event_id_is_32_lowercase_hex_characters() {
  const std::array<uint32_t, 4> words = {0x01234567, 0x89abcdef, 0x00000001, 0xffffffff};
  const std::string value = formatEventId(words);

  TEST_ASSERT_EQUAL_UINT32(32, value.size());
  TEST_ASSERT_EQUAL_STRING("0123456789abcdef00000001ffffffff", value.c_str());
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_event_id_is_32_lowercase_hex_characters);
  return UNITY_END();
}

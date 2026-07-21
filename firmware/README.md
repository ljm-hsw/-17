# ESP32 设备端

设备代码使用 Arduino Framework。为保证团队依赖和 CI 可复现，PlatformIO 是标准构建入口。

```bash
pio test -e native
pio run -e esp32dev
pio run -e esp32dev --target upload
pio device monitor
```

复制 `include/config.example.h` 为 `include/config.h` 并仅在本机填写凭据。`config.h` 不得提交。

当前编译基线是通用 `esp32dev`。确认实际 ESP32 板型后，须通过独立 PR 修改 `board`，并附一次真实烧录结果。

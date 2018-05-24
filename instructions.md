get firmware

open terminal:

git clone https://github.com/loboris/MicroPython_ESP32_psRAM_LoBo.git

in terminal navigate to dir "MicroPython_BUILD"

type:
./BUILD.sh menuconfig

1. give board a name (BoardName)

set to yes (y)
micropython ->
- system settings ->
  - use both cores
  - enable webServer

- modules ->
  - enable framebuffer
  - use WebSocketS

./BUILD.sh clean

./BUILD.sh
./BUILD.sh flash


wiki: https://github.com/loboris/MicroPython_ESP32_psRAM_LoBo/wiki

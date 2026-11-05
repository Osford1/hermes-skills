# Taobao Term Mapping (grow with every project)

Formula: `[中文名] [关键规格]`. Append `模块`/`开发板`/`套装` as needed. Prefer queries that surface 天猫/品牌店 stock.

| English / part | Taobao query |
|---|---|
| ESP32 dev board | `ESP32 开发板 WROOM-32` |
| ESP32-C3 | `ESP32-C3 开发板` |
| ESP8266 / NodeMCU | `ESP8266 NodeMcu 开发板` |
| Raspberry Pi Pico / RP2040 | `RP2040 Pico 开发板` |
| Arduino Nano | `Arduino Nano CH340` |
| NEMA17 stepper | `42步进电机 42BYGH` |
| NEMA23 stepper | `57步进电机` |
| A4988 driver | `A4988 步进驱动模块` |
| DRV8825 driver | `DRV8825 驱动模块` |
| TMC2208 / TMC2209 | `TMC2208 静音驱动模块` / `TMC2209 步进驱动` |
| TB6600 | `TB6600 步进驱动器` |
| 0.96" OLED SSD1306 | `0.96寸 OLED 模块 SSD1306 I2C` |
| 1.3" OLED SH1106 | `1.3寸 OLED 模块 SH1106` |
| TFT SPI screen | `1.8寸 TFT 液晶屏 SPI` |
| MAX98357A I2S amp | `MAX98357A I2S 功放模块` |
| PAM8403 amp | `PAM8403 功放模块` |
| MPU6050 IMU | `MPU6050 六轴模块` |
| HC-SR04 | `HC-SR04 超声波模块` |
| DHT22 | `DHT22 温湿度传感器` |
| MicroSD module | `MicroSD 卡模块 SPI` |
| LM2596 buck | `LM2596 降压模块` |
| MP1584 buck | `MP1584 降压模块` |
| XL4015 buck | `XL4015 降压模块` |
| MT3608 boost | `MT3608 升压模块` |
| XT60 connector | `XT60 插头 公母` |
| JST-XH connectors | `JST-XH 2.54 线束` |
| Dupont wires | `杜邦线 公对母 40cm` |
| Breadboard 830 | `面包板 830孔` |
| 5V PSU | `5V 电源适配器 3A` |
| 12V / 24V PSU | `12V 开关电源` / `24V 开关电源` |
| Mean Well PSU | `明纬 电源` |
| SG90 servo | `SG90 舵机` |
| MG996R servo | `MG996R 舵机 金属` |
| 2020 extrusion | `2020铝型材 欧标` |
| 2020 T-nut | `2020 T型螺母` |
| GT2 belt 6mm | `GT2 同步带 6mm` |
| GT2 pulley 20T | `GT2 同步轮 20齿 5mm` |
| T8 leadscrew | `T8 丝杆` |
| T8 nut | `T8 丝杆螺母 铜` |
| 8mm linear rod | `光轴 8mm` |
| LM8UU bearing | `LM8UU 直线轴承` |
| 608 bearing | `608 轴承` |
| M3 hardware kit | `M3 螺丝螺母套装` |
| M3 brass standoff | `铜柱 M3 母对母` |
| M3 heat-set insert | `M3 热熔铜螺母 嵌件` |
| BLTouch | `BLTouch 探针` |
| NTC 100k thermistor | `NTC 100K 热敏电阻` |
| heater cartridge | `3D打印 加热棒 12V` |
| 5015 blower fan | `5015 鼓风机 24V` |
| relay module | `继电器模块 5V 1路` |
| USB-C breakout | `Type-C 母座 转接板` |
| beam-splitter cube (pepper's ghost) | `分光棱镜 半透半反` |
| acrylic sheet | `亚克力板 3mm 透明` |
| laser cut service | `亚克力激光切割 定制` |
| 3D print service | `3D打印 定制 服务` |

## Patterns
- Unknown part → search the category + form factor (e.g. `DC-DC 降压 5A 模块`).
- Kit check: search `<project name> 套件` / `全套散件` and compare vs sum of parts × 1.2.
- Clone/quality judgment: MCUs & sensors fine as clones; power paths (PSU, battery, fuses) want branded (明纬, 绿联-style) — per quality policy.

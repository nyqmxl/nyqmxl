#include <Arduino.h>
#include <ArduinoJson.h>

// HID 键盘按键值定义（部分）
#define KEY_NULL 0x00           // 无键
#define KEY_LEFT_CONTROL 0x80   // 左控制键
#define KEY_LEFT_SHIFT 0x81     // 左Shift键
#define KEY_LEFT_ALT 0x82       // 左Alt键
#define KEY_LEFT_GUI 0x83       // 左GUI键
#define KEY_RIGHT_CONTROL 0x84  // 右控制键
#define KEY_RIGHT_SHIFT 0x85    // 右Shift键
#define KEY_RIGHT_ALT 0x86      // 右Alt键
#define KEY_RIGHT_GUI 0x87      // 右GUI键
#define KEY_UP_ARROW 0xDA       // 上箭头
#define KEY_DOWN_ARROW 0xD9     // 下箭头
#define KEY_LEFT_ARROW 0xD8     // 左箭头
#define KEY_RIGHT_ARROW 0xD7    // 右箭头
#define KEY_BACKSPACE 0xB2      // 退格键
#define KEY_ENTER 0xB0          // 回车键
#define KEY_Y 0x1A              // Y键
#define KEY_X 0x1B              // X键
#define KEY_B 0x1C              // B键
#define KEY_A 0x1D              // A键
#define LED_PIN 46              // LED引脚
#define ADC_PIN 2               // ADC电量检测引脚

// Ctrl模块：控制功能相关变量和函数

// Ctrl模块：摇杆默认值数组
std::array<int16_t, 4> Ctrl_JoystickValuesDefault = {0};

// Ctrl模块：按键值映射数组
const std::array<uint8_t, 12> Ctrl_KeyMap = {
  KEY_LEFT_CONTROL, // 左摇杆按钮
  KEY_Y,            // Y键
  KEY_X,            // X键
  KEY_B,            // B键
  KEY_A,            // A键
  KEY_BACKSPACE,    // BACK键
  KEY_ENTER,        // START键
  KEY_UP_ARROW,     // 上方向键
  KEY_LEFT_ARROW,   // 左方向键
  KEY_RIGHT_ARROW,  // 右方向键
  KEY_DOWN_ARROW,   // 下方向键
  KEY_RIGHT_CONTROL // 右摇杆按钮
};

// Ctrl模块：摇杆引脚数组
const std::array<uint16_t, 4> Ctrl_JoystickPins = {4, 5, 7, 8}; // 左摇杆X轴、左摇杆Y轴、右摇杆X轴、右摇杆Y轴

// Ctrl模块：按键引脚数组
const std::array<uint8_t, 12> Ctrl_ButtonPins = {6, 15, 14, 16, 21, 1, 0, 10, 12, 11, 13,  9}; // 左摇杆按钮、Y、X、B、A、BACK、START、UP、LEFT、RIGHT、DOWN、右摇杆按钮

// Ctrl模块：是否发送摇杆数据的标志
bool Ctrl_SendJoystickData = false;

// Ctrl模块：摇杆当前值数组
std::array<int16_t, 4> Ctrl_JoystickValuesHid = {0};

// Ctrl模块：按键状态数组
std::array<uint8_t, 12> Ctrl_ButtonStates = {0};

// Ctrl模块：初始化函数
void Ctrl_Initialize()
{
  // 设置LED引脚为输出模式
  pinMode(LED_PIN, OUTPUT);
  // 点亮LED
  digitalWrite(LED_PIN, HIGH);
  // 设置ADC引脚为输入模式
  pinMode(ADC_PIN, INPUT);
  // 初始化摇杆引脚为输入模式
  for (const auto& pin : Ctrl_JoystickPins)
  {
    pinMode(pin, INPUT);
  }
  // 初始化按键引脚为输入模式，启用内部上拉电阻
  for (const auto& pin : Ctrl_ButtonPins)
  {
    pinMode(pin, INPUT_PULLUP);
  }
  // 读取摇杆的初始默认值
  for (size_t i = 0; i < Ctrl_JoystickPins.size(); ++i)
  {
    Ctrl_JoystickValuesDefault[i] = analogRead(Ctrl_JoystickPins[i]);
  }
  // 将初始默认值复制到当前值数组
  Ctrl_JoystickValuesHid = Ctrl_JoystickValuesDefault;
}

// Ctrl模块：检测按键和摇杆状态的函数
void Ctrl_Detect()
{
  // 读取按键状态
  for (size_t i = 0; i < Ctrl_ButtonPins.size(); ++i) Ctrl_ButtonStates[i] = digitalRead(Ctrl_ButtonPins[i]) == LOW;
  // 读取摇杆当前值
  for (size_t i = 0; i < Ctrl_JoystickPins.size(); ++i) Ctrl_JoystickValuesHid[i] = analogRead(Ctrl_JoystickPins[i]);
  // 如果需要发送摇杆数据，则更新摇杆当前值
  if (Ctrl_SendJoystickData)
  {
    for (size_t i = 0; i < Ctrl_JoystickPins.size(); ++i)
      Ctrl_JoystickValuesHid[i] = analogRead(Ctrl_JoystickPins[i]);
    Ctrl_SendJoystickData = false;
  }
}

// Ctrl模块：打印设备状态的函数
void Ctrl_PrintStatus()
{
  // 打印LED状态
  Serial.print("LED State: ");
  Serial.print(digitalRead(LED_PIN));
  Serial.print("\t");

  // 打印ADC数值
  Serial.print("ADC Value: ");
  Serial.print(analogRead(ADC_PIN));
  Serial.print("\t");

  // 打印按键状态
  Serial.print("Button States: ");
  for (uint8_t state : Ctrl_ButtonStates)
  {
    Serial.print(state);
    Serial.print(" ");
  }
  Serial.print("\t");

  // 打印摇杆当前值
  Serial.print("Joystick Values: ");
  for (int16_t value : Ctrl_JoystickValuesHid)
  {
    Serial.print(value);
    Serial.print(" ");
  }
  Serial.println();
}

// 系统设置函数
void setup()
{
  // 初始化串口，波特率115200
  Serial.begin(115200);
  // 执行初始化操作
  Ctrl_Initialize();
  // 打印初始化完成信息
  Serial.println("Initialization Complete:");
  // 打印初始状态
  Ctrl_PrintStatus();
}

// 系统主循环函数
void loop()
{
  // 检测按键和摇杆状态
  Ctrl_Detect();
  // 打印当前状态
  Ctrl_PrintStatus();
  // 添加短暂延迟
  delay(10);
}

/***************************************************************************************
  宏定义区域
*/

#define WIFI_SSID     "NYQBB"        // WiFi 网络名称
#define WIFI_PASSWORD "16675900329"  // WiFi 网络密码

#define WS_PORT       80             // WebSocket 服务器端口

#define LED_PIN       46             // LED 指示灯引脚
#define ADC_PIN       2              // ADC 模拟输入引脚



// 按钮的默认值
#define BUTTON_LEFT_JOYSTICK  129               // 左摇杆按钮 - 关机
#define BUTTON_Y              KEY_PAGE_UP       // Y 按钮 - 键盘 Y 键 (HID 0x1D)
#define BUTTON_X              KEY_HOME          // X 按钮 - 键盘 X 键 (HID 0x1C)
#define BUTTON_B              KEY_END           // B 按钮 - 键盘 B 键 (HID 0x2F)
#define BUTTON_A              KEY_PAGE_DOWN     // A 按钮 - 键盘 A 键 (HID 0x20)
#define BUTTON_BACK           KEY_BACKSPACE     // 返回按钮 - 键盘 BACKSPACE 键 (HID 0x29)
#define BUTTON_START          KEY_KP_ENTER      // 开始按钮 - 键盘 ENTER 键 (HID 0x2B)
#define BUTTON_UP             0X43   // 上方向按钮 - 键盘上箭头键 (HID 0x52)
#define BUTTON_LEFT           0X58    // 左方向按钮 - 键盘左箭头键 (HID 0x53)
#define BUTTON_RIGHT          0X59     // 右方向按钮 - 键盘右箭头键 (HID 0x51)@@@@@@@@@@@@@@@@
#define BUTTON_DOWN           0X5A     // 下方向按钮 - 键盘下箭头键 (HID 0x54)
#define BUTTON_RIGHT_JOYSTICK KEY_ESC           // 右摇杆按钮 - 暂停 / 播放YYYYYYYYYYYYY

/***************************************************************************************
  包含头文件区域
*/

#include <Arduino.h>
#include <WiFi.h>
#include <WebSocketsServer_Generic.h>
#include <ArduinoJson.h>
#include <USB.h>
#include <USBHIDKeyboard.h>
#include <USBHIDMouse.h>
#include <USBHIDSystemControl.h>

/***************************************************************************************
  定义变量区域
*/

WebSocketsServer ws_server = WebSocketsServer(WS_PORT);
USBHIDKeyboard kbd;
USBHIDMouse mouse;
USBHIDSystemControl sys_ctrl;

const std::array<uint8_t, 4> pin_joystick = {4, 5, 7, 8};
const std::array<uint8_t, 12> pin_button = {15, 14, 16, 21, 1, 0, 10, 12, 11, 13, 9, 6};
const std::array<uint8_t, 12> button_map = {
  BUTTON_Y,
  BUTTON_X,
  BUTTON_B,
  BUTTON_A,
  BUTTON_BACK,
  BUTTON_START,
  BUTTON_UP,
  BUTTON_LEFT,
  BUTTON_RIGHT,
  BUTTON_DOWN,
  BUTTON_RIGHT_JOYSTICK,
  BUTTON_LEFT_JOYSTICK
};
std::array<bool, 12> hid_status = {
  true, false, false, false, false, false,
  false, false, false, false, false, true
}; // HID 状态数组
std::array<uint8_t, 12> hid_send = button_map;    // HID 发送数据数组
uint16_t hid_final[4] = {0}; // 用于保存摇杆的初始值
bool hid_use_preset = true; // 是否使用默认 HID 配置


/***************************************************************************************
  函数声明区域
*/

void cmd_execute(const JsonDocument& input_doc, JsonDocument& result);
std::string cmd_process(std::string& json_string);
void ws_handle_event(const uint8_t& num, const WStype_t& type, uint8_t* payload, const size_t& length);
void ctrl_init();
void ctrl_process();
void ctrl_print_status();

/***************************************************************************************
  函数定义区域
*/

// 执行命令函数
void cmd_execute(
  const JsonDocument& input_doc,
  JsonDocument& result
)
{
  const std::vector<std::string> function_names = {
    "Delay",
    "Keyboard.begin",
    "Keyboard.end",
    "Keyboard.press",
    "Keyboard.release",
    "Keyboard.releaseAll",
    "Keyboard.write",
    "Keyboard.print",
    "Keyboard.println",
    "Mouse.move",
    "Mouse.press",
    "Mouse.release",
    "Mouse.click",
    "Mouse.isPressed",
    "SystemControl.begin",
    "SystemControl.end",
    "SystemControl.press",
    "SystemControl.release"
  };
  result.clear();
  JsonObjectConst obj = input_doc.as<JsonObjectConst>();
  for (const auto& elem : obj)
  {
    const std::string function_name = elem.key().c_str();
    const JsonVariantConst& parameters = obj[function_name];
    result[function_name]["status"] = true;
    result[function_name]["args"] = parameters;
    result[function_name]["message"] = "Function executed successfully";
    uint32_t index = 0;
    for (const auto& func_name : function_names)
    {
      if (function_name == func_name) break;
      index++;
    }
    try
    {
      switch (index)
      {
        case 0: delay(parameters.as<uint32_t>()); break;
        case 1: kbd.begin(); break;
        case 2: kbd.end(); break;
        case 3: kbd.press(parameters.as<unsigned char>()); break;
        case 4: kbd.release(parameters.as<unsigned char>()); break;
        case 5: kbd.releaseAll(); break;
        case 6: kbd.write(parameters.as<unsigned char>()); break;
        case 7: kbd.print(parameters.as<const char*>()); break;
        case 8: kbd.println(parameters.as<const char*>()); break;
        case 9: mouse.move(parameters.as<JsonArrayConst>()[0].as<int32_t>(), parameters.as<JsonArrayConst>()[1].as<int32_t>()); break;
        case 10: mouse.press(parameters.as<uint8_t>()); break;
        case 11: mouse.release(parameters.as<uint8_t>()); break;
        case 12: mouse.click(parameters.as<uint8_t>()); break;
        case 13: result[function_name]["result"] = mouse.isPressed(parameters.as<uint8_t>()); break;
        case 14: sys_ctrl.begin(); break;
        case 15: sys_ctrl.end(); break;
        case 16: sys_ctrl.press(parameters.as<uint8_t>()); break;
        case 17: sys_ctrl.release(); break;
        default:
          result[function_name]["status"] = false;
          result[function_name]["message"] = "Function not recognized";
          break;
      }
    }
    catch (const std::exception& e)
    {
      result[function_name]["status"] = false;
      result[function_name]["message"] = e.what();
    }
  }
}

// 处理命令函数
std::string cmd_process(
  std::string& json_string
)
{
  JsonDocument input_doc;
  JsonDocument output_doc;
  DeserializationError error = deserializeJson(input_doc, json_string);
  if (error) return "";
  if (input_doc.is<JsonArray>())
  {
    JsonArray result_array = output_doc.to<JsonArray>();
    for (JsonVariant item : input_doc.as<JsonArray>())
    {
      JsonDocument result_doc;
      cmd_execute(item.as<JsonObjectConst>(), result_doc);
      result_array.add(result_doc.as<JsonObject>());
    }
  }
  if (input_doc.is<JsonObject>()) cmd_execute(input_doc.as<JsonObjectConst>(), output_doc);
  serializeJsonPretty(output_doc, json_string);
  std::string response = json_string;
  json_string.clear();
  return response;
}

// WebSocket 事件处理函数
void ws_handle_event(
  const uint8_t& num,
  const WStype_t& type,
  uint8_t* payload,
  const size_t& length
)
{
  switch (type)
  {
    case WStype_DISCONNECTED: break;
    case WStype_CONNECTED: ws_server.sendTXT(num, "Connected"); break;
    case WStype_TEXT:
      {
        const char* payload_str = reinterpret_cast<const char*>(payload);
        std::string json_string(payload_str, length);
        std::string response = cmd_process(json_string);
        ws_server.sendTXT(num, response.c_str());
        break;
      }
    case WStype_BIN: ws_server.sendBIN(num, payload, length); break;
    case WStype_FRAGMENT_TEXT_START: break;
    case WStype_FRAGMENT_BIN_START: break;
    case WStype_FRAGMENT: break;
    case WStype_FRAGMENT_FIN: break;
    case WStype_PING: break;
    case WStype_PONG: break;
    default: break;
  }
}

// 初始化控制函数
void ctrl_init()
{
  for (const auto& pin : pin_joystick) pinMode(pin, INPUT);
  for (const auto& pin : pin_button) pinMode(pin, INPUT_PULLUP);
  hid_final[0] = analogRead(pin_joystick[0]); // 左 X 初始值
  hid_final[1] = analogRead(pin_joystick[1]); // 左 Y 初始值
  hid_final[2] = analogRead(pin_joystick[2]); // 右 X 初始值
  hid_final[3] = analogRead(pin_joystick[3]); // 右 Y 初始值
  pinMode(LED_PIN, OUTPUT);
  pinMode(ADC_PIN, INPUT);
  digitalWrite(LED_PIN, HIGH);
}

// 控制处理函数
void ctrl_process()
{
  int8_t final_values[4] = {
    ((analogRead(pin_joystick[0]) - hid_final[0])) / 50,
    ((analogRead(pin_joystick[1]) - hid_final[1])) / 50,
    ((analogRead(pin_joystick[2]) - hid_final[2])) / 100,
    ((analogRead(pin_joystick[3]) - hid_final[3])) / 100,
  };
  if (final_values[0] || final_values[1]) mouse.move(final_values[0], final_values[1]);
  if (final_values[2] < 0) kbd.press(KEY_LEFT_ARROW);
  if (final_values[3] < 0) kbd.press(KEY_DOWN_ARROW);
  if (final_values[2] > 0) kbd.press(KEY_RIGHT_ARROW);
  if (final_values[3] > 0) kbd.press(KEY_UP_ARROW);
  if (hid_use_preset) hid_send = button_map;
  std::array<uint8_t, 12> pin_status = {0};
  // if (!digitalRead(pin_button[pin_button.size() - 1])) kbd.press(BUTTON_RIGHT_JOYSTICK);
  if (!digitalRead(pin_button[pin_button.size() - 1])) mouse.click();
  for (size_t i = 0; i < pin_button.size() - 2; ++i)
    pin_status[i] = !digitalRead(pin_button[i]);
  for (size_t i = 0; i < pin_button.size() - 2; ++i)
    switch (pin_status[i])
    {
      case 1:
        kbd.press(hid_send[i]);
    }
  delay(25);
  kbd.releaseAll();
}

// 打印状态函数
void ctrl_print_status()
{
  Serial.print("LED State: ");
  Serial.print(digitalRead(LED_PIN));
  Serial.print("\t");
  Serial.print("ADC Value: ");
  Serial.print(analogRead(ADC_PIN));
  Serial.print("\t");
  Serial.print("Button States: ");
  for (size_t i = 8; i < hid_send.size(); ++i)
  {
    Serial.print(hid_send[i]);
    Serial.print(" ");
  }
  Serial.print("\t");
  Serial.print("Joystick Values: ");
  for (size_t i = 0; i < 8; ++i)
  {
    Serial.print(hid_send[i]);
    Serial.print(" ");
  }
  Serial.println();
}

/***************************************************************************************
  主函数
*/

void setup()
{
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(1000);
    Serial.print(".");
  }
  kbd.begin();
  mouse.begin();
  sys_ctrl.begin();
  ws_server.begin();
  ws_server.onEvent(ws_handle_event);
  USB.begin();
  delay(5000);
  Serial.println("连接成功");
  ctrl_init();
  Serial.println("Initialization Complete:");
}

void loop()
{
  ws_server.loop();
  ctrl_process();
  //  ctrl_print_status();
}

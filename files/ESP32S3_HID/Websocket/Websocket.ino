#include <Arduino.h>
#include <WiFi.h>
#include <ESPmDNS.h>
#include <WebSocketsServer_Generic.h>
#include <ArduinoJson.h>
#include <USB.h>
#include <USBHIDKeyboard.h>
#include <USBHIDMouse.h>
#include <USBHIDSystemControl.h>

const char* ssid = "NYQBB";
const char* password = "16675900329";

#define WS_PORT 80

WebSocketsServer webSocket = WebSocketsServer(WS_PORT);

USBHIDKeyboard hid_keyboard;
USBHIDMouse hid_mouse;
USBHIDSystemControl hid_system_control;

void execute_commands(const JsonDocument& input_doc, JsonDocument& result)
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
        case 1: hid_keyboard.begin(); break;
        case 2: hid_keyboard.end(); break;
        case 3: hid_keyboard.press(parameters.as<unsigned char>()); break;
        case 4: hid_keyboard.release(parameters.as<unsigned char>()); break;
        case 5: hid_keyboard.releaseAll(); break;
        case 6: hid_keyboard.write(parameters.as<unsigned char>()); break;
        case 7: hid_keyboard.print(parameters.as<const char*>()); break;
        case 8: hid_keyboard.println(parameters.as<const char*>()); break;
        case 9: hid_mouse.move(parameters.as<JsonArrayConst>()[0].as<int32_t>(), parameters.as<JsonArrayConst>()[1].as<int32_t>()); break;
        case 10: hid_mouse.press(parameters.as<uint8_t>()); break;
        case 11: hid_mouse.release(parameters.as<uint8_t>()); break;
        case 12: hid_mouse.click(parameters.as<uint8_t>()); break;
        case 13: result[function_name]["result"] = hid_mouse.isPressed(parameters.as<uint8_t>()); break;
        case 14: hid_system_control.begin(); break;
        case 15: hid_system_control.end(); break;
        case 16: hid_system_control.press(parameters.as<uint8_t>()); break;
        case 17: hid_system_control.release(); break;
        default:
          result[function_name]["status"] = NULL;
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

std::string process_command(std::string& json_string)
{
  JsonDocument input_doc;
  JsonDocument output_doc;
  input_doc.clear();
  DeserializationError error = deserializeJson(input_doc, json_string);
  if (error) return "";
  if (input_doc.is<JsonArray>())
  {
    JsonArray result_array = output_doc.to<JsonArray>();
    const JsonArray& arr = input_doc.as<JsonArray>();
    for (JsonVariantConst item : arr)
    {
      if (item.is<JsonVariantConst>()) {
        JsonDocument result_doc;
        execute_commands(item.as<JsonObjectConst>(), result_doc);
        result_array.add(result_doc.as<JsonObject>());
      }
    }
  }
  if (input_doc.is<JsonObject>()) execute_commands(input_doc.as<JsonObjectConst>(), output_doc);
  serializeJsonPretty(output_doc, json_string);
  std::string response = json_string;
  json_string.clear();
  return response;
}

void webSocketEvent(const uint8_t& num, const WStype_t& type, uint8_t* payload, const size_t& length)
{
  switch (type)
  {
    case WStype_DISCONNECTED: break;
    case WStype_CONNECTED: webSocket.sendTXT(num, "Connected"); break;
    case WStype_TEXT:
      {
        const char* payload_str = reinterpret_cast<const char*>(payload);
        std::string json_string(payload_str, length);
        std::string response = process_command(json_string);
        webSocket.sendTXT(num, response.c_str());
        response.clear();
      }
      break;
    case WStype_BIN: webSocket.sendBIN(num, payload, length); break;
    case WStype_FRAGMENT_TEXT_START: break;
    case WStype_FRAGMENT_BIN_START: break;
    case WStype_FRAGMENT: break;
    case WStype_FRAGMENT_FIN: break;
    case WStype_PING: break;
    case WStype_PONG: break;
    default: break;
  }
}


ICACHE_FLASH_ATTR auto NetInit(String names)
{
  names += String(WiFi.macAddress());
  names.replace(':', '-');
  WiFi.mode(WIFI_STA);
  WiFi.hostname(names);
  MDNS.begin("esp32");
  if (WiFi.status() != WL_CONNECTED) WiFi.begin(WiFi.SSID().c_str(), WiFi.psk().c_str());
  //  WiFi.begin("萌小狸宝宝", "13226253380");
  return names;
}

ICACHE_FLASH_ATTR auto NetConnect()
{
  if (WiFi.status() == WL_CONNECTED)
  {
    WiFi.disconnect();
    delay(100);
  }
  WiFi.beginSmartConfig();
  uint64_t connect_times = millis();
  while (millis() < 60 * 1000 || millis() - connect_times <= 60 * 1000)
  {
    if (WiFi.smartConfigDone())
    {
      WiFi.setAutoReconnect(true);
      delay(5000);
      return true;
    }
    delay(100);//一定要加延时，不然直接重启。
  }
  WiFi.stopSmartConfig();
  WiFi.begin(WiFi.SSID().c_str(), WiFi.psk().c_str());
  return false;
}

void setup()
{
  pinMode(0, OUTPUT);
  digitalWrite(0, HIGH);
  Serial.begin(115200);
  Serial.println(NetInit("ESP32S2_"));
  hid_mouse.begin();
  hid_keyboard.begin();
  hid_system_control.begin();
  USB.begin();
  webSocket.begin();
  webSocket.onEvent(webSocketEvent);
}

void loop()
{
  if (WiFi.status() == WL_CONNECTED) webSocket.loop();
  if (!digitalRead(0)) NetConnect();
}

/*
   帮助说明：该库为Dfrobot公司提供，对PN532开发板进行二次开发。
   编译时间：2024年12月14日。
   开发人员：奶元清～萌小狸。
   代码地址：https://github.com/nyqmxl/nyqmxl/dfrotbot_PN532.ino。
   备注说明：该库仅用于测试。
*/

#include <DFRobot_PN532.h>

#define PN532_IRQ (2)
#define POLLING (0)

DFRobot_PN532_IIC nfc(PN532_IRQ, POLLING);

ICACHE_FLASH_ATTR class PN532
{
  public:
    /*
       功能：将String类型字符串转uint8_t类型二维数组。
       参数：String类型字符，uint8_t类型二维数组。
       返回：无。
       备注：通过函数对uint8_t类型二维数组进行操作。
    */
    ICACHE_FLASH_ATTR uint8_t string_uint8(String data_string = String(), uint8_t data_char[][0X10] = {0})
    {
      // uint8_t data_demo[(input.length() + 0XF) / 0X10][0X10];  // 获取uint8_t类型二位数组长度
      uint16_t data_length = (data_string.length() + 0XF) / 0X10; // 计算二维数组的行数
      for (int f1 = 0; f1 < data_string.length(); f1++)
        data_char[f1 / 0X10][f1 % 0X10] = data_string.charAt(f1); // 将字符串转换为二维数组
      for (int f1 = data_string.length(); f1 < data_length * 0X10; f1++)
        data_char[f1 / 0X10][f1 % 0X10] = NULL; // 填充剩余位置为NULL
      return data_length;
    }

    /*
       功能：写入数据，data_public默认为公有写入，可以通过修改值进行写入。
       参数：String类型字符，Bool类型。
       返回：写入成功或者失败，即true|false。
       备注：默认为true写入公共区域。
    */
    ICACHE_FLASH_ATTR bool write(String data_string = String(), bool data_public = true)
    {
      if (!nfc.scan()) return NULL;
      DFRobot_PN532::sCard_t NFCcard;
      NFCcard = nfc.getInformation();
      uint8_t data_length = (data_string.length() + 0XF) / 0X10; // 获取String类型字符串长度
      uint8_t data_char[data_length][0X10];                      // 定义输出数组
      string_uint8(data_string, data_char);                      // 将字符串转换为uint8_t二维数组
      if (NFCcard.AQTA[1] == 0x02 || NFCcard.AQTA[1] == 0x04)    // 循环写入数据
      {
        for (uint8_t f1 = 0X0; f1 < data_length && data_length < (data_public ? 0X3 : NFCcard.blockNumber); f1++)
          for (uint8_t f2 = 0X0; f2 < 0X3; f2++)
          {
            // Serial.println(data_public ? f2 : f1 * 0X3 + f2);                                                                              // 写入异常启用这里
            if ((data_public ? f2 : f1 * 0X3 + f2) >= data_length) goto goto_exit;                                                            // 重要环节提前跳出，不然内存泄露（￣︶￣）↗　触发看门狗。
            uint8_t data_number = nfc.writeData(data_public ? f2 + 0X1 : (f1 + 0X1) * 0X4 + f2, data_char[data_public ? f2 : f1 * 0X3 + f2]); // 写入数据，并根据返回值打印相应的状态信息
            // switch (data_number)
            // {
            //   case -1: Serial.println("写入失败！"); break;
            //   case 0: Serial.println("正在写入！"); break;
            //   case 1: Serial.println("写入成功！"); break;
            // }
          }
goto_exit:
        return true;
      }
      return false;
    }

    /*
       功能：写入零覆盖，data_public默认为公有写入，可以通过修改值进行写入。
       参数：String类型字符，Bool类型。
       返回：写入成功或者失败，即true|false。
       备注：默认为true写入公共区域。
    */
    ICACHE_FLASH_ATTR bool clear(bool data_public = true)
    {
      if (!nfc.scan()) return false;
      DFRobot_PN532::sCard_t NFCcard;
      uint8_t data_char[0X10] = {0};
      NFCcard = nfc.getInformation();
      if (NFCcard.AQTA[1] == 0x02 || NFCcard.AQTA[1] == 0x04)
        for (uint8_t f1 = (data_public ? 0X1 : 0X4); f1 < (data_public ? 0X3 : NFCcard.blockNumber); f1++)
        {
          // Serial.print(f1);                                // 写入异常启用这里
          uint8_t data_number = nfc.writeData(f1, data_char); // 写入数据，并根据返回值打印相应的状态信息
          switch (data_number)
          {
            case -1: Serial.println("写入失败！"); break;
            case 0: Serial.println("正在写入！"); break;
            case 1: Serial.println("写入成功！"); break;
          }
        }
      return true;
    }

    /*
       功能：读取数据，data_public默认为公有读取，可以通过修改值进行写入。
       参数：String类型字符，Bool类型。
       返回：String类型字符串。
       备注：默认为true读取公共区域。
    */
    ICACHE_FLASH_ATTR String read(bool data_public = true)
    {
      if (!nfc.scan()) return String();
      DFRobot_PN532::sCard_t NFCcard;
      String data_string = String();
      NFCcard = nfc.getInformation();
      if (NFCcard.AQTA[1] == 0x02 || NFCcard.AQTA[1] == 0x04)
        for (uint8_t f1 = (data_public ? 0X0 : 0X4); f1 < (data_public ? 0X3 : NFCcard.blockNumber); f1++)
        {
          if (f1 % 0X4 != 0X3 && f1 != 0X0)
          {
            uint8_t data_char[0X10];
            uint8_t data_number = nfc.readData(data_char, f1);
            // switch (data_number)
            // {
            //   case -1: Serial.println("读取失败！"); break;
            //   case 0: Serial.println("正在读取！"); break;
            //   case 1: Serial.println("读取成功！"); break;
            // }
            for (uint8_t f2 = 0X0; f2 < 0X10; f2++)
            {
              if ((char)data_char[f2] == '\0') goto goto_exit;
              data_string += (char)data_char[f2];
            }
          }
        }
goto_exit:
      data_string += '\0';
      return String(data_string);
    }

    /*
       功能：读取卡片ID号。
       参数：Bool类型，默认为false。
       返回：uint32_t类型变量。
       备注：默认false的HEX值是倒序输出，true的HEX和原始输出一样。
    */
    ICACHE_FLASH_ATTR uint32_t id(bool data_sort = false)
    {
      uint32_t data_id = 0X0;
      if (!nfc.scan()) return data_id;
      DFRobot_PN532::sCard_t NFCcard;
      NFCcard = nfc.getInformation();
      if (NFCcard.AQTA[1] == 0x02 || NFCcard.AQTA[1] == 0x04)
        ;
      {
        uint8_t data_byte[0X10] = {0X0};
        nfc.readData(data_byte, 0);
        for (uint8_t f1 = 0X0; f1 < 0X4; f1++)
          data_id += data_byte[f1] << (data_sort ? 24 - 0X8 * f1 : 0X8 * f1);
      }
      return data_id;
    }

    /*
       功能：读取卡片厂商。
       参数：Bool类型，默认为true。
       返回：String类型变量。
       备注：默认true的十进制值是输出，false输出十六进制值。
    */
    ICACHE_FLASH_ATTR String firm(bool data_dec = true)
    {
      String data_firm = String();
      if (!nfc.scan()) return data_firm;
      DFRobot_PN532::sCard_t NFCcard;
      NFCcard = nfc.getInformation();
      if (NFCcard.AQTA[1] == 0x02 || NFCcard.AQTA[1] == 0x04)
      {
        uint8_t data_byte[0X10] = {0X0};
        nfc.readData(data_byte, 0);
        for (uint8_t f1 = 0X5; f1 < 0X10; f1++)
          data_firm += String(data_byte[f1], data_dec ? DEC : HEX);
      }
      return data_firm;
    }

} pn532;

void setup()
{
  Serial.begin(115200);
  Serial.println();
  while (!nfc.begin())
  {
    Serial.println("initial failure");
    delay(1000);
  }
  Serial.println("Waiting for a card......");
}

void loop()
{
  bool db = true;
  //  Serial.println(pn532.id());
  //  Serial.println(pn532.id(), HEX);
  //  Serial.println(pn532.firm());
  if (Serial.available() > 0)
  {
    uint8_t data_len = Serial.readString().toInt();
    String data_str = String();
    for (uint8_t f1 = 0X0; f1 < data_len; f1++) data_str += "测试文字!!" + (f1 < 10 ? "0" + String(f1) : String(f1));
    Serial.println(data_str.length());
    pn532.write(data_str, db);
    // pn532.clear(db);
  }
  //  read();
  Serial.println(pn532.read(db));
  delay(1000);
}

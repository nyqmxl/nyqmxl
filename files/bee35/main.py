import serial
import time

def send_receive(command, ser):
    # 发送命令（函数内对字符串进行编码）
    ser.write(command.encode())
    # 读取响应
    response = ser.readline()
    # 将响应字节转换为十六进制字符串
    hex_response = response.hex()
    # 将响应字节转换为ASCII字符串（过滤掉非可打印字符）
    ascii_response = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in response)
    return command, hex_response, ascii_response

def control_drone():
    # 打开串口连接
    ser = serial.Serial('COM3', 921600, timeout=1)
    
    # 定义要发送的命令列表（字符串形式）和每个命令后等待的时间列表（秒）
    commands = [
        'CONNECT',          # 连接
        'DISABLE_RC',       # 禁用遥控器
        'ARM',              # 解锁
        'TAKEOFF',          # 起飞
        'OFFBOARD',         # 进入板外模式
        'LAND',             # 降落
        'STOP'              # 停止
    ]
    
    delays = [2, 2, 2, 10, 10, 10, 2]
    
    # 使用for循环发送每个命令
    for i, command in enumerate(commands):
        sent, hex_response, ascii_response = send_receive(command, ser)
        print(f"Sent: {sent}")
        print(f"Response (hex): {hex_response}")
        print(f"Response (ascii): {ascii_response}")
        time.sleep(delays[i])
    
    # 关闭串口连接
    ser.close()

if __name__ == "__main__":
    try:
        control_drone()
    except KeyboardInterrupt:
        print("Program exited.")
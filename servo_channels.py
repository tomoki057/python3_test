import time
import board
import busio
from adafruit_pca9685 import PCA9685

# I2Cバスの初期化
i2c = busio.I2C(board.SCL, board.SDA)

# PCA9685の初期化
pca = PCA9685(i2c)
pca.frequency = 50  # サーボモーター用に50Hzに設定

# サーボのチャンネル(青)
servo_channel_Blue = 3

# サーボのチャンネル(黄)
servo_channel_Yellow = 4

# サーボのチャンネル(赤)
servo_channel_Red = 5

# 停止時間（秒）
stop_duration = 2

def set_servo_angle(channel, angle):
    pulse_min = 550  # 0度のときのパルス幅（0.55ms）
    pulse_max = 2500  # 180度のときのパルス幅（2.5ms）
    pulse_range = pulse_max - pulse_min
    pulse = pulse_min + (pulse_range * angle / 180)
    duty_cycle = int(pulse / 1000000 * pca.frequency * 65535)
    pca.channels[channel].duty_cycle = duty_cycle

def tank_move (rate):
    set_servo_angle(servo_channel_Blue, rate * 0.6 + 7)
    set_servo_angle(servo_channel_Yellow, 125 - (rate * 0.3))
    set_servo_angle(servo_channel_Red, 180 - (rate *0.6))

try:
    while True:
        # 0 -> 60 slow rotate (blue tank)
        for i in range(0, 100, 1):  # 1度ずつ増加
            tank_move(i)
            time.sleep(0.03)  # 時間を短くして滑らかに
        time.sleep(stop_duration)  # 停止時間

        # 60 -> 0 slow rotate (blue tank)
        for i in range(100, 0, -1):  # 1度ずつ減少
            tank_move(i)
            time.sleep(0.03)  # 時間を短くして滑らかに
        time.sleep(stop_duration)  # 停止時間

except KeyboardInterrupt:
    # 終了時にPCA9685をシャットダウン
    pca.deinit()
    print("Program terminated and PCA9685 shutdown.")

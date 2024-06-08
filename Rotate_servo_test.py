import time
import board
import busio
from adafruit_pca9685 import PCA9685

# I2Cバスの初期化
i2c = busio.I2C(board.SCL, board.SDA)

# PCA9685の初期化
pca = PCA9685(i2c)
pca.frequency = 50  # サーボモーター用に50Hzに設定

# PWM信号を計算する関数（角度をPWMのデューティサイクルに変換）
def set_servo_angle(channel, angle):
    # 角度をPWM信号に変換
    pulse_length = 1000000  # 1,000,000 us per second
    pulse_length //= 50     # 50 Hz
    pulse_length //= 4096   # 12-bit resolution
    pulse = angle * (2000 / 180) + 1000
    pulse //= pulse_length
    pca.channels[channel].duty_cycle = int(pulse)

# サーボモーターのチャンネル設定（例えば、チャンネル0を使用）
servo_channel = 1

try:
    while True:
        # サーボを0度に動かす
        set_servo_angle(servo_channel, 0)
        #time.sleep(1)
        #pca.channels[servo_channel].duty_cycle = 0
        time.sleep(2)

        # サーボを90度に動かす
        set_servo_angle(servo_channel, 90)
        #time.sleep(1)
        #pca.channels[servo_channel].duty_cycle = 0
        time.sleep(2)

        # サーボを180度に動かす
        set_servo_angle(servo_channel, 180)
        time.sleep(1)
        pca.channels[servo_channel].duty_cycle = 0
        time.sleep(2)

except KeyboardInterrupt:
    # 終了時にPCA9685をシャットダウン
    pca.deinit()
    print("Program terminated and PCA9685 shutdown.")

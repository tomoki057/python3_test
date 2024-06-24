import cv2
import numpy as np
import time
import board
import busio
from adafruit_pca9685 import PCA9685

# I2Cバスの初期化
i2c = busio.I2C(board.SCL, board.SDA)

# PCA9685の初期化
pca = PCA9685(i2c)
pca.frequency = 50  # サーボモーター用に50Hzに設定

# サーボモータを動かす関数
def move_servo(channel, pulse):
    pca.channels[channel].duty_cycle = pulse

# サーボモータのチャンネルとパルス幅のマッピング
# ここで、各色に対応するサーボモータのチャンネルとパルス幅を指定します。

PCAchannel = 2

servo_mapping = {
    'blue': (PCAchannel, 2000),   # 例: 青いボール用のサーボモータ
    'red': (PCAchannel, 4000),    # 例: 赤いボール用のサーボモータ
    'yellow': (PCAchannel, 6000)  # 例: 黄色いボール用のサーボモータ
}

def main():
    # USBカメラの映像をキャプチャ
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("カメラを開けませんでした")
        return

    # 各色の範囲を定義（HSV色空間）
    color_ranges = {
        'blue': ([100, 150, 0], [140, 255, 255]),
        'yellow': ([20, 100, 100], [30, 255, 255])
    }

    previous_max_color = None

    while True:
        # フレームを取得
        ret, frame = cap.read()
        if not ret:
            break

        # frame resize(320*240)
        frame = cv2.resize(frame, (320, 240))

        # フレームをHSV色空間に変換
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 赤色のマスクを作成（赤色は二つの範囲に分ける）
        red_lower1 = np.array([0, 120, 70])
        red_upper1 = np.array([10, 255, 255])
        red_lower2 = np.array([170, 120, 70])
        red_upper2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
        mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
        red_mask = mask1 | mask2

        # 他の色のマスクを作成
        masks = {'red': red_mask}
        for color, (lower, upper) in color_ranges.items():
            lower_bound = np.array(lower)
            upper_bound = np.array(upper)
            masks[color] = cv2.inRange(hsv, lower_bound, upper_bound)

        detected_balls = []  # ボール情報を保存するリスト

        for color, mask in masks.items():
            # 輪郭を検出
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                # 輪郭の面積を計算
                area = cv2.contourArea(contour)
                if area > 500:
                    # 外接円を計算
                    ((x, y), radius) = cv2.minEnclosingCircle(contour)
                    center = (int(x), int(y))
                    radius = int(radius)

                    # 円形状かどうかをチェック
                    if radius > 10:
                        circularity = 4 * np.pi * (area / (cv2.arcLength(contour, True) ** 2))
                        if 0.7 < circularity < 1.3:  # 円形に近いかどうか
                            detected_balls.append((color, radius, center))  # 色、半径、中心座標を保存

        # ボールを半径でソート（大きい順）
        detected_balls.sort(key=lambda x: x[1], reverse=True)

        # 最大面積の色を取得
        if detected_balls:
            max_color = detected_balls[0][0]
            if max_color != previous_max_color:
                move_servo_based_on_color(max_color)
                previous_max_color = max_color
                time.sleep(1)  # サーボが安定するまで待機

        # ソートされたボールに順位を表示
        for i, (color, radius, center) in enumerate(detected_balls):
            if color == 'blue':
                cv2.circle(frame, center, radius, (255, 0, 0), 2)
            elif color == 'red':
                cv2.circle(frame, center, radius, (0, 0, 255), 2)
            elif color == 'yellow':
                cv2.circle(frame, center, radius, (0, 255, 255), 2)
            cv2.putText(frame, f'{i+1}', (center[0] - 10, center[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # 結果を表示
        cv2.imshow('Frame', frame)

        # 'q'キーで終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # リソースを解放
    cap.release()
    cv2.destroyAllWindows()

# ボールの色に応じてサーボモータを動かす関数
def move_servo_based_on_color(color):
    if color in servo_mapping:
        channel, pulse = servo_mapping[color]
        move_servo(channel, pulse)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3

###############################################################################
# Example 5 Servo PWM Control
#
#                        Copyright (c) 2021 Wataru KUNINO https://bokunimo.net/
###############################################################################

# ラズベリー・パイに接続した Tower Pro製 マイクロ・サーボモータSG90を
# キーボードから入力した角度の位置に回転して合わせます。。
# 回転時に約120mAの電流が流れます(電源5.2V, 無負荷, 実測値, ピーク電流除く)。
# servo > のプロンプトが表示されたら角度0～180を入力してください。
# 終了するには[Ctrl]キーを押しながら[C]を押してください。

port = 14                                       # GPIO ポート番号=14 (8番ピン)
duty_min = 2.7                                  # 180°のときのPWMのDuty比
duty_max = 13.0                                 # 0°のときのPWMのDuty比

from RPi import GPIO                            # GPIOモジュールの取得
from time import sleep                          # sleepモジュールの取得
GPIO.setmode(GPIO.BCM)                          # ポート番号の指定方法の設定
GPIO.setup(port, GPIO.OUT)                      # ポートportのGPIOを出力に設定
pwm = GPIO.PWM(port, 50)                        # 50Hzを設定
pwm.start(0)                                    # PWM出力 0% (Lレベル)

def deg2duty(deg):                              # Duty比を計算する関数
    return (duty_max - duty_min) * (180 - deg) / 180 + duty_min

try:                                            # キー割り込みの監視を開始
    while True:                                 # 繰り返し処理
        print('servo',end=' > ');               # キーボード入力待ち表示
        val_s =input()                          # キーボードから入力
        if len(val_s)<0 or not val_s.isdigit(): # 入力が数字でないとき
            continue                            # whileの先頭に戻る
        val = int(val_s)                        # 整数値をvalに代入
        if val < 0 or val > 180:                # 0〜180の範囲外のとき
            continue                            # whileの先頭に戻る
        duty = deg2duty(val)                    # 角度値をデューティに変換
        pwm.ChangeDutyCycle(duty)               # サーボの制御を実行
        # sleep(0.36 + 1 / 50)                  # 回転待ち時間
        # pwm.ChangeDutyCycle(0)                # サーボの制御を停止
        print('PWM('+str(port)+')=', str(duty)) # ポート番号と変数dutyを表示

except (KeyboardInterrupt,EOFError):            # キー割り込み発生時
    print('\nKeyboardInterrupt')                # キーボード割り込み表示
    GPIO.cleanup(port)                          # GPIOを未使用状態に戻す
    exit()                                      # 終了

'''
pi@raspberrypi:~ $ git clone https://bokunimo.net/git/raspifan ⏎
　～～～～～～～～～～～～～～～～～～(省略)～～～～～～～～～～～～～～～～～
pi@raspberrypi:~ $ cd raspifan ⏎
pi@raspberrypi:~/raspifan $ ./ex05_servo.py ⏎
servo > 0 ⏎
PWM(14)= 13.0
servo > 45 ⏎
PWM(14)= 10.425
servo > 90 ⏎
PWM(14)= 7.8500000000000005
servo > 135 ⏎
PWM(14)= 5.275
servo > 180 ⏎
PWM(14)= 2.7
servo > ^C
KeyboardInterrupt
pi@raspberrypi:~/raspifan $
'''

#!/usr/bin/env python3

###############################################################################
# Example 6 Servo Velocity Control
#
#                         Copyright (c) 2021 Wataru KUNINO https://bokunimo.net
###############################################################################

# ラズベリー・パイに接続した Tower Pro製 マイクロ・サーボモータSG90を
# 予め設定した速度でサーボモータを定速回転させ、入力した角度の位置で止めます。
# 回転速度を下げることで回転中の消費電流を減らすことが出来ます。
# 1倍速:100mA, 1/2倍速:80mA, 1/4倍速50mA (5.1V動作, 実測値、ピーク電流除く)
# servo > のプロンプトが表示されたら角度0～180を入力してください。
# 終了するには[Ctrl]キーを押しながら[C]を押してください。

port = 14                                       # GPIO ポート番号=14 (8番ピン)
velocity = 180. / 0.36 / 4                      # 最大回転速度(°/秒)の半分
duty_min = 2.7                                  # 180°のときのPWMのDuty比
duty_max = 13.0                                 # 0°のときのPWMのDuty比
delta = (duty_max - duty_min) * velocity / 50 / 180 # 1サイクル当たりの回転角

from RPi import GPIO                            # GPIOモジュールの取得
from time import sleep                          # sleepモジュールの取得
GPIO.setmode(GPIO.BCM)                          # ポート番号の指定方法の設定
GPIO.setup(port, GPIO.OUT)                      # ポートportのGPIOを出力に設定

def deg2duty(deg, offset = 0):                  # Duty比を計算する関数
    return (duty_max - duty_min) * (180 - deg) / 180 + duty_min

def pwm_out(duty):                              # 単一PWM出力用の関数
    GPIO.output(port, 1)                        # Highレベルを出力
    sleep(duty / 5000)                          # 入力Duty比の待ち時間処理
    GPIO.output(port, 0)                        # Lowレベルを出力
    sleep(1 / 50 - duty / 5000)                 # Duty比の残り時間待ち処理

duty = duty_min                                 # PWM制御値(Duty比) 0～100
try:                                            # キー割り込みの監視を開始
    while True:                                 # 繰り返し処理
        print('servo',end=' > ');               # キーボード入力待ち表示
        val_s =input()                          # キーボードから入力
        if len(val_s)<0 or not val_s.isdigit(): # 入力が数字でないとき
            continue                            # whileの先頭に戻る
        val = int(val_s)                        # 整数値をvalに代入
        if val < 0 or val > 180:                # 0〜180の範囲外のとき
            continue                            # whileの先頭に戻る
        target = deg2duty(val)                  # 角度値をデューティに変換
        v_sign = (target > duty)-(target < duty) # 目標の大小を符号に変換
        while True:                             # PWM出力を行うループ
            duty += v_sign * delta              # 変数dutyに回転角分を加減算
            if v_sign * (duty - target) >= 0:   # 目標値に達成した時
                break                           # ループを抜ける
            pwm_out(duty)                       # 変数dutyのDuty比でPWM出力
        duty = target                           # 変数dutyに目標値を代入
        for i in range(18):                     # 180°回転に要する時間に相当
            pwm_out(duty)                       # 変数dutyのDuty比でPWM出力
        print('PWM('+str(port)+')=', str(duty)) # ポート番号と変数dutyの値を表示

except (KeyboardInterrupt,EOFError):            # キー割り込み発生時
    print('\nKeyboardInterrupt')                # キーボード割り込み表示
    GPIO.cleanup(port)                          # GPIOを未使用状態に戻す
    exit()                                      # 終了

'''
pi@raspberrypi:~ $ git clone https://bokunimo.net/git/raspifan ⏎
　～～～～～～～～～～～～～～～～～～(省略)～～～～～～～～～～～～～～～～～
pi@raspberrypi:~ $ cd raspifan ⏎
pi@raspberrypi:~/raspifan $ ./pwm_tester.py ⏎
PWM(14)= 0
servo > 20 ⏎
PWM(14)= 20
servo > 100 ⏎
PWM(14)= 100
servo > ^C
KeyboardInterrupt
pi@raspberrypi:~/raspifan $
'''

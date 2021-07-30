#!/usr/bin/env python3

###############################################################################
# pwm_tester
#
#                        Copyright (c) 2021 Wataru KUNINO https://bokunimo.net/
###############################################################################

# キーボードから0⏎〜100⏎を入力すると入力に応じたディーティ比でPWMを出力します。
# 終了するには[Ctrl]キーを押しながら[C]を押してください。

port = 14                                       # GPIO ポート番号=14 (8番ピン)

from RPi import GPIO                            # GPIOモジュールの取得
GPIO.setmode(GPIO.BCM)                          # ポート番号の指定方法の設定
GPIO.setup(port, GPIO.OUT)                      # ポートportのGPIOを出力に設定
pwm = GPIO.PWM(port, 50)                        # 50Hzを設定
pwm.start(0)                                    # PWM出力 0% (Lレベル)

duty = 0                                        # PWM制御値(Duty比) 0～100
try:                                            # キー割り込みの監視を開始
    while True:                                 # 繰り返し処理
        print('PWM('+str(port)+')=', str(duty)) # ポート番号と変数dutyの値を表示
        pwm.ChangeDutyCycle(duty)               # 変数dutyの値をGPIO出力
        print('fan',end=' > ');                 # キーボード入力待ち表示
        val_s =input()                          # キーボードから入力
        if len(val_s) > 0 and val_s.isdigit():  # 入力が数字のとき
            val = int(val_s)                    # 整数値をvalに代入
            if val >= 0 and val <= 100:         # 0〜100の範囲内のとき
                duty = val

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
fan > 20
PWM(14)= 20
fan > 100
PWM(14)= 100
fan > ^C
KeyboardInterrupt
pi@raspberrypi:~/raspifan $
'''

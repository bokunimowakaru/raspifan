#!/usr/bin/env python3

###############################################################################
# Example 1 FAN ON/OFF
#
#                        Copyright (c) 2021 Wataru KUNINO https://bokunimo.net/
###############################################################################

# キーボードから1⏎を入力するとFANが回転、0⏎を入力すると停止します。
# 終了するには[Ctrl]キーを押しながら[C]を押してください。

port = 14                                       # GPIO ポート番号=14 (8番ピン)

from RPi import GPIO                            # GPIOクラスメソッドの取得
GPIO.setmode(GPIO.BCM)                          # ポート番号の指定方法の設定
GPIO.setup(port, GPIO.OUT)                      # ポートportのGPIOを出力に設定

val = 0                                         # GPIO 制御値 0 または 1
try:                                            # キー割り込みの監視を開始
    while True:                                 # 繰り返し処理
        print('GPIO'+str(port),'=',str(val))    # ポート番号と変数valの値を表示
        GPIO.output(port, val)                  # 変数valの値をGPIO出力
        print('fan',end=' > ');                 # キーボード入力待ち表示
        val_s =input()                          # キーボードから入力
        val = 0                                 # 制御値を0(Lowレベル)に
        if len(val_s) > 0 and val_s.isdigit():  # 入力が数字のとき
            val = int(bool(int(val_s)))         # 真偽値の整数値をvalに代入

except (KeyboardInterrupt,EOFError):            # キー割り込み発生時
    print('\nKeyboardInterrupt')                # キーボード割り込み表示
    GPIO.cleanup(port)                          # GPIOを未使用状態に戻す
    exit()                                      # 終了

'''
pi@raspberrypi:~ $ git clone https://bokunimo.net/git/raspifan ⏎
　～～～～～～～～～～～～～～～～～～(省略)～～～～～～～～～～～～～～～～～
pi@raspberrypi:~ $ cd raspifan ⏎
pi@raspberrypi:~/raspifan $ ./ex01_gpio.py ⏎
GPIO14 = 0
fan > 1 ⏎
GPIO14 = 1
fan > 0 ⏎
GPIO14 = 0
fan > ^C
KeyboardInterrupt
pi@raspberrypi:~/raspifan $
'''

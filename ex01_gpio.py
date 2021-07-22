#!/usr/bin/env python3

###############################################################################
# Example 1 FAN ON/OFF
#
#                         Copyright (c) 2021 Wataru KUNINO https://bokunimo.net
###############################################################################

# キーボードからH⏎を入力するとFANが回転、L⏎を入力すると停止します。
# 終了するには[Ctrl]キーを押しながら[C]を押してください。

port = 14                                       # GPIO ポート番号=14 (8番ピン)

from RPi import GPIO                            # GPIOモジュールの取得
GPIO.setmode(GPIO.BCM)                          # ポート番号の指定方法の設定
GPIO.setup(port, GPIO.OUT)                      # ポートportのGPIOを出力に設定

val = 0                                         # GPIO 制御値 0 または 1
try:                                            # キー割り込みの監視を開始
    while True:                                 # 繰り返し処理
        print('GPIO'+str(port),'=',str(val))    # ポート番号と変数valの値を表示
        GPIO.output(port, val)                  # 変数valの値をGPIO出力
        print('fan',end=' > ');                 # キーボード入力待ち表示
        val_s =input()                          # キーボードから入力
        if val_s[0].upper()=='L':               # 先頭文字がLのとき
            val = 0                             # 制御値は0(Lowレベル)
        elif val_s[0].upper()=='H':             # 先頭文字がHのとき
            val = 1                             # 制御値は1(Highレベル)
        elif val_s.isdigit():                   # 数字のとき
            val = int(val_s)                    # 整数に変換
        else:                                   # 以上の条件に合わないとき
            val = 0                             # 制御値は0(Lowレベル)

except (KeyboardInterrupt,EOFError):            # キー割り込み発生時
    print('\nKeyboardInterrupt')                # キーボード割り込み表示
    GPIO.cleanup(port)                          # GPIOを未使用状態に戻す
    exit()                                      # 終了

'''
pi@raspberrypi:~ $ git clone https://bokunimo.net/git/raspifan
　～～～～～～～～～～～～～～～～～～(省略)～～～～～～～～～～～～～～～～～
pi@raspberrypi:~ $ cd raspifan
pi@raspberrypi:~/raspifan $ ./ex01_gpio.py
GPIO14 = 0
fan > High
GPIO14 = 1
fan > Low
GPIO14 = 0
fan > ^C
KeyboardInterrupt
pi@raspberrypi:~/raspifan $
'''

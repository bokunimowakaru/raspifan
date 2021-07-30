#!/usr/bin/env python3

###############################################################################
# Example 2 FAN AUTO ON/OFF
#
#                        Copyright (c) 2021 Wataru KUNINO https://bokunimo.net/
###############################################################################

# CPU温度が60℃以上でFANを回転、55℃以下で停止するファンの自動制御を行います
# 終了するには[Ctrl]キーを押しながら[C]を押してください。

port = 14                                       # GPIO ポート番号 = 14 (8番ピン)
temp_fan_on = 60                                # ファンをONにする温度
temp_fan_off = 55                               # ファンをOFFにする温度

from RPi import GPIO                            # GPIOモジュールの取得
from time import sleep                          # スリープ実行モジュールの取得
GPIO.setmode(GPIO.BCM)                          # ポート番号の指定方法の設定
GPIO.setup(port, GPIO.OUT)                      # ポートportのGPIOを出力に設定

filename = '/sys/class/thermal/thermal_zone0/temp' # 温度値が書かれたファイル
val = 0                                         # GPIO 制御値 0 または 1
try:                                            # キー割り込みの監視を開始
    while True:                                 # 繰り返し処理
        fp = open(filename)                     # 温度ファイルを開く
        temp = float(fp.read()) / 1000          # ファイルを読み込み1000で除算
        fp.close()                              # ファイルを閉じる
        print('Temperature =', round(temp,1), end=', ') # 温度を表示する
        if temp >= temp_fan_on:
            val = 1
        if temp <= temp_fan_off:
            val = 0
        print('GPIO'+str(port),'=',str(val))    # ポート番号と変数valの値を表示
        GPIO.output(port, val)                  # 変数valの値をGPIO出力
        sleep(5)                                # 5秒間の待ち時間処理
except KeyboardInterrupt:                       # キー割り込み発生時
    print('\nKeyboardInterrupt')                # キーボード割り込み表示
    GPIO.cleanup(port)                          # GPIOを未使用状態に戻す
    exit()                                      # 終了

'''
pi@raspberrypi:~ $ git clone https://bokunimo.net/git/raspifan ⏎
　～～～～～～～～～～～～～～～～～～(省略)～～～～～～～～～～～～～～～～～
pi@raspberrypi:~ $ cd raspifan ⏎
pi@raspberrypi:~/raspifan $ ./ex02_auto.py ⏎
Temperature = 52.6, GPIO14 = 0
Temperature = 53.1, GPIO14 = 0
Temperature = 54.0, GPIO14 = 0
　～～～～～～～～～～～～～～～～～～(省略)～～～～～～～～～～～～～～～～～
Temperature = 59.4, GPIO14 = 0
Temperature = 60.9, GPIO14 = 1
Temperature = 61.3, GPIO14 = 1
　～～～～～～～～～～～～～～～～～～(省略)～～～～～～～～～～～～～～～～～
Temperature = 55.0, GPIO14 = 1
Temperature = 54.5, GPIO14 = 0
Temperature = 55.0, GPIO14 = 0
Temperature = 54.0, GPIO14 = 0
^C
KeyboardInterrupt
pi@raspberrypi:~/raspifan $
'''

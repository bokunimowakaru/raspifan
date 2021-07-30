#!/usr/bin/env python3

###############################################################################
# Example 3 FAN PWM Control
#
#                        Copyright (c) 2021 Wataru KUNINO https://bokunimo.net/
###############################################################################

# CPU温度が55℃以下に抑えるようにファン速度をPWMで調整します。
# 終了するには[Ctrl]キーを押しながら[C]を押してください。

# /etc/rc.localに下記を追加するとRaspberry Piの起動時に自動実行できます
# nohup /home/pi/raspifan/ex03_pwm.py &> /dev/null &

port = 14                                       # GPIO ポート番号 = 14 (8番ピン)
temp_target = 55                                # ファンをOFFにする温度(℃)
accele = 35                                     # 温度1℃あたりのファン速度
velocity = 25                                   # 平衡時のファン速度
duty_min = 25                                   # 最小Duty(ファン動作可能電圧)
period = 15                                     # 制御間隔(秒)

from RPi import GPIO                            # GPIOモジュールの取得
from time import sleep                          # スリープ実行モジュールの取得
GPIO.setmode(GPIO.BCM)                          # ポート番号の指定方法の設定
GPIO.setup(port, GPIO.OUT)                      # ポートportのGPIOを出力に設定
pwm = GPIO.PWM(port, 50)                        # 50Hzを設定
pwm.start(0)                                    # PWM出力 0% (Lレベル)

filename = '/sys/class/thermal/thermal_zone0/temp' # 温度値が書かれたファイル
duty = 0                                        # PWM制御値(Duty比) 0～100
try:                                            # キー割り込みの監視を開始
    while True:                                 # 繰り返し処理
        temp = 0                                # 温度を保持する変数tempを生成
        for i in range(period):                 # 繰り返し処理(回数=period)
            fp = open(filename)                 # 温度ファイルを開く
            temp += float(fp.read()) / 1000     # ファイルを読み込み1000で除算
            fp.close()                          # ファイルを閉じる
            sleep(1)                            # 1秒間の待ち時間処理
        temp /= period                          # 平均値を算出
        print('Temperature =', round(temp,1), end=', ') # 温度を表示する
        duty = (temp - temp_target) * accele + velocity # 出力dutyを算出
        duty = round(duty)                      # 変数dutyの値を整数に丸める
        if duty <= 0:                           # 目標以下なので冷却不要
            duty = 0                            # PWM Duty(ファン速度)を0に
        elif duty < duty_min:                   # ファン非動作範囲(だが要冷却)
            duty = duty_min                     # PWM Duty(ファン速度)を最小値
        elif duty > 100:                        # 最大ファン速度を超過
            duty = 100                          # PWM Duty(ファン速度)を100に
        print('PWM('+str(port)+')=', str(duty)) # ポート番号と変数dutyの値を表示
        pwm.ChangeDutyCycle(duty)               # 変数dutyの値をGPIO出力
except KeyboardInterrupt:                       # キー割り込み発生時
    print('\nKeyboardInterrupt')                # キーボード割り込み表示
    GPIO.cleanup(port)                          # GPIOを未使用状態に戻す
    exit()                                      # 終了

'''
pi@raspberrypi:~ $ git clone https://bokunimo.net/git/raspifan ⏎
　～～～～～～～～～～～～～～～～～～(省略)～～～～～～～～～～～～～～～～～
pi@raspberrypi:~ $ cd raspifan ⏎
pi@raspberrypi:~/raspifan $ ./ex03_pwm.py ⏎
Temperature = 59.3, PWM(14)= 100
Temperature = 58.0, PWM(14)= 100
Temperature = 56.8, PWM(14)= 84
Temperature = 55.8, PWM(14)= 53
Temperature = 54.8, PWM(14)= 25
Temperature = 55.0, PWM(14)= 30
Temperature = 55.6, PWM(14)= 47
Temperature = 55.2, PWM(14)= 35
Temperature = 54.8, PWM(14)= 25
Temperature = 55.0, PWM(14)= 29
^C
KeyboardInterrupt
pi@raspberrypi:~/raspifan $
'''

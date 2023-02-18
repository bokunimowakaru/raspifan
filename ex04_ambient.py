#!/usr/bin/env python3

###############################################################################
# Example 4 Temperature to Ambient
#
#                        Copyright (c) 2021 Wataru KUNINO https://bokunimo.net/
###############################################################################

# CPU温度によるファン制御の様子を Ambient へ送信します。
# 温度や制御の推移をスマホで確認することが出来るようになります。
# 終了するには[Ctrl]キーを押しながら[C]を押してください。

ambient_chid='00000'            # ここにAmbientで取得したチャネルIDを入力
ambient_wkey='0123456789abcdef' # ここにはライトキーを入力
port = 14                                       # GPIO ポート番号 = 14 (8番ピン)
temp_target = 55                                # ファンをOFFにする温度(℃)
accele = 35                                     # 温度1℃あたりのファン速度
velocity = 25                                   # 平衡時のファン速度
duty_min = 25                                   # 最小Duty(ファン動作可能電圧)
period = 30                                     # 制御間隔(秒) ※30秒以上

from RPi import GPIO                            # GPIOモジュールの取得
from time import sleep                          # スリープ実行モジュールの取得
GPIO.setmode(GPIO.BCM)                          # ポート番号の指定方法の設定
GPIO.setup(port, GPIO.OUT)                      # ポートportのGPIOを出力に設定
pwm = GPIO.PWM(port, 50)                        # 50Hzを設定
pwm.start(0)                                    # PWM出力 0% (Lレベル)

import urllib.request                           # HTTP通信ライブラリを組み込む
import json                                     # JSON変換ライブラリを組み込む

def sendToAmbient(ambient_chid, head_dict, body_dict):
    if int(ambient_chid) != 0:
        post = urllib.request.Request(\
            url_s, json.dumps(body_dict).encode(), head_dict\
        )                                       # POSTリクエストデータを作成
        try:                                    # 例外処理の監視を開始
            res = urllib.request.urlopen(post)  # HTTPアクセスを実行
        except Exception as e:                  # 例外処理発生時
            print('ERROR:',e,url_s)             # エラー内容と変数url_sを表示
            return
        res_str = res.read().decode()           # 受信テキストを変数res_strへ
        res.close()                             # HTTPアクセスの終了
    else:
        print('    チャネルID(ambient_chid)が設定されていません')

filename = '/sys/class/thermal/thermal_zone0/temp' # 温度値が書かれたファイル
url_s = 'https://ambidata.io/api/v2/channels/'+ambient_chid+'/data' # アクセス先
head_dict = {'Content-Type':'application/json'} # ヘッダを変数head_dictへ
body_dict = {'writeKey':ambient_wkey, 'd1':None,'d2':None}
duty = 0                                        # PWM制御値(Duty比) 0～100

try:                                            # キー割り込みの監視を開始
  while True:
    temp = 0                                    # 温度を保持する変数tempを生成
    for i in range(period):                     # 繰り返し処理(回数=period)
        fp = open(filename)                     # 温度ファイルを開く
        temp += float(fp.read()) / 1000         # ファイルを読み込み1000で除算
        fp.close()                              # ファイルを閉じる
        sleep(1)                                # 1秒間の待ち時間処理
    temp /= period                              # 平均値を算出
    print('Temperature =', round(temp,1), end=', ') # 温度を表示する
    duty = (temp - temp_target) * accele + velocity # 出力dutyを算出
    duty = round(duty)                          # 変数dutyの値を整数に丸める
    if duty <= 0:                               # 目標以下なので冷却不要
        duty = 0                                # PWM Duty(ファン速度)を0に
    elif duty < duty_min:                       # ファン非動作範囲(だが要冷却)
        duty = duty_min                         # PWM Duty(ファン速度)を最小値
    elif duty > 100:                            # 最大ファン速度を超過
        duty = 100                              # PWM Duty(ファン速度)を100に
    print('PWM('+str(port)+')=', str(duty), end=', ')   # 変数dutyの値を表示
    pwm.ChangeDutyCycle(duty)                   # 変数dutyの値をGPIO出力
    body_dict['d1'] = temp                      # 項目d1にCPU温度値tempを代入
    body_dict['d2'] = duty                      # 項目d2に制御値dutyを代入
    print(body_dict)                            # 送信内容body_dictを表示
    sendToAmbient(ambient_chid, head_dict, body_dict)   # Ambientへ送信
except KeyboardInterrupt:                       # キー割り込み発生時
    print('\nKeyboardInterrupt')                # キーボード割り込み表示
    GPIO.cleanup(port)                          # GPIOを未使用状態に戻す
    exit()                                      # 終了

'''
pi@raspberrypi:~ $ git clone https://bokunimo.net/git/raspifan ⏎
　～～～～～～～～～～～～～～～～～～(省略)～～～～～～～～～～～～～～～～～
pi@raspberrypi:~ $ cd raspifan ⏎
pi@raspberrypi:~/raspifan $ ./ex04_ambient.py ⏎
Temperature = 58.0, PWM(14)= 100, {'writeKey': '3209ffa1xxxxxxxx', 'd1': 58.00393333333332, 'd2': 100}
Temperature = 57.3, PWM(14)= 100, {'writeKey': '3209ffa1xxxxxxxx', 'd1': 57.27343333333333, 'd2': 100}
Temperature = 55.3, PWM(14)= 45, {'writeKey': '3209ffa1xxxxxxxx', 'd1': 55.29296666666666, 'd2': 45}
Temperature = 54.4, PWM(14)= 25, {'writeKey': '3209ffa1xxxxxxxx', 'd1': 54.44883333333332, 'd2': 25}
Temperature = 54.8, PWM(14)= 27, {'writeKey': '3209ffa1xxxxxxxx', 'd1': 54.77350000000001, 'd2': 27}
^C
KeyboardInterrupt
pi@raspberrypi:~/raspifan $
'''

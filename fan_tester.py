#!/usr/bin/env python3

###############################################################################
# fan_tester
#
#                         Copyright (c) 2021 Wataru KUNINO https://bokunimo.net
###############################################################################

# CPU温度の制御の様子をセンサ値のグラフ化サイト Ambient へ送信します。
# パラメータはリスト型の配列変数 accele_list, velocity_list に代入します。
# 代入したすべての組み合わせでテストが実行されます。
# 5分間、CPUの負荷を高めて、その後15分間の測定を実行します。
# 測定結果は、Ambientへの送信、UDPブロードキャスト送信、ファイル、コンソール表示で出力します。
# 終了するには[Ctrl]キーを押しながら[C]を押してください。

ambient_chid='00000'                # ここにAmbientで取得したチャネルIDを入力
ambient_wkey='xxxxxxxxxxxxxxxx'     # ここにはライトキーを入力
udp_sendto = '255.255.255.255'      # UDP送信宛先
udp_port   = 1024                   # UDP送信先ポート番号
udp_suffix = '4'                    # UDP送信デバイス名に付与する番号
savedata = True                     # ファイル保存の要否
sendupd = False                     # UDP送信の要否
port = 14                           # GPIO ポート番号 = 14 (8番ピン)
temp_target = 60                    # ファンをOFFにする温度(℃)
accele_list = [55,45,35,25,15]      # 温度1℃あたりのファン速度
velocity_list = [30,25,20]          # 平衡時のファン速度
duty_min = 25                       # 最小Duty(ファン動作可能電圧)
period = 30                         # 制御間隔(秒) ※30秒以上

from RPi import GPIO                            # GPIOモジュールの取得
from time import sleep                          # スリープ実行モジュールの取得
from time import time
import datetime                                         # 日時・時刻用ライブラリ
import socket                                           # IP通信用ライブラリ
GPIO.setmode(GPIO.BCM)                          # ポート番号の指定方法の設定
GPIO.setup(port, GPIO.OUT)                      # ポートportのGPIOを出力に設定
pwm = GPIO.PWM(port, 50)                        # 50Hzを設定
pwm.start(0)

import urllib.request                           # HTTP通信ライブラリを組み込む
import json                                     # JSON変換ライブラリを組み込む

filename = '/sys/class/thermal/thermal_zone0/temp' # 温度値が書かれたファイル
url_s = 'https://ambidata.io/api/v2/channels/'+ambient_chid+'/data' # アクセス先
head_dict = {'Content-Type':'application/json'} # ヘッダを変数head_dictへ
body_dict = {'writeKey':ambient_wkey, \
    'd1':None, 'd2':None, 'd3':None, 'd4':None, 'd5':None}
duty = 0                                        # PWM制御値(Duty比) 0～100

def udp_sender(udp):
  if udp is None or len(udp) < 8:
    return
  if savedata:
    if udp[5] == '_' and udp[7] == ',':
      save(udp[0:7] + '.csv', udp[7:])
  if sendupd == False:
    return
  if udp_port <= 0:
    return
  try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # ソケットを作成
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
  except Exception as e:                                  # 例外処理発生時
    print('ERROR:',e)                                   # エラー内容を表示
    exit()                                              # プログラムの終了
  if sock:                                                # 作成に成功したとき
    udp = udp.strip('\r\n')                             # 改行を削除してudpへ
    print('\nUDP/' + udp_sendto + '/' + str(udp_port), '=', udp)
    udp=(udp + '\n').encode()                           # 改行追加とバイト列変換
    sock.sendto(udp,(udp_sendto, udp_port))             # UDPブロードキャスト送信
    sock.close()                                        # ソケットの切断

def udp_sender_sensor(body_dict):
  d1 = body_dict.get('d1')
  d2 = body_dict.get('d2')
  d3 = body_dict.get('d3')
  d4 = body_dict.get('d4')
  d5 = body_dict.get('d5')
  udp_sender(\
    'pufan_' + udp_suffix + ','\
    + str(round(d1,2)) + ' ,'\
    + str(d2) + ' ,'\
    + str(d3) + ' ,'\
    + str(d4) + ' ,'\
    + str(d5)\
  )

def sendToAmbient(ambient_chid, head_dict, body_dict):
  print('\nto Ambient:')
  print('    body',body_dict)                   # 送信内容body_dictを表示
  if int(ambient_chid) != 0:
    post = urllib.request.Request(\
      url_s, json.dumps(body_dict).encode(), head_dict\
    )                                           # POSTリクエストデータを作成
    try:                                        # 例外処理の監視を開始
      res = urllib.request.urlopen(post)        # HTTPアクセスを実行
    except Exception as e:                      # 例外処理発生時
      print('ERROR:',e,url_s)                   # エラー内容と変数url_sを表示
      return
    res_str = res.read().decode()               # 受信テキストを変数res_strへ
    res.close()                                 # HTTPアクセスの終了
    if len(res_str):                            # 受信テキストがあれば
      print('    Response:', res_str)           # 変数res_strの内容を表示
    else:
      print('    Done')                         # Doneを表示
  else:
    print('    チャネルID(ambient_chid)が設定されていません')

def save(filename, csv):                        # CSVデータをファイルに保存する
  try:                                          # 例外の監視を開始
    fp = open(filename, mode='a')               # 書込用ファイルを開く
  except Exception as e:                        # 例外処理発生時
    print('ERROR:',e)                           # エラー内容を表示
  s = datetime.datetime.today().strftime('%Y/%m/%d %H:%M')  # 日時を取得
  fp.write(s + csv + '\n')                      # sとcsvをファイルへ
  fp.close()                                    # ファイルを閉じる

def noop():
    return None

def target_temp(target):
  try:                      # キー割り込みの監視を開始
    duty = 0
    j=0
    for j in range(60): # 5分 5×60
      temp = 0                # 温度を保持する変数tempを生成
      for i in range(5):         # 繰り返し処理(回数=period)
        fp = open(filename)         # 温度ファイルを開く
        temp += float(fp.read()) / 1000   # ファイルを読み込み1000で除算
        fp.close()              # ファイルを閉じる
        if duty < duty_min:
          t = time() + 1.0
          while time() < t:
            noop()
        else:
          sleep(1)              # 1秒間の待ち時間処理
      temp /= 5              # 平均値を算出
      print('Temperature =', round(temp,1), end=', ') # 温度を表示する
      if temp - target < -0.3:
        duty = 0
      elif temp - target > 0.3:
        duty = duty_min
      else:
        duty = 0
      print('PWM('+str(port)+')=', str(duty)) # ポート番号と変数dutyの値を表示
      pwm.ChangeDutyCycle(duty)         # 変数dutyの値をGPIO出力
      if j%6 == 5:
        # Ambientへの送信部
        body_dict['d1'] = temp
        body_dict['d2'] = duty
        body_dict['d3'] = 0
        body_dict['d4'] = 0
        body_dict['d5'] = j
        udp_sender_sensor(body_dict)
        sendToAmbient(ambient_chid, head_dict, body_dict)
  except KeyboardInterrupt as e:
    raise e

try:                                            # キー割り込みの監視を開始
  for i in range(6):
    target_temp(70)
  for velocity in velocity_list:
    for accele in accele_list:
      target_temp(68)
      for j in range(30): # 15分 0.5分×30
        temp = 0                                # 温度を保持する変数tempを生成
        for i in range(period):                 # 繰り返し処理(回数=period)
          fp = open(filename)                   # 温度ファイルを開く
          temp += float(fp.read()) / 1000       # ファイルを読み込み1000で除算
          fp.close()                            # ファイルを閉じる
          sleep(1)                              # 1秒間の待ち時間処理
        temp /= period                          # 平均値を算出
        print('Temperature =', round(temp,1), end=', ') # 温度を表示する
        duty = (temp - temp_target) * accele + velocity # 出力dutyを算出
        duty = round(duty)                      # 変数dutyの値を整数に丸める
        if duty <= 0:                           # 目標以下なので冷却不要
          duty = 0                              # PWM Duty(ファン速度)を0に
        elif duty < duty_min:                   # ファン非動作範囲(だが要冷却)
          duty = duty_min                       # PWM Duty(ファン速度)を最小値
        elif duty > 100:                        # 最大ファン速度を超過
          duty = 100                            # PWM Duty(ファン速度)を100に
        print('PWM('+str(port)+')=', str(duty)) # ポート番号と変数dutyの値を表示
        pwm.ChangeDutyCycle(duty)               # 変数dutyの値をGPIO出力

        body_dict['d1'] = temp
        body_dict['d2'] = duty
        body_dict['d3'] = accele
        body_dict['d4'] = velocity
        body_dict['d5'] = j
        udp_sender_sensor(body_dict)
        sendToAmbient(ambient_chid, head_dict, body_dict)

except KeyboardInterrupt:                       # キー割り込み発生時
  print('\nKeyboardInterrupt')                  # キーボード割り込み表示
  GPIO.cleanup(port)                            # GPIOを未使用状態に戻す
  exit()

try:                                            # キー割り込みの監視を開始
  while True:
    pwm.ChangeDutyCycle(50)
    sleep(60)

except KeyboardInterrupt:                       # キー割り込み発生時
  print('\nKeyboardInterrupt')                  # キーボード割り込み表示
  GPIO.cleanup(port)                            # GPIOを未使用状態に戻す
  exit()                                        # 終了


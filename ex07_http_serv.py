#!/usr/bin/env python3

###############################################################################
# Example 7 HTTP Server for Servo PWM Control
#
#                         Copyright (c) 2021 Wataru KUNINO https://bokunimo.net
###############################################################################

# ラズベリー・パイに接続した Tower Pro製 マイクロ・サーボモータSG90を
# インターネット・ブラウザ等から入力した角度の位置に回転して合わせます。
# 同じラズベリーパイ上の別のLXTerminalで「curl http://127.0.0.1:8080/?=90」の
# ようにアクセスします。?=の数字はサーボへの指示角です。
# 他のPCのインターネットブラウザからラズベリーパイのIPアドレスを指定して、
# 「http://192.168.XX.XX:8080/?=180」のようにアクセスすることも出来ます。
# 終了するには[Ctrl]キーを押しながら[C]を押してください。

port = 14                                       # GPIO ポート番号=14 (8番ピン)
duty_min = 2.7                                  # 180°のときのPWMのDuty比
duty_max = 13.0                                 # 0°のときのPWMのDuty比

from wsgiref.simple_server import make_server   # HTTPサーバ用モジュールの取得
from RPi import GPIO                            # GPIOモジュールの取得
from time import sleep                          # sleepモジュールの取得
GPIO.setmode(GPIO.BCM)                          # ポート番号の指定方法の設定
GPIO.setup(port, GPIO.OUT)                      # ポートportのGPIOを出力に設定
pwm = GPIO.PWM(port, 50)                        # 50Hzを設定
pwm.start(0)                                    # PWM出力 0% (Lレベル)

def deg2duty(deg):                              # Duty比を計算する関数
    return (duty_max - duty_min) * (180 - deg) / 180 + duty_min

Res_Text = [('Content-type', 'text/plain; charset=utf-8')]

def wsgi_app(environ, start_response):          # HTTPアクセス受信時の処理
    val = None                                  # 取得値を保持するための変数
    query = environ.get('QUERY_STRING')         # 変数queryにHTTPクエリを代入
    sp = query.find('=')                        # 変数query内の「=」を探す
    if sp >= 0 and sp + 1 < len(query):         # 「=」の発見位置が有効範囲内
        if query[sp+1:].isdigit():              # 取得値(指示角)が整数値の時
            val = int(query[sp+1:])             # 取得値を変数valへ
            val %= 181                          # 181(°)の剰余を代入
    if val is not None:
        duty = round(deg2duty(val),1)           # 角度値をデューティに変換
        print('Value =',val,', Duty = ',duty)   # 取得値(指示角)とDuty比を表示
        pwm.ChangeDutyCycle(duty)               # サーボの制御を実行
        sleep(0.36 + 1 / 50)                    # 回転待ち時間
        pwm.ChangeDutyCycle(0)                  # サーボの制御を停止
        ok = 'Value=' + str(val) + ' (' + str(duty) + ')\r\n' # 応答文
        ok = ok.encode('utf-8')                 # バイト列へ変換
        start_response('200 OK', Res_Text)
        return [ok]                             # 応答メッセージを返却
    else:
        start_response('400 Bad Request', Res_Text)
        return ['Bad Request\r\n'.encode()]     # 応答メッセージを返却

try:
    httpd = make_server('', 80, wsgi_app)       # TCPポート80でHTTPサーバ実体化
    print("HTTP port 80")                       # ポート確保時,ポート番号を表示
except PermissionError:                         # 例外処理発生時(アクセス拒否)
    httpd = make_server('', 8080, wsgi_app)     # ポート8080でHTTPサーバ実体化
    print("HTTP port 8080")                     # 起動ポート番号の表示
try:
    httpd.serve_forever()                       # HTTPサーバを起動
except KeyboardInterrupt:                       # キー割り込み発生時
    print('\nKeyboardInterrupt')                # キーボード割り込み表示
    GPIO.cleanup(port)                          # GPIOを未使用状態に戻す
    exit()                                      # プログラムの終了

'''
pi@raspberrypi:~ $ git clone https://bokunimo.net/git/raspifan ⏎
　～～～～～～～～～～～～～～～～～～(省略)～～～～～～～～～～～～～～～～～
pi@raspberrypi:~ $ cd raspifan ⏎
pi@raspberrypi:~/raspifan $ ./ex07_http_serv.py ⏎
HTTP port 8080

　～～～～ (別のLXTerminalで「curl http://127.0.0.1:8080/?=0」を入力) ～～～～
Value = 0 , Duty =  13.0
127.0.0.1 - - [31/Jul/2021 19:22:02] "GET /?=0 HTTP/1.1" 200 16

　～～～～～～～～～(PCのインターネットブラウザからアクセス)～～～～～～～～～
Value = 0 , Duty =  13.0
192.168.1.3 - - [31/Jul/2021 19:22:28] "GET /?=0 HTTP/1.1" 200 16
192.168.1.3 - - [31/Jul/2021 19:22:28] "GET /favicon.ico HTTP/1.1" 400 13
Value = 90 , Duty =  7.9
192.168.1.3 - - [31/Jul/2021 19:22:34] "GET /?=90 HTTP/1.1" 200 16
Value = 180 , Duty =  2.7
192.168.1.3 - - [31/Jul/2021 19:22:47] "GET /?=180 HTTP/1.1" 200 16
^C
KeyboardInterrupt
pi@raspberrypi:~/raspifan $
'''

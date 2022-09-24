#!/usr/bin/env python3

###############################################################################
# Example 8 Heat Dissipation Mechanism for Raspberry Pi
#
#                        Copyright (c) 2021 Wataru KUNINO https://bokunimo.net/
###############################################################################

# ラズベリー・パイのCPU温度が60℃を超えたときに Tower Pro製 マイクロ・サーボ
# SG90を制御し、ケースの上蓋を開いて排熱します。
# インターネット・ブラウザから、CPU温度の確認と、上蓋の開閉制御を行うことも
# 可能です。

# インターネット・ブラウザ等から http://127.0.0.1:8080/ にアクセスして下さい。
# 他のPCのインターネットブラウザからラズベリーパイのIPアドレスを指定して、
# 「http://192.168.XX.XX:8080/」のようにアクセスすることも出来ます。
# 終了するには[Ctrl]キーを押しながら[C]を押してください。

port = 14                                       # GPIO ポート番号=14 (8番ピン)
duty_min = 3.0                                  # 180°のときのPWMのDuty比
duty_max = 11.8                                 # 0°のときのPWMのDuty比
cover_closed_deg = 150                          # ケースが閉じているときの角度
cover_opened_deg = 90                           # ケースが開いているときの角度
cover_status = cover_closed_deg                 # ケース状態の初期値を閉じに
temp_emit_on = 60                               # 放熱をON(ケース開)する温度
temp_emit_off = 55                              # 放熱をOFF(ケース閉)する温度

from wsgiref.simple_server import make_server   # HTTPサーバ用モジュールの取得
from RPi import GPIO                            # GPIOモジュールの取得
from time import sleep                          # sleepモジュールの取得
import threading                                # スレッド管理を組み込む

def deg2duty(deg):                              # Duty比を計算する関数
    return (duty_max - duty_min) * (180 - deg) / 180 + duty_min

def coverCtrl(deg):                             # 角度degにサーボを制御する関数
    global cover_status                         # cover_statusの取得(Thread用)
    print('coverCtrl :',cover_status,'->',deg)  # 制御前の値と指示値を表示
    pwm.ChangeDutyCycle(deg2duty(deg))          # Duty比に変換しサーボを制御
    cover_status = deg                          # 状態を更新
    sleep(0.36 + 1 / 50)                        # 回転待ち時間
    pwm.ChangeDutyCycle(0)                      # サーボの制御を停止

filename = '/sys/class/thermal/thermal_zone0/temp' # 温度値が書かれたファイル

def getTemp():
    fp = open(filename)                         # CPU温度ファイルを開く
    temp = round(float(fp.read()) / 1000,1)     # ファイルを読み込み1000で除算
    fp.close()                                  # ファイルを閉じる
    print('CPU Temperature =', temp)            # CPU温度を表示する
    return temp                                 # CPU温度値を返却する

def barChart(name, val, max, color='green'):    # 棒グラフHTMLを作成する関数
    html = '<tr><td>' + name + '</td>\n'        # 棒グラフ名を表示
    html +='<td align="right">'+str(val)+'</td>\n' # 変数valの値を表示
    i = round(200 * val / max)                  # 棒グラフの長さを計算
    if val >= max * 0.75:                       # 75％以上のとき
        color = 'red'                           # 棒グラフの色を赤に
        if val > max:                           # 最大値(100％)を超えた時
            i = 200                             # グラフ長を200ポイントに
    html += '<td><div style="background-color:' + color
    html += '; width:' + str(i) + 'px">&nbsp;</div></td>\n'
    return html                                 # HTMLデータを返却

def wsgi_app(environ, start_response):          # HTTPアクセス受信時の処理
    global cover_status                         # cover_statusの取得(Thread用)
    path  = environ.get('PATH_INFO')            # リクエスト先のパスを代入
    query = environ.get('QUERY_STRING')         # 変数queryにHTTPクエリを代入
    if path != '/':                             # パスがルート以外のとき
        start_response('404 Not Found',[])      # 404エラー設定
        return ['404 Not Foundt\r\n'.encode()]  # 応答メッセージ(404)を返却
    sp = query.find('=')                        # 変数query内の「=」を探す
    if sp >= 0 and sp + 1 < len(query):         # 「=」の発見位置が有効範囲内
        if query[sp+1:].isdigit():              # 取得値(指示角)が整数値の時
            val = int(query[sp+1:])             # 取得値を変数valへ
            val %= 2                            # 2の剰余を代入
            if val == 0 and cover_status == cover_opened_deg:
                coverCtrl(cover_closed_deg)     # ケースを閉じる
            elif val == 1 and cover_status == cover_closed_deg:
                coverCtrl(cover_opened_deg)     # ケースを開く
    temp = getTemp()                            # 温度を取得
    html = '<html>\n<head>\n'                   # HTMLコンテンツを作成
    html += '<meta http-equiv="refresh" content="10;URL=/">\n' # 自動更新
    html += '</head>\n<body>\n'                 # 以下はHTML本文
    html += '<table border=1>\n'                # 作表を開始
    html += '<tr><th>項目</th><th width=50>値</th>' # 「項目」「値」を表示
    html += '<th width=200>グラフ</th>\n'       # 「グラフ」を表示
    html += barChart('CPU温度(℃)', temp, 80)   # 温度値を棒グラフ化
    html += barChart('ケース状態', int(cover_status == cover_opened_deg), 1) 
    # html += barChart('サーボ角(°)', cover_status, 180)  # 現在の角度を表示
    html += '</tr>\n</table>\n'                 # 作表の終了
    html += 'ケース制御 <a href="/?=0">閉じる</a> <a href="/?=1">開く</a>'
    html += '</body>\n</html>\n'                # htmlの終了
    start_response('200 OK', [('Content-type', 'text/html; charset=utf-8')])
    return [html.encode('utf-8')]               # 応答メッセージを返却

def httpd():                                    # HTTPサーバ用スレッド
    try:                                        # 例外処理の監視
        htserv = make_server('', 80, wsgi_app)  # HTTPサーバ実体化
        print('HTTP port', port)                # ポート番号を表示
    except PermissionError:                     # 例外処理発生時(アクセス拒否)
        htserv = make_server('', 8080,wsgi_app) # ポート8080でHTTPサーバ実体化
        print("HTTP port 8080")                 # 起動ポート番号の表示
    try:                                        # 例外処理の監視
        htserv.serve_forever()                  # HTTPサーバを起動
    except KeyboardInterrupt as e:              # キー割り込み発生時
        raise e                                 # キー割り込み例外を発生

GPIO.setmode(GPIO.BCM)                          # ポート番号の指定方法の設定
GPIO.setup(port, GPIO.OUT)                      # ポートportのGPIOを出力に設定
pwm = GPIO.PWM(port, 50)                        # 50Hzを設定
pwm.start(0)                                    # PWM出力 0% (Lレベル)
sleep(1/50)                                     # 待ち時間
coverCtrl(cover_status)                         # ケースを閉じる

try:
    thread = threading.Thread(target=httpd, daemon=True) # httpdの実体化
    thread.start()                              # httpdの起動
    while thread.is_alive:                      # 永久ループ
        temp = getTemp()                        # 温度値を取得
        if temp >= temp_emit_on and cover_status == cover_closed_deg:
        # 放出温度に達していて、かつケースが閉じていた時
                coverCtrl(cover_opened_deg)     # ケースを開く
        if temp <= temp_emit_off and cover_status == cover_opened_deg:
        # 放出停止温度以下、かつケースが開いていた時
                coverCtrl(cover_closed_deg)     # ケースを閉じる
        sleep(30)                               # 30秒間の待ち時間処理

except KeyboardInterrupt:                       # キー割り込み発生時
    print('\nKeyboardInterrupt')                # キーボード割り込み表示
    GPIO.cleanup(port)                          # GPIOを未使用状態に戻す
    exit()                                      # プログラムの終了

'''
pi@raspberrypi:~ $ git clone https://bokunimo.net/git/raspifan ⏎
　～～～～～～～～～～～～～～～～～～(省略)～～～～～～～～～～～～～～～～～
pi@raspberrypi:~ $ cd raspifan ⏎
pi@raspberrypi:~/raspifan $ ./ex08_emission.py ⏎
overCtrl : 150 -> 150
CPU Temperature = 58.0
HTTP port 8080

　～～～～ (別のLXTerminalで「curl http://127.0.0.1:8080/?=1」を入力) ～～～～
coverCtrl : 150 -> 90
CPU Temperature = 58.5
127.0.0.1 - - [01/Aug/2021 12:15:59] "GET /?=1 HTTP/1.1" 200 513

　～～～～～～～～ (「curl http://127.0.0.1:8080/?=1」を入力) ～～～～～～～～
coverCtrl : 90 -> 150
CPU Temperature = 58.0
127.0.0.1 - - [01/Aug/2021 12:16:09] "GET /?=0 HTTP/1.1" 200 513

　～～～～～～～～～(PCのインターネットブラウザからアクセス)～～～～～～～～～
192.168.1.3 - - [01/Aug/2021 12:16:48] "GET / HTTP/1.1" 200 513
192.168.1.3 - - [01/Aug/2021 12:16:48] "GET /favicon.ico HTTP/1.1" 404 16
CPU Temperature = 57.5
192.168.1.3 - - [01/Aug/2021 12:16:58] "GET / HTTP/1.1" 200 513
CPU Temperature = 57.5
192.168.1.3 - - [01/Aug/2021 12:17:08] "GET / HTTP/1.1" 200 513

　～～～～～～～～～～～～ (CPU温度が60℃に達した時)～～～～～～～～～～～～～
CPU Temperature = 59.1
CPU Temperature = 58.5
CPU Temperature = 59.6
CPU Temperature = 60.1
coverCtrl : 150 -> 90
^C
KeyboardInterrupt
pi@raspberrypi:~/raspifan $
'''

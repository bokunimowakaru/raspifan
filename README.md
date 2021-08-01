# raspifan
GPIO Control Example Code for Raspberry Pi FAN

## Example 1 FAN ON/OFF (ex01_gpio.py)  
キーボードから1⏎を入力するとFANが回転、0⏎を入力すると停止します。  

## Example 2 FAN AUTO ON/OFF (ex02_auto.py)  
CPU温度が60℃以上でFANを回転、55℃以下で停止するファンの自動制御を行います。  

## Example 3 FAN PWM Control (ex03_pwm.py)  
CPU温度が55℃以下に抑えるようにファン速度をPWMで調整します。  

## Example 4 Temperature to Ambient  (ex04_ambient.py)  
CPU温度によるファン制御の様子を Ambient へ送信します。
温度や制御の推移をスマホで確認することが出来るようになります。  

## Example 5 Servo PWM Control (ex05_servo.py)  
Tower Pro製 マイクロ・サーボモータSG90をキーボードから入力した角度の位置に回転して合わせます。  

## Example 6 Servo Velocity Control (ex06_velocity.py)  
予め設定した速度でサーボモータを定速回転させ、入力した角度の位置で止めます。
回転速度を下げることで回転中の消費電流を減らすことが出来ます。  

## Example 7 HTTP Server for Servo PWM Control (ex07_http_serv.py)
サーボモータをインターネット・ブラウザ等から入力した角度の位置に回転して合わせます。  

## Example 8 Heat Dissipation Mechanism for Raspberry Pi (ex08_emission.py)
CPU温度が60℃を超えたときに サーボモータを制御し、ケースの上蓋を開いて排熱します。
また、インターネット・ブラウザ等から開閉制御を行うことも出来ます。  

本ドキュメントの保存先：  
	https://bokunimo.net/git/raspifan/  

ダウンロード方法：  
	git clone https://bokunimo.net/git/raspifan  

Copyright (c) 2021 Wataru KUNINO https://bokunimo.net/  


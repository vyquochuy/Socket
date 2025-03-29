import os
from socket import *
import base64
from send_email import *
from reciept_email import *

with open('config.json', 'r') as file:
    config_data = json.load(file)

HOST = config_data["MailServer"]
SMTP_port = config_data["SMTP"]
POP3_port = config_data["POP3"]

def main():
    username = input("Tên Đăng Nhập: ")
    password = input("Mật Khẩu: ")
    base64_str = ("\x00"+username+"\x00"+password).encode()
    base64_str = base64.b64encode(base64_str)
    #có sẵn user_
    while True:
        print("\nVui lòng chọn Menu:")
        print("1. Để gửi email")
        print("2. Để xem danh sách các email đã nhận")
        print("3. Để thay đổi tài khoản")
        print("4. Thoát")

        choice = input("\nBạn chọn: ")

        if choice == '1':

            send_email(HOST, SMTP_port, username, password)
            #reciept_email()
        elif choice == '2':
            #print("Chức năng này chưa được triển khai.")
            reciept_email(HOST, POP3_port, username, password)
        elif choice == '3':
            username = input("Nhập địa chỉ: ")
            password = input("Nhập mật khẩu: ")
        elif choice == '4':
            print("Tạm biệt.")
            break
        else:
            print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")



main()



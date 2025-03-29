from socket import socket, AF_INET, SOCK_STREAM
import base64
import re
from datetime import datetime
import os
import math
import json


with open('config.json', 'r') as file:
    config_data = json.load(file)

Project = config_data["Project"]
Important = config_data["Important"]
Work = config_data["Work"]
Spam = config_data["Spam"]

class Email:
    def __init__(self, header="", body=""):
        self.header = header
        self.body = body

    def set_content(self, header, body):
        self.header = header
        self.body = body

    def display(self):
        print("Header:")
        print(self.header)
        print("Body:")
        print(self.body)
    def save_to_file(self, file_path, key):
        with open(file_path, 'w') as file:
            file.write(key + '\n')
            file.write(self.header + '\n\n' + key + '\n')
            file.write(self.body)

class File:
    def __init__(self, name, data):
        self.name = name
        self.data = data

    def append_to_file(self, file_path, key):
        try:
            # Mở hoặc tạo một file với tên là 'file_path' trong chế độ ghi tiếp ('a')
            with open(file_path, 'a') as file:
                # Ghi dữ liệu vào file
                file.write('\n' + key + '\n')
                file.write('file_name:' + self.name + '\n')
                file.write(self.data)
            print(f"Dữ liệu đã được ghi tiếp vào file '{self.name}' thành công.")
        except Exception as e:
            print(f"Có lỗi xảy ra: {e}")

def lay_tu_pha_sau_key_cuoi_cung(data, key):
    vi_tri_cuoi_cung = data.rfind(key)

    if vi_tri_cuoi_cung != -1:
        tu_pha_sau_key_cuoi_cung = data[vi_tri_cuoi_cung + len(key):]
        
        header_body = '\n\n\n\nContent-Type: text/plain\nContent-Transfer-Encoding: 7bit\n\n\n'
        end_body ='\n.\n\n'
        
        tu_pha_sau_key_cuoi_cung = tu_pha_sau_key_cuoi_cung[len(header_body): -len(end_body)]
        
        return tu_pha_sau_key_cuoi_cung
    else:
        return None

def lay_key_den_cuoi_cung(data, key):
    index = data.rfind(key)

    if index != -1:
        file_str = data[index:] 
        return file_str
    else:
        return None

def extract_data_between_keys(data, key):
    key_count = data.count(key)

    if key_count % 2 != 0:
        print("Số lượng key không phải số chẵn.")
        return

    extracted_data_list = []
    index_key = 0
    for i in range(0, 2):
        start_index = data.find(key, index_key)
        end_index = data.find(key, start_index + 1)
        index_key = end_index
        
        if start_index != -1 and end_index != -1:
            extracted_data = data[start_index + len(key):end_index].strip()
            extracted_data_list.append(extracted_data)


    for i in range(2, key_count + 1, 2):
        start_index = data.find(key, index_key)
        end_index = data.find(key, start_index + 1)
        index_key = end_index + 1
        
        if start_index != -1 and end_index != -1:
            extracted_data = data[start_index + len(key):end_index].strip()
            extracted_data_list.append(extracted_data)
    
    return extracted_data_list
        
def management_file(user_name):
    file_name = user_name + '_count_email.txt'
    
    try:
        # Thử đọc tệp tin nếu tồn tại
        with open(file_name, 'r') as file:
            count = int(file.read())
    except FileNotFoundError:
        # Tệp không tồn tại, tạo tệp và ghi số 0 vào đó
        count = 0
        # Lấy đường dẫn của mã nguồn
        source_directory = os.path.dirname(os.path.abspath(__file__))
        # Tạo đường dẫn cho thư mục "mai_box"
        emai_box_directory = os.path.join(source_directory, 'count_email')
        
        # Kiểm tra nếu thư mục "mai_box" chưa tồn tại, tạo mới
        if not os.path.exists(emai_box_directory):
            os.makedirs(emai_box_directory)
        
        # Tạo đường dẫn tuyệt đối cho file mới trong thư mục "mai_box"
        file_name = os.path.join(emai_box_directory, file_name)
        
        # Ghi số 0 vào tệp tin mới tạo
        with open(file_name, 'w') as file:
            file.write(str(count))
    
    return count

def write_mail_box(user_name, count):
    file_name = user_name + '_count_email.txt'
    # Lấy đường dẫn của mã nguồn
    source_directory = os.path.dirname(os.path.abspath(__file__))
    # Tạo đường dẫn cho thư mục "mai_box"
    emai_box_directory = os.path.join(source_directory, 'count_email')
    
    # Kiểm tra nếu thư mục "mai_box" chưa tồn tại, tạo mới
    if not os.path.exists(emai_box_directory):
        os.makedirs(emai_box_directory)
    
    # Tạo đường dẫn tuyệt đối cho file mới trong thư mục "mai_box"
    file_name = os.path.join(emai_box_directory, file_name)
    try:
        with open(file_name, 'w') as file:
            file.write(str(count))
    except Exception as e:
        print(f"Error writing to {file_name}: {e}")

# Hàm tạo file với data, tên file.txt và địa chỉ
def save_email_to_file(email_content, email_name, place):
    # Nhận đường dẫn thư mục từ người dùng
    directory_path = place

    # Tạo thư mục nếu nó không tồn tại
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # Tạo đường dẫn tập tin
    file_path = os.path.join(directory_path, (email_name + ".txt"))

    # Lưu nội dung email vào tập tin
    with open(file_path, 'w') as file:
        file.write(email_content)

# Hàm để tách tên
def extract_to_name(information):
    to_line = None
    # Tìm dòng chứa thông tin đích đến (To:)
    for line in information.split('\n'):
        # Bắt đầu với 'To:'
        if line.startswith('To:'): 
            to_line = line
            break

    if to_line:
        # Tách chuỗi dựa trên dấu ':' và xóa khoảng trắng dư thừa
        to_parts = to_line.split(': ')
        if len(to_parts) > 1:
            # Tách các địa chỉ email trong trường 'To'
            to_emails = to_parts[1].strip().split(',')  
            # Lấy tên từ địa chỉ email
            to_names = []
            for email in to_emails:
                email = email.strip()
                if '@' in email:  # Kiểm tra xem có dấu '@' trong địa chỉ email không
                    name = email.split('@')[0]
                    to_names.append(name)
                else:
                    to_names.append(email)  # Nếu không có dấu '@' thì coi toàn bộ là tên

            return to_names
        else:
            print("Không tìm thấy địa chỉ email trong dòng 'To:'")
            return None
    else:
        print("Không tìm thấy thông tin 'To:' trong phần thông tin của email")
        return None

# Hàm để tách Subject
def extract_to_subject(information):
    to_line = None
    # Tìm dòng chứa thông tin đích đến (To:)
    for line in information.split('\n'):
        # Bắt đầu với 'To:'
        if line.startswith('Subject:'): 
            to_line = line
            break

    if to_line:
        # Tách chuỗi dựa trên dấu ':' và xóa khoảng trắng dư thừa
        to_sub = to_line.split(':')
        if len(to_sub) > 1: 
            return to_sub
        else:
            print("Không tìm thấy tiêu đề trong dòng 'Subject:'")
            return None
    else:
        print("Không tìm thấy thông tin 'Subject:' trong phần thông tin của email")
        return None
    
# Hàm để tách Date
def extract_to_date(information):
    to_line = None
    # Tìm dòng chứa thông tin đích đến (Date:)
    for line in information.split('\n'):
        # Bắt đầu với 'Date:'
        if line.startswith('Subject:'): 
            to_line = line
            break

    if to_line:
        # Tách chuỗi dựa trên dấu ':' và xóa khoảng trắng dư thừa
        to_date = to_line.split(': ')
        if len(to_date) > 1: 
            return to_date
        else:
            print("Không tìm thấy thời gian trong dòng 'Date:'")
            return None
    else:
        print("Không tìm thấy thông tin 'Date:' trong phần thông tin của email")
        return None

# Hàm tạo thư mục trong thư mục dẫn
def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
        os.chmod(folder_name, 0o777)

def is_spam(header, body):
    keys = Spam
    for key in keys:
        if key in header or key in body:
            return True
    return False

def is_project(header, add_pro):
    emails = Project
    names = []
    for email in emails:
        email = email.strip()
        if '@' in email:  # Kiểm tra xem có dấu '@' trong địa chỉ email không
            name = email.split('@')[0]
            names.append(name)
        else:
            names.append(email)  # Nếu không có dấu '@' thì coi toàn bộ là tên 

    for name in names:
        if name in header:
            return True
        
    return False
    
def is_important(header, add_im):
    keys = Important
    for key in keys:
        if key in header:
            return True
        
    return False

def is_work(body, add_wrk):
    keys = Work
    for key in keys:
        if key in body:
            return True
        
    return False

def check_type(header, body, add_pro, add_im, add_wrk, add_spam, add_in):
    if is_spam(header, body) == True:
        return add_spam
    elif is_project(header, add_pro) == True:
        return add_pro
    elif is_important(header, add_im) == True:
        return add_im
    elif is_work(body, add_wrk) == True:
        return add_wrk
    else:
        return add_in
    
def email_processing(email_info, user_name, number, add_pro, add_im, add_wrk, add_spam, add_in):

    # Sử dụng biểu thức chính quy để tìm giá trị của boundary
    boundary_match = re.search(r'boundary="([^"]+)"', email_info)

    # Lấy giá trị boundary nếu tìm thấy
    if boundary_match:
        boundary_value = boundary_match.group(1)
    else:
        print("Không tìm thấy giá trị của boundary.")
        return

    # Key cần tìm
    key = boundary_value
    
    count_key = email_info.count(key)

    if count_key == 2:
        start_index = email_info.find(key)
        end_index = email_info.find(key, start_index + len(key))
        header = email_info[start_index + len(key):end_index].strip()
        header = header[3:]
        
        body = lay_tu_pha_sau_key_cuoi_cung(email_info, key).strip()
        print("Nội dung của bức thư gồm:")
        print(header)
        print(body)
        result_email = Email()
        result_email.set_content(header, body)
        writed = False
 
        # Kiểm tra và tạo thư mục nếu chưa tồn tại
        folder_add = check_type(header, body, add_pro, add_im, add_wrk, add_spam, add_in)
        file_name = user_name + '_' + str(number) + '_email.txt'
        file_path = os.path.join(folder_add, file_name)

        result_email = ''
        result_email = header + '\n' + body

        with open(file_path, "w") as file:
            file.write(result_email)
        
    else:
        block_list = extract_data_between_keys(email_info, key)
        list_length = len(block_list)
        '''for index, email in enumerate(block_list):
            print(f"Chỉ số {index}: {email}")'''
        
        # đoạn này xử lí thủ công
        header = block_list[0][3:].strip()
        
        start_body = block_list[1].find('7bit') + len('7bit')
        body = block_list[1][start_body:].strip()
        
        print("Nội dung của bức thư gồm:")
        print(header)
        print(body)
        
        folder_add = check_type(header, body, add_pro, add_im, add_wrk, add_spam, add_in)
        file_name = user_name + '_' + str(number) + '_email.txt'
        file_path = os.path.join(folder_add, file_name)

        result_email = ''
        result_email = header + '\n' + body

        with open(file_path, "w") as file:
            file.write(result_email)
        
        file_list = []
        #print('duong dan file', file_name)
        for i in range(2, list_length):
            index1 = block_list[i].find('"')
            index2 = block_list[i].find('"', index1 + 1)
            file_name_in_mail =  block_list[i][index1 + 1:index2]
            #print(file_name_in_mail)
            file_data_in_mail = block_list[i][index2 + 2:].strip()
            #print(file_data_in_mail)
            # Tạo đối tượng File và ghi dữ liệu vào file
            email_file = File(file_name_in_mail, file_data_in_mail)
            #email_file.append_to_file(file_name, key)

            # Thêm đối tượng File vào danh sách file_list
            file_list.append(email_file)
            try:
                # Giải mã dữ liệu từ Base64
                decoded_data = base64.b64decode(file_data_in_mail)
                place_downloads = os.path.join('Downloads', file_name_in_mail)
                # Ghi dữ liệu vào file mới
                with open(place_downloads, 'wb') as new_file:
                    new_file.write(decoded_data)

            except Exception as e:
                print(f"Lỗi: {e}")

# Đây là hàm để in ra danh sách các mail trong folder file_path và lưu danh sách các địa chỉ đó để in ra khi cần
def in_cac_mail_trong_thu_muc(file_path):
    print("Đây là danh sách các email có trong " + file_path + " của bạn: <người gửi>_<tiêu đề>_<thời gian gửi>")
    contents = os.listdir(file_path)
    emails_add = []
    if contents:
        i = 0
        for content in contents:
            i = i + 1
            email_add = file_path + "\\" + content
            with open(email_add, "rb") as f:
                name = extract_to_name(f)
                sub = extract_to_subject(f)
                date = extract_to_date(f)
                set_name = name + "_" + sub + "_" + date

            print(str(i) + "." + set_name)
            emails_add.append(set_name)

        return emails_add
    else:
        print("Thư mục " + file_path + " hiện đang rỗng!.")

# Đây là hàm để in ra các thư mục con trong Process
def in_thu_muc_con(file_path):
    print("Đây là danh sách các thư mục có trong " + file_path + " của bạn: ")
    contents = os.listdir(file_path)
    folder_add = []
    if contents:
        i = 0
        for content in contents:
            add = file_path + "\\" + content
            i += 1
            print(str(i) + "." + content)
            folder_add.append(add)
        return folder_add
    else:
        print("Thư mục " + file_path + " hiện đang rỗng!.")
    
#Hàm để in mail ra dưới tên <Tên người gửi>_<tiêu đề>_<thời gian gửi>, lỗi 
def in_mail_tu_link(link):
    a = 0
    
# Đây là hàm đẻ chạy tổng hợp các hàm in ở trên, lỗi
def print_menu_mail(add_process, add_pro, add_im, add_wrk, add_spam, add_in):
    mailbox_folder = in_thu_muc_con(add_process)
    check = int(input("Bạn muốn xem thư mục nào: "))
    while check:
        if 'Spam' in mailbox_folder[check - 1]:
            spam_folder = in_cac_mail_trong_thu_muc(add_spam)
            if spam_folder:
                check_ = int(input("Bạn muốn xem mail thứ mấy: "))
                in_mail_tu_link(spam_folder[check_ - 1])

        elif 'Project' in mailbox_folder[check - 1]:
            project_folder = in_cac_mail_trong_thu_muc(add_pro)
            if project_folder:
                check_ = int(input("Bạn muốn xem mail thứ mấy: "))
                in_mail_tu_link(project_folder[check_ - 1])

        elif 'Work' in mailbox_folder[check - 1]:
            w_folder = in_cac_mail_trong_thu_muc(add_wrk)
            if w_folder:
                check_ = int(input("Bạn muốn xem mail thứ mấy: "))
                in_mail_tu_link(w_folder[check_ - 1])

        elif 'Important' in mailbox_folder[check - 1]:
            Im_folder = in_cac_mail_trong_thu_muc(add_im)
            if Im_folder:
                check_ = int(input("Bạn muốn xem mail thứ mấy: "))
                in_mail_tu_link(Im_folder[check_ - 1])


        else:
            inbox_folder = in_cac_mail_trong_thu_muc(add_in)
            if inbox_folder:
                check_ = int(input("Bạn muốn xem mail thứ mấy: "))
                in_mail_tu_link(inbox_folder[check - 1])

def reciept_email(HOST, POP3_port, user_name, user_pass):
    try:
        pop3_server = (HOST, POP3_port)
        pop3_socket = socket(AF_INET, SOCK_STREAM)
        pop3_socket.connect(pop3_server)  # OK Test Mail Server

        # Nhận phản hồi đầu tiên từ máy chủ
        response = pop3_socket.recv(1024).decode().strip()

        # Gửi lệnh USER và nhận phản hồi
        pop3_socket.sendall(f'USER {user_name}\r\n'.encode())
        response = pop3_socket.recv(1024).decode().strip()

        # Gửi lệnh PASS và nhận phản hồi
        pop3_socket.sendall(f'PASS {user_pass}\r\n'.encode())
        response = pop3_socket.recv(1024).decode().strip()

        #--------- đoạn trên dùng để tạo xong kết nối với tài khoản------------------

        # Gửi lệnh STAT để lấy thông tin về số lượng email và kích thước
        pop3_socket.sendall(b'STAT\r\n')
        response = pop3_socket.recv(1024).decode().strip()

        '''đoạn này là để lấy số lượng email trên sever và trong máy, xem email cần tải thì tải:
        #Phân tích phản hồi để lấy số lượng email
        number_email_in_sever = int(response.split()[1])
        print("Số lượng email của bạn trên server là", number_email_in_sever)
        numb_mail_in_box = management_file(user_name)
        write_mail_box(user_name, number_email_in_sever)
        print("Số lượng mail trên máy là: ", numb_mail_in_box)'''

        # In danh sách email và kích thước
        pop3_socket.sendall(b'LIST\r\n')
        response = pop3_socket.recv(1024).decode().strip() 

        add_cur = os.getcwd()

        email = user_name.strip()
        if '@' in email:  # Kiểm tra xem có dấu '@' trong địa chỉ email không
            name = email.split('@')[0]
            to_name = name
        else:
            to_name = email  # Nếu không có dấu '@' thì coi toàn bộ là tên
        
        mailbox_name = to_name + "s_" + "MailBox"
        add_process = os.path.join(add_cur, mailbox_name)
        create_folder(add_process)

        add_project = os.path.join(add_process, 'Project')
        create_folder(add_project)

        add_important = os.path.join(add_process, 'Important')
        create_folder(add_important)

        add_work = os.path.join(add_process, 'Work')
        create_folder(add_work)

        add_spam = os.path.join(add_process, 'Spam')
        create_folder(add_spam)

        add_inbox = os.path.join(add_process, 'Inbox')
        create_folder(add_inbox)
        
        add_downloads = os.path.join(add_cur, 'Downloads')
        create_folder(add_downloads)
        
        # Phân tích phản hồi để lấy danh sách email và kích thước
        email_list = response.split('\r\n')[1:-1]  # Bỏ qua dòng đầu và dòng cuối
        for email_info in email_list:
            #nếu chỉ số emal lớn hơn chỉ số emai trong hôp thư tức nó chưa được tải về -> thì tải về
            email_number, email_size = map(int, email_info.split())

            # Số lượng byte cần nhận để đảm bảo nhận đủ dữ liệu
            number_recv = math.ceil((email_size + 1) / 1024)

            # Gửi lệnh RETR để lấy nội dung email và nhận phản hồi
            pop3_socket.sendall(f'RETR {email_number}\r\n'.encode())

            # Nhận dữ liệu email trong một vòng lặp
            email_response = ""
            while number_recv > 0:
                data_chunk = pop3_socket.recv(1024).decode()
                email_response += data_chunk
                number_recv -= 1


            # Xử lý nội dung emai 
            email_processing(email_response, user_name, email_number, add_project, add_important, add_work, add_spam, add_inbox)

        #Đay là hàm đẻ in ra danh sách các folder và các mail trong folder, đang lỗi
        print_menu_mail(add_process, add_project, add_important, add_work, add_spam, add_inbox)

        # Đóng kết nối POP3
        pop3_socket.sendall(b"QUIT\r\n")
        pop3_socket.recv(1024).decode()
        pop3_socket.close()

    except Exception as e:
        print(f"LỖI: {e}")

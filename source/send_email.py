import socket, os, base64, time, random, string

def generate_message_id():
    timestamp = int(time.time())
    unique_id = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    message_id = f"<{timestamp}.{unique_id}@gmail.com>"
    return message_id

def attach_files(max_size):
    file_list = []
    numberOfFile = int(input("Số lượng file muốn gửi là: "))
    
    for i in range(numberOfFile):
        file_path = input(f"Cho biết đường dẫn file thứ {i + 1}: ")
        
        while not os.path.exists(file_path):
            print(f"Lỗi: {file_path} không tồn tại. Vui lòng chọn lại.\n")
            file_path = input(f"Cho biết đường dẫn file thứ {i + 1}: ")
        while os.path.getsize(file_path) > max_size:
            print(f"Lỗi: Dung lượng của {file_path} vượt quá giới hạn. Hãy chọn file khác.\n")
            file_path = input(f"Cho biết đường dẫn file thứ {i + 1}: ")
        
        file_list.append(file_path)

    return file_list

def guess_mime_type(file_path):
    mime_types = {
        '.txt': 'text/plain',
        '.pdf': 'application/pdf',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.zip': 'application/zip',
        # Thêm các định dạng file khác nếu cần thiết
    }
    # Lấy phần mở rộng của file từ đường dẫn
    _, file_extension = os.path.splitext(file_path)
    # Sử dụng kiểu MIME mặc định hoặc kiểu MIME đã định nghĩa
    return mime_types.get(file_extension.lower(), 'application/octet-stream')


def send_attachment_content(file_list, clientSocket, boundary):
    for file_path in file_list:
        with open(file_path, "rb") as file:
            # Đọc dữ liệu từ file
            file_data = file.read()
            # Mã hóa dữ liệu thành Base64
            attachment_content = base64.b64encode(file_data)
            
            mime_type = guess_mime_type(file_path)
            clientSocket.send(f'\r\n{boundary}\r\nContent-Type: {mime_type}\r\n'.encode('utf-8'))
            clientSocket.send(f'Content-Transfer-Encoding: base64\r\n'.encode('utf-8'))
            clientSocket.send(f'Content-Disposition: attachment; filename= "{os.path.basename(file_path)}"\r\n\r\n'.encode('utf-8'))
            
            # Split the base64-encoded content into lines
            lines = [attachment_content[i:i+998] 
                    for i in range(0, len(attachment_content), 998)]

            # Send each line as UTF-8 encoded bytes
            for line in lines:
                clientSocket.sendall((line.decode('utf-8') + '\r\n').encode('utf-8'))
            
        clientSocket.send(f'\r\n{boundary}\r\n'.encode('utf-8'))

def generate_email_content(to, from_, subject, message, cc_recipients, boundary):
    email_content = ''
    email_content += f'Content-Type: multipart/mixed; boundary="{boundary}"\r\n'
    email_content += f"Message-ID: {generate_message_id()}\r\n"
    email_content += f'MIME-Version: 1.0\r\n'
    email_content += f'Date: {time.strftime("%a, %d %b %Y %H:%M:%S +0700", time.localtime())}\r\n'
    email_content += f'User-Agent: VMS\r\n'
    email_content += f'To: {to}\r\n'
    
    if cc_recipients:
        email_content += f'CC: {", ".join(cc_recipients)}\r\n'
    
    email_content += f'From: {from_}\r\n'
    email_content += f'Subject: {subject}\r\n'
    email_content += f'\r\n{boundary}\r\nContent-Type: text/plain\r\n'
    email_content += f'Content-Transfer-Encoding: 7bit\r\n\r\n{message}\r\n'
    
    return email_content

def get_recipients(temp):
    cc_recipients = input(f"{temp} (comma-separated): ")
    if cc_recipients == '':
        return None
    cc_list = [cc.strip() for cc in cc_recipients.split(',')]
    return cc_list

def send_email(HOST, SMTP_port, username, password):
    try:
        to_list  = get_recipients("TO")
        cc_list  = get_recipients("CC")
        bcc_list = get_recipients("BCC")
        sub = input("SUBJECT: ")
        msg = input("\r\n ")
        endmsg = "\r\n.\r\n"
        
        print("\n\nbạn có muốn đính kèm tệp\n")
        print("1. có        2. không\n")

        t = input()
        attachment_file_list = []
        if t == '1':
            attachment_file_list = attach_files(3145728)

        # Tạo nội dung email
        boundary = '------' + str(time.time()) + '------'
        email_content = generate_email_content(to_list, username, sub, msg, cc_list, boundary)
                
        mailserver = (HOST, SMTP_port)
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect(mailserver)
        
        recv = clientSocket.recv(1024)

        heloCommand = f'EHLO [ {HOST} ]\r\n'
        clientSocket.send(heloCommand.encode())
        recv1 = clientSocket.recv(1024)

        mailFrom = f'MAIL FROM: <{username}>\r\n'
        clientSocket.send(mailFrom.encode())
        recv2 = clientSocket.recv(1024)

        for to in to_list:
            rcptTo = f'RCPT TO: <{to.strip()}>\r\n'
            clientSocket.send(rcptTo.encode())
            recv3 = clientSocket.recv(1024)

        if cc_list:
            for cc in cc_list:
                cc_rcptTo = f'RCPT TO: <{cc.strip()}>\r\n'
                clientSocket.send(cc_rcptTo.encode())
                recv_cc = clientSocket.recv(1024)
        
        if bcc_list:
            for bcc in bcc_list:
                bcc_rcptTo = f'RCPT TO: <{bcc.strip()}>\r\n'
                clientSocket.send(bcc_rcptTo.encode())
                recv_bcc = clientSocket.recv(1024)
        
        data = "DATA\r\n"
        clientSocket.send(data.encode())
        recv4 = clientSocket.recv(1024)

        clientSocket.sendall(email_content.encode('utf-8'))
        
        if attachment_file_list:
            send_attachment_content(attachment_file_list, clientSocket, boundary)
        
        clientSocket.sendall(endmsg.encode())
        recv_msg = clientSocket.recv(1024)

        print("\n\nGửi email thành công \n\n")
        quit = "QUIT\r\n"
        
        clientSocket.send(quit.encode())
        recv5 = clientSocket.recv(1024)
        clientSocket.close()
        
    except Exception as e:
        print(f"ERROR: {e}")
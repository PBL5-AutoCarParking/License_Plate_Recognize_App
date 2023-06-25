import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
from flask import Flask, request
import threading
import requests
import numpy as np
import io
from src.lp_recognition import E2E



cap = cv2.VideoCapture(1)  # Kết nối camera thứ 2 intergrated với máy tính ( vì kinh phí có hạn :))

model_left = E2E()
model_right = E2E()
IP = '192.168.129.163'  # Replace with the IP address of your ESP32-CAM
URL = f'http://{IP}/capture'
DELAY = 500  # Milliseconds to wait between updating the image
WIDTH, HEIGHT = 400, 300  # Width and height of the image
CAPTURE_WIDTH, CAPTURE_HEIGHT = 320, 240  # Width and height of the capture image

app = Flask(__name__)
window = tk.Tk()


class App:
    def __init__(self, window):
        self.window = window
        self.window.title('Car Parking Camera Stream')
        # Set full screen:
        # self.window.attributes('-fullscreen', True)  # Set full man hinh, luu y khong co chuc nang thu nho hay full man hinh
        # Set optional screen:
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        window_width = int(screen_width * 0.9)  # 90% chiều rộng màn hình
        window_height = int(screen_height * 0.9)  # 90% chiều cao màn hình

        x = (screen_width - window_width) // 2  # Căn giữa theo chiều ngang
        y = (screen_height - window_height) // 2  # Căn giữa theo chiều dọc

        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Khung gốc
        self.frame = ttk.Frame(self.window)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Phần trên bên trái (Camera từ URL)
        self.frame_top_left = ttk.Frame(self.frame)
        self.frame_top_left.grid(row=0, column=0, padx=10, pady=10)

        # Label cổng vào
        self.lbl_input = tk.Label(self.frame_top_left, text='Cổng vào')
        self.lbl_input.pack(side=tk.TOP, padx=10, pady=10)

        self.canvas_top_left = tk.Canvas(self.frame_top_left, width=WIDTH, height=HEIGHT)
        self.canvas_top_left.pack()

        self.container_top_left = tk.Frame(self.frame_top_left)  # Frame cha
        self.container_top_left.pack()

        self.capture_frame_top_left = tk.Frame(self.container_top_left, width=CAPTURE_WIDTH, height=CAPTURE_HEIGHT)
        self.capture_frame_top_left.pack(padx=10, pady=10)

        self.btn_frame_top_left = ttk.Frame(self.container_top_left)
        self.btn_frame_top_left.pack(side=tk.LEFT, padx=10, pady=10)

        self.capture_image_top_left = tk.Label(self.capture_frame_top_left)
        self.capture_image_top_left.pack()

        self.btn_start_top_left = tk.Button(self.btn_frame_top_left, text='Start', command=self.start_top_left)
        self.btn_start_top_left.pack(side=tk.LEFT, padx=10, pady=10)

        self.btn_stop_top_left = tk.Button(self.btn_frame_top_left, text='Stop', command=self.stop_top_left)
        self.btn_stop_top_left.pack(side=tk.LEFT, padx=10, pady=10)

        self.lbl_result_lp_top_left = tk.Label(self.btn_frame_top_left, text='License Plate: Not found')
        self.lbl_result_lp_top_left.pack(padx=10, pady=10)

        self.lbl_result_uuid_top_left = tk.Label(self.btn_frame_top_left, text='UUID: Not found')
        self.lbl_result_uuid_top_left.pack(padx=10, pady=10)

        self.lbl_message_left = tk.Label(self.btn_frame_top_left, text='Message:')
        self.lbl_message_left.pack(side=tk.LEFT)

        # Phần trên bên phải (Camera từ Webcam)
        self.frame_top_right = ttk.Frame(self.frame)
        self.frame_top_right.grid(row=0, column=1, padx=10, pady=10)

        # Label cổng ra
        self.lbl_output_port = tk.Label(self.frame_top_right, text='Cổng ra')
        self.lbl_output_port.pack(side=tk.TOP, padx=10, pady=10)

        self.canvas_top_right = tk.Canvas(self.frame_top_right, width=WIDTH, height=HEIGHT)
        self.canvas_top_right.pack()

        self.container_top_right = tk.Frame(self.frame_top_right)  # Frame cha
        self.container_top_right.pack()

        self.capture_frame_top_right = tk.Frame(self.container_top_right, width=CAPTURE_WIDTH, height=CAPTURE_HEIGHT)
        self.capture_frame_top_right.pack(padx=10, pady=10)

        self.btn_frame_top_right = ttk.Frame(self.container_top_right)
        self.btn_frame_top_right.pack(side=tk.LEFT, padx=10, pady=10)

        self.capture_image_top_right = tk.Label(self.capture_frame_top_right)
        self.capture_image_top_right.pack()

        self.btn_start_top_right = tk.Button(self.btn_frame_top_right, text='Start', command=self.start_top_right)
        self.btn_start_top_right.pack(side=tk.LEFT, padx=10, pady=10)

        self.btn_stop_top_right = tk.Button(self.btn_frame_top_right, text='Stop', command=self.stop_top_right)
        self.btn_stop_top_right.pack(side=tk.LEFT, padx=10, pady=10)

        self.lbl_result_lp_top_right = tk.Label(self.btn_frame_top_right, text='License Plate: Not found')
        self.lbl_result_lp_top_right.pack(padx=10, pady=10)

        self.lbl_result_uuid_top_right = tk.Label(self.btn_frame_top_right, text='UUID: Not found')
        self.lbl_result_uuid_top_right.pack(padx=10, pady=10)

        self.lbl_message_right = tk.Label(self.btn_frame_top_right, text='Message:')
        self.lbl_message_right.pack(side=tk.LEFT)

        # Các biến và cờ cho phần trên bên trái
        self.running_top_left = False
        self.after_id_top_left = None
        self.can_capture_top_left = True
        self.previous_capture_image_top_left = None

        # Các biến và cờ cho phần trên bên phải
        # self.video_capture = cv2.VideoCapture(0)
        self.running_top_right = False
        self.after_id_top_right = None
        self.can_capture_top_right = True
        self.previous_capture_image_top_right = None

        # Các phương thức bắt sự kiện cho phần trên bên trái

    def start_top_left(self):
        self.running_top_left = True
        self.update_image_top_left()

    def stop_top_left(self):
        self.running_top_left = False
        if self.after_id_top_left is not None:
            self.window.after_cancel(self.after_id_top_left)
            self.after_id_top_left = None

    # Các phương thức bắt sự kiện cho phần trên bên phải
    def start_top_right(self):
        self.running_top_right = True
        self.update_image_top_right()

    def stop_top_right(self):
        self.running_top_right = False
        if self.after_id_top_right is not None:
            self.window.after_cancel(self.after_id_top_right)
            self.after_id_top_right = None

    # Các phương thức cập nhật hình ảnh cho phần trên bên trái
    def update_image_top_left(self):
        if not self.running_top_left:
            return
        try:
            response = requests.get(URL)
            if response.status_code == 200:
                # Đoạn code 
                img_bytes = io.BytesIO(response.content)
                img = Image.open(img_bytes)
                img = img.resize((WIDTH, HEIGHT))
                img_np = np.array(img)
                img = Image.fromarray(cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB))
                self.img_top_left = ImageTk.PhotoImage(img)
                self.canvas_top_left.create_image(0, 0, image=self.img_top_left, anchor=tk.NW)

                cropped_img, img = model_left.predict(img_np)
                license_plate_left = model_left.format()  # text

                if license_plate_left != "":
                    if license_plate_left != self.lbl_result_lp_top_left.cget('text')[15:]:
                        self.lbl_result_lp_top_left.config(text='License Plate: ' + license_plate_left)  # In ra label
                        self.lbl_result_uuid_top_left.config(text='UUID: Not Found')
                        self.lbl_message_left.config(text=f'Message:')
                        capture_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
                        capture_img = cv2.resize(capture_img, (CAPTURE_WIDTH, CAPTURE_HEIGHT))
                        pil_capture_img = Image.fromarray(capture_img)
                        pil_capture_img = ImageTk.PhotoImage(pil_capture_img)
                        self.capture_image_top_left.config(image=pil_capture_img)
                        self.capture_image_top_left.image = pil_capture_img
                        self.capture()  # Gọi phương thức chụp ảnh khi có sự nhận diện biển số
                else:
                    self.lbl_result_lp_top_left.config(text='License Plate: Not found')
                    if self.previous_capture_image_top_left is not None:
                        # Sử dụng hình ảnh chụp trước đó nếu không có biển số được nhận dạng
                        pil_capture_img = Image.fromarray(self.previous_capture_image_top_left)
                        pil_capture_img = ImageTk.PhotoImage(pil_capture_img)
                        self.capture_image_top_left.config(image=pil_capture_img)
                        self.capture_image_top_left.image = pil_capture_img
                        # self.lbl_message_left.config(text=f'Cổng vào nhận diện được biển số')
            else:
                print("Khong ket noi voi cam duoc")

        except Exception as e:
            print("An error occurred:", e)
            # self.lbl_message_left.config(text=f'Error when recognize license plate')
            # self.stop_top_left()

        finally:
            self.after_id_top_left = self.window.after(DELAY, self.update_image_top_left)

    # Các phương thức cập nhật hình ảnh cho phần trên bên phải
    def update_image_top_right(self):
        if not self.running_top_right:
            return
        try:
            ret, frame = cap.read()
            # ret, frame=self.video_capture.read()
            if ret:
                frame = cv2.resize(frame, (WIDTH, HEIGHT))
                img_np = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # chỉnh lại màu sắc
                img = Image.fromarray(img_np)
                self.img_top_right = ImageTk.PhotoImage(img)
                self.canvas_top_right.create_image(0, 0, image=self.img_top_right, anchor=tk.NW)

                # Xử lý nhận dạng biển số
                cropped_img, img = model_right.predict(frame)
                license_plate_right = model_right.format()
                if license_plate_right != "":
                    if license_plate_right != self.lbl_result_lp_top_right.cget('text')[15:]:
                        self.lbl_result_lp_top_right.config(text='License Plate: ' + license_plate_right)
                        self.lbl_result_uuid_top_right.config(text='UUID: Not Found')
                        self.lbl_message_right.config(text=f'Message:')
                        capture_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
                        capture_img = cv2.resize(capture_img, (CAPTURE_WIDTH, CAPTURE_HEIGHT))
                        pil_capture_img = Image.fromarray(capture_img)
                        pil_capture_img = ImageTk.PhotoImage(pil_capture_img)
                        self.capture_image_top_right.config(image=pil_capture_img)
                        self.capture_image_top_right.image = pil_capture_img
                        self.capture()  # Gọi phương thức chụp ảnh khi có sự nhận diện biển số
                else:
                    # self.lbl_result_lp_top_right.config(text='License Plate: Not found')
                    if self.previous_capture_image_top_right is not None:
                        # Sử dụng hình ảnh chụp trước đó nếu không có biển số được nhận dạng
                        pil_capture_img = Image.fromarray(self.previous_capture_image_top_right)
                        pil_capture_img = ImageTk.PhotoImage(pil_capture_img)
                        self.capture_image_top_right.config(image=pil_capture_img)
                        self.capture_image_top_right.image = pil_capture_img
                        # self.lbl_message_right.config(text=f'Nhận diện được biển số')

        except Exception as e:
            # self.lbl_message_right.config(text=f'Error: {str(e)}')
            print("An error occurred:", e)
            # self.lbl_message_right.config(text=f'Lỗi trong quá trình nhận diện biển số.')
            # self.stop_top_right()
        finally:
            self.after_id_top_right = self.window.after(DELAY, self.update_image_top_right)

    # Các phương thức chụp ảnh
    def capture(self):
        if self.can_capture_top_left:
            self.previous_capture_image_top_left = self.capture_image_top_left.image
        if self.can_capture_top_right:
            self.previous_capture_image_top_right = self.capture_image_top_right.image



@app.route('/process_post', methods=['POST'])
def receive_uuid():
    uuid = request.form.get('uuid')
    uuid = uuid.replace(' ', '')  # Loại bỏ dấu cách trong uuid
    entry_signal = request.form.get('entry_signal')
    print(' entry_signal', entry_signal)
    if entry_signal == "1" or entry_signal == 1:
        entry_signal = True
        license_plate = app_window.lbl_result_lp_top_left.cget('text')[15:]  # Lấy giá trị từ label của biển số
        app_window.lbl_result_uuid_top_left.config(text='UUID: ' + uuid)
        response_code, response_text = sendDataToServer(license_plate, uuid, entry_signal)
        if response_code == 200:
            app_window.lbl_message_left.config(text='Message: Đã gửi lên server thành công, 200')
        else:
            app_window.lbl_message_left.config(text=f'Message: Error {response_code} - {response_text}')
    else:
        entry_signal = False
        license_plate = app_window.lbl_result_lp_top_right.cget('text')[15:]  # Lấy giá trị từ label của biển số
        app_window.lbl_result_uuid_top_right.config(text='UUID: ' + uuid)
        response_code, response_text = sendDataToServer(license_plate, uuid, entry_signal)
        if response_code == 200:
            app_window.lbl_message_right.config(text='Message: Đã gửi lên server thành công, 200')
        else:
            app_window.lbl_message_right.config(text=f'Message: Error {response_code} - {response_text}')
    return str(response_code)


def sendDataToServer(lp, uuid, entry_signal):
    # license_plate = lp_label.cget('text')[15:]
    # uuid = uuid_label.cget('text')[6:]

    if lp and uuid:
        if entry_signal:
            url = 'http://127.0.0.1:8000/entry_car/'
        else:
            url = 'http://127.0.0.1:8000/exit_car/'
        payload = {'license_plate': lp, 'uuid': uuid}
        try:
            response = requests.post(url, data=payload)
            response_text = response.text
            if response.status_code == 200:
                print('Data sent successfully')
                # return response.status_code, response_text
            else:
                print(f'Failed to send data. Status code: {response.status_code}')

            return response.status_code, response_text
        except requests.exceptions.RequestException as e:
            print(f'An error occurred while sending data: {e}')
            return -1, 'Lỗi khi gửi thông tin'
    else:
        print('Không đủ thông tin giữ xe')
        return -1, 'Lỗi khi gửi thông tin'


@app.route('/')
def index():
    return 'Hello, World!'


if __name__ == '__main__':
    app_window = App(window)
    threading.Thread(target=app.run, kwargs={'host': '192.168.129.68', 'port': 8000}).start()
    window.mainloop()

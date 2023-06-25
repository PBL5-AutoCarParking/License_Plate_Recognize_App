import cv2 # Thư viên Opencv hỗ trợ xử lý hình ảnh
from pathlib import Path # Path và argparse lần lượt là thuư viện hỗ trợ xử lý đường dẫn và tham số dòng lệnh
import argparse
import time # Thư viện hỗ trợ tính thời gian thực thi

from src.lp_recognition import E2E # lớp nhận dạng biển số xe trong file lp.recognition

def get_arguments():
    arg = argparse.ArgumentParser() # Khởi tạo đối tượng Ardument Parser
    arg.add_argument('-i', '--image_path', help='link to image', default='./samples/1.jpg') # các tham số cho đối tượng
    #arg = argparse.ArgumentParser('-i', '--image_path', help='link to image', default='./samples/1.jpg') #thay hàm add_argument bằng cách này sẽ gặp bug. Không trùng tham số với hàm
    return arg.parse_args() # hàm parse_args()


args = get_arguments() # trả về đối tượng ảnh
img_path = Path(args.image_path) # lấy đường dẫn ảnh từ tham số args. imagepath

# read image
img = cv2.imread(str(img_path))  # đọc ảnh từ đường dẫn

# start
start = time.time() # lấy thời điểm bắt đầu

# load model
model = E2E() #

model.test()
# recognize license plate
cropped_image,image = model.predict(img)  # check hàm predict

# end
end = time.time()# lấy thời điểm kết thúc

print('Model process on %.2f s' % (end - start))

# show image
# Tạo cửa sổ hiển thị với kích thước cố định
cv2.namedWindow('License Plate', cv2.WINDOW_NORMAL)
cv2.resizeWindow('License Plate', 800, 600)
cv2.imshow('License Plate', image) # Bao gồm tên cửa sổ và ảnh
import matplotlib.pyplot as plt

# Hiển thị hình ảnh cắt toàn màn hình
plt.imshow(cropped_image)
plt.show()

if cv2.waitKey(0) & 0xFF == ord('q'):
    exit(0)


cv2.destroyAllWindows()
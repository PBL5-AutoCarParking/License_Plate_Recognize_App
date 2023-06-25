import cv2
import numpy as np
import os


# Tính toán Intersection over Union (IoU) giữa 2 bounding box
def iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou


# Tính toán Average Precision (AP) dựa trên Precision và Recall
def compute_ap(precision, recall):
    mrec = np.concatenate(([0.], recall, [1.]))
    mpre = np.concatenate(([0.], precision, [0.]))
    for i in range(len(mpre) - 2, -1, -1):
        mpre[i] = max(mpre[i], mpre[i + 1])
    i = np.where(mrec[1:] != mrec[:-1])[0] + 1
    ap = np.sum((mrec[i] - mrec[i - 1]) * mpre[i])
    return ap


# Load tập test và file labels chứa thông tin bounding box thực tế
test_path = 'path/to/test/images'
label_path = 'path/to/test/labels'

with open(label_path, 'r') as f:
    labels = f.readlines()

# Tính toán IoU và AP trên tập test
num_images = len(os.listdir(test_path))
ious = []
for i in range(num_images):
    # Load ảnh và bounding box thực tế
    img_path = os.path.join(test_path, f'{i}.jpg')
    img = cv2.imread(img_path)
    height, width, _ = img.shape
    boxes = []
    for line in labels:
        if line.startswith(f'{i}.jpg'):
            _, x, y, w, h = map(float, line.strip().split()[1:])
            xmin = int((x - w / 2) * width)
            ymin = int((y - h / 2) * height)
            xmax = int((x + w / 2) * width)
            ymax = int((y + h / 2) * height)
            boxes.append([xmin, ymin, xmax, ymax])
    boxes = np.array(boxes)

    # Dự đoán bounding box bằng YoloV3 model và tính toán IoU giữa các bounding box dự đoán và bounding box thực tế

pred_boxes = []  # danh sách chứa các bounding box dự đoán

for pred_box in pred_boxes:
    ious.append([iou(pred_box, true_box) for true_box in boxes])
ious = np.array(ious)

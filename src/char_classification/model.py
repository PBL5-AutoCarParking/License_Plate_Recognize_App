import numpy as np  # Thư viện hỗ trợ tính toán số học
from tensorflow.keras import optimizers # tensor-flow: mã nguồn mở dành cho thư viện học máy
# module optimizers import từ keras chưas các thuật toán tối ưu hóa trong mô hình học máy huấn luyện
from tensorflow.keras.layers import Dense, Conv2D, MaxPooling2D, Dropout, Flatten # Các loại lớp của mạng nơ rôn được import từ thư viện tensor flow layers
from tensorflow.keras.callbacks import ReduceLROnPlateau, ModelCheckpoint # là các hàm Callback, hàm (1) để giảm tốc độ học và hàm 2 là lưu mô hình tốt nhất
from tensorflow.keras.models import Sequential # Sequential là một model class đại diện cho các chuỗi lớp của mạng nơ rôn

import numpy as np
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import to_categorical


from src.char_classification import config
from src.char_classification.data_provider import Datasets # từ module nhận diện ký tự

# định nghĩa 1 thư viện map class chỉ số với các nhãn
ALPHA_DICT = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'K', 9: 'L', 10: 'M', 11: 'N', 12: 'P',
              13: 'R', 14: 'S', 15: 'T', 16: 'U', 17: 'V', 18: 'X', 19: 'Y', 20: 'Z', 21: '0', 22: '1', 23: '2', 24: '3',
              25: '4', 26: '5', 27: '6', 28: '7', 29: '8', 30: '9', 31: "Background"}


class CNN_Model(object):
    # Khởi tạo hàm dựng
    def __init__(self, trainable=True):
        self.batch_size = config.BATCH_SIZE # Số lượng mẫu dữ liệu đẻ huấn luyện mô hình trong mỗi lần cập nhật trọng số của nó, Nếu batch size càng lớn thì tốc độ huấn luyện nhanh, tuy nhiên bộ nhớ lớn
        self.trainable = trainable # Xác định liệu mô hình có được phép cập nhật trọng số trong quá trình huấn luyện
        self.num_epochs = config.EPOCHS # số lượng epoch trong huấn luyện

        # Building model
        self._build_model()

        # Input data
        if trainable:
            self.model.summary()
            self.data = Datasets()

        self.model.compile(loss="categorical_crossentropy", optimizer=optimizers.Adam(1e-3), metrics=['acc']) # Hàm compile

    def _build_model(self):
        # CNN model
        self.model = Sequential()
        self.model.add(Conv2D(32, (3, 3), padding='same', activation='relu', input_shape=(28, 28, 1)))
        self.model.add(Conv2D(32, (3, 3), activation='relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Dropout(0.25))

        self.model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
        self.model.add(Conv2D(64, (3, 3), activation='relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Dropout(0.25))

        self.model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
        self.model.add(Conv2D(64, (3, 3), activation='relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Dropout(0.25))

        self.model.add(Flatten())
        self.model.add(Dense(512, activation='relu'))
        self.model.add(Dropout(0.5))
        #self.model.add(Dense(32, activation='softmax'))
        self.model.add(Dense(32, activation='softmax'))

    def train(self):
        # reduce learning rate
        reduce_lr = ReduceLROnPlateau(monitor='val_acc', factor=0.2, patience=5, verbose=1, )
        # Model Checkpoint
        cpt_save = ModelCheckpoint('./weight.h5', save_best_only=True, monitor='val_acc', mode='max')

        print("Training......")
        trainX, trainY = self.data.gen()
        trainX = np.array(trainX)

        self.model.fit(trainX, trainY, validation_split=0.15, callbacks=[cpt_save, reduce_lr], verbose=1,
                       epochs=self.num_epochs, shuffle=True, batch_size=self.batch_size)

    def test(self):
        # Load MNIST dataset
        (x_train, y_train), (x_test, y_test) = mnist.load_data()

        # # Normalize and reshape the data
        # x_test = x_test.reshape(-1, 28, 28, 1) / 255.0
        # y_test = np.eye(10)[y_test]  # One-hot encode the labels
        x_test = np.expand_dims(x_test, axis=-1)
        x_test = np.repeat(x_test, 3, axis=-1)
        x_test = x_test / 255.0

        y_test = to_categorical(y_test)
        # Load the trained model
        self.model.load_weights('../weights/weight.h5')

        # Evaluate the model on the test set
        loss, accuracy = self.model.evaluate(x_test, y_test, verbose=0)

        # Print the accuracy
        print(f"Accuracy: {accuracy * 100:.2f}%")


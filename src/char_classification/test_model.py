from src.char_classification.model import CNN_Model
# Tạo một đối tượng CNN_Model
from src.lp_recognition import E2E  #

test_model=CNN_Model(trainable=False)
# test_model.load_weights('./weights/weight.h5')
# Gọi phương thức test()
test_model.test()

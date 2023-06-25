import cv2
import serial
import time
import easyocr

# Initialize serial communication with Arduino
ser = serial.Serial('COM5', 115200)

# Initialize the camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Initialize the OCR reader
reader = easyocr.Reader(['en'])

while True:
    # Capture a frame from the camera
    ret, frame = cap.read()

    # Apply license plate recognition to the frame
    results = reader.readtext(frame, detail=0)
    for result in results:
        if len(result) == 7 and result.isalnum():
            print('License plate detected:', result)

            # Send a signal to the Arduino to control the servo motor
            ser.write(b'90')

    # Display the frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) == ord('q'):
        ser.write(b'90')
        break

# Release the resources
cap.release()
cv2.destroyAllWindows()
ser.close()

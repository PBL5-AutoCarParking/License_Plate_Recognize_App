import cv2

# Connect to the camera
cap = cv2.VideoCapture(0)  # 0 is the index of the camera, change it if necessary

# Check if the camera is connected
if not cap.isOpened():
    print("Cannot connect to the camera")
    exit()

# Read frames from the camera
while True:
    ret, frame = cap.read()

    # Display the frame
    cv2.imshow('frame', frame)

    # Exit the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()

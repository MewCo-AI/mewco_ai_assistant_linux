import cv2


def list_available_cameras():
    index = 0
    available_cameras = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        else:
            available_cameras.append(index)
        cap.release()
        index += 1
    return available_cameras


cameras = list_available_cameras()
if cameras:
    print(f"可用的摄像头索引: {cameras}")
else:
    print("没有找到可用的摄像头。")

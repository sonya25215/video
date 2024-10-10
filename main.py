import cv2

#инициируем детектор людей
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

def process_video(input_video_path, output_video_path, min_object_size, progress_callback):
  cap=cv2.VideoCapture(input_video_path)

  if not cap.isOpened():
    raise Exception("Ошибка при открытии видео")

  frame_width = int(cap.get(3))
  frame_height = int(cap.get(4))
  fps = cap.get(cv2.CAP_PROP_FPS)
  total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

  #VIDEOWRITTER для записи фрагментов
  out_temp = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

  frame_count = 0

  while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
      break

    #детект людей в кадре
    boxes, _ = hog.detectMultiScale(frame, winStride=(8, 8))
    boxes = [box for box in boxes if box[2] * box[3] > min_object_size]
    #при обнаружении сохраняем кадр
    if boxes:
      out_temp.write(frame)
    #обновление прогресса
    progress_callback(frame_count / total_frames * 100)

    frame_count += 1
  
  cap.release()
  out_temp.release()

  processing_done()

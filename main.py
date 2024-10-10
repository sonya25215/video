import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
import threading
import os

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

#фукнция об обновалении прогресса
def update_progress(value):
  progress_bar['value'] = value
  root.update_idletasks()

#запуск процесса обработки в отдельном потоке
def start_processing():
  input_video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4")])
  if not input_video_path:
      messagebox.showerror("Ошибка", "Пожалуйста, выберите видеофайл.")
      return

  output_video_path = os.path.join(os.path.dirname(input_video_path), "output_video.mp4")
  min_object_size = int(min_object_size_entry.get())

  progress_bar['value'] = 0

  process_button.config(state=tk.DISABLED)
  close_button.config(state=tk.DISABLED)

    #обработка видео в отдельном потоке
  threading.Thread(target=process_video,
                   args=(input_video_path, output_video_path, min_object_size, update_progress)).start()


#графический интерфейс
root = tk.Tk()
root.title("Видеообработка с постоянным присутствием человека")

frame = tk.Frame(root)
frame.pack(pady=20)

min_object_size_label = tk.Label(frame, text="Минимальный размер объекта:")
min_object_size_label.grid(row=0, column=0, padx=10)

min_object_size_entry = tk.Entry(frame)
min_object_size_entry.grid(row=0, column=1, padx=10)
min_object_size_entry.insert(0, "1000")

process_button = tk.Button(frame, text="Начать обработку", command=start_processing)
process_button.grid(row=1, column=0, columnspan=2, pady=10)

progress_bar = Progressbar(frame, length=200)
progress_bar.grid(row=2, column=0, columnspan=2, pady=10)

close_button = tk.Button(frame, text="Закрыть", command=root.quit, state=tk.DISABLED)
close_button.grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()

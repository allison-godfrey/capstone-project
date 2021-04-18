import os
import shutil
import re
import editdistance
import cv2
import pytesseract
from pytesseract import Output
import pandas as pd

from .htr.src.DataLoaderIAM import DataLoaderIAM, Batch
from .htr.src.SamplePreprocessor import preprocess
from .htr.src.Model import Model, DecoderType

from capstone.settings import BASE_DIR

# configure tesseract
## oem 3 == Engine Mode: Default, based on what is available (Legacy, LSTM, or both)
## psm 3 == Page Segmentation Mode: Fully automatic page segmentation, but no OSD
## psm 11 == Page Segmentation Mode: Sparse text - find as much text as possible in no particular order, no OSD
custom_config = r'--oem 3 --psm 11'

def infer(model, fnImg):
  "recognize text in image provided by file path"
  img = preprocess(cv2.imread(fnImg, cv2.IMREAD_GRAYSCALE), Model.imgSize)
  batch = Batch(None, [img])
  (recognized, probability) = model.inferBatch(batch, True)
  return (recognized[0],probability[0])

def split_image(img_path, out_path):
  img = cv2.imread(img_path)
  imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  imgBinary = cv2.threshold(imgGray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

  details = pytesseract.image_to_data(imgBinary, output_type=Output.DICT, config=custom_config, lang='eng')
  total_boxes = len(details['text'])
  for sequence_number in range(total_boxes):
    if int(details['conf'][sequence_number]) > -1:
      (x, y, w, h) = (details['left'][sequence_number], details['top'][sequence_number], details['width'][sequence_number],  details['height'][sequence_number])
      imgBinary = cv2.rectangle(imgBinary, (x, y), (x + w, y + h), (0, 255, 0), 2)
      crop_img = img[y:y+h, x:x+w]
      cv2.imwrite(os.path.join(out_path,str(sequence_number).zfill(len(str(total_boxes)))+'.png'), crop_img)

def extract_words_from_image(img_name, img_path):
  tmp_dir = BASE_DIR / 'tmp'
  if not os.path.exists(tmp_dir):
    os.mkdir(tmp_dir)
  out_path = tmp_dir / img_name
  os.mkdir(out_path)

  try:
    split_image(img_path, out_path)

    # df = pd.DataFrame(columns=['Actual','Guess','Conf','Result','Dist','Path'])
    out = []
    model = Model(open('autoreader/htr/model/charList.txt').read(), DecoderType.BestPath, mustRestore=True, dump=False)
    for sample in os.listdir(out_path):
      guess, conf = infer(model, os.path.join(out_path,sample))
      actual = re.sub('((\W+\(\d*\))?\.((png)|(jpg)))','',sample)
      result = actual==guess
      if len(actual)>0:
        dist = editdistance.eval(guess, actual)/len(actual)
      else:
        dist=len(guess)
      # df = df.append(pd.Series([actual, guess, conf, result, dist, os.path.join(out_path,sample)], index = df.columns), ignore_index=True)
      out.append((sample.split('.')[0], guess))
  finally:
    # delete the tmp directory
    shutil.rmtree(out_path)

  # sort by order of image name
  # then return just the guess
  return ' '.join(map(lambda x: x[1], sorted(out, key=lambda x: x[0])))

# -*- coding: utf-8 -*-
"""telegram bot.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14M_VCuCCi69MmU3cMoNXxQBCd09Nodsl

##Импорт библиотек
"""

! pip install pytelegrambotapi

import torch
from PIL import Image
from torchvision import transforms
import numpy as np
import pandas as pd

import telebot
import requests
import shutil

"""##Иницилизация обвязки модели"""

resnet_transforms = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

! wget "https://getfile.dokpub.com/yandex/get/https://yadi.sk/d/DwxCSAMhhNtp9Q" -O mushroom_database.csv

! wget "https://getfile.dokpub.com/yandex/get/https://yadi.sk/d/L1vdaKCEG2ZU-w" -O mushroom_model.pt

model_new = torch.load('mushroom_model.pt')

mtd = pd.read_csv('mushroom_database.csv')

"""##Запуск бота"""

API_TOKEN = '2027085491:AAGM3mxz4HHOn23AyCowB_A5uj2tMYU6i-0'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(content_types=["photo"])
def echo_message(message):
    file_info = bot.get_file(message.photo[-1].file_id) #const
    # bot.reply_to(message, f'Got your image: {file_info}')

    url = 'https://api.telegram.org/file/bot{0}/{1}'.format(API_TOKEN, file_info.file_path)
    response = requests.get(url, stream=True)
    
    path = 'image.jpg'
    if response.status_code == 200:
        with open(path, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)
    
    img_test = Image.open(path)
    img_tensor = resnet_transforms(img_test)
    img_tensor = img_tensor.view(1, 3, 224, 224)
    output = model_new(img_tensor)
    prediction_new = int(torch.max(output.data, 1)[1].numpy())

    mushroom = mtd['mushroom'].values[prediction_new] + "\n" + "\n"
    description = mtd['description'].values[prediction_new] + "\n" + "\n"
    usefulness = mtd['usefulness'].values[prediction_new] + "\n" + "\n"
    fact = mtd['fact'].values[prediction_new] + "\n" + "\n"
    recipe = mtd['recipe'].values[prediction_new].replace(r'\n', '\n')

    bot.reply_to(message, mushroom + description + usefulness + fact + recipe)

bot.infinity_polling()
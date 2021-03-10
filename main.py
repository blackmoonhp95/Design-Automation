from tkinter import messagebox
from PIL import Image
import time
import os
import pandas as pd
import re
import concurrent.futures
import shutil
import PySimpleGUI as sg

mocks = ['t-shirt', 'v-neck', 'unisex-long', 'CREW', 'hoodie', 'tank-top']
colors = ['black', 'white', 'navy', 'royal-blue', 'sport-grey']
bucket = 'cuongcicopa'
region = 'ap-southeast-1'
folder = input('Nhập tên thư mục để up ảnh:\n')
list_name = os.listdir(r'Resource\Result')


def get_image(designs):
    img_path = []
    for design in os.listdir(designs):
        design_path = designs + '\\' + design
        for img in os.listdir(os.path.normpath(design_path)):
            path = os.path.normpath(design_path) + '\\' + img
            img_path.append(path)
    return img_path


def modify_image(design, mockup):
    img = Image.open(design)
    bg = Image.open(mockup)
    width_img, height_img = img.size
    width_bg, height_bg = bg.size
    position = (width_bg // 2 - width_img // 2, (height_bg // 2 - height_img // 2)*2//3)
    bg.paste(img, position, mask=img)
    return bg


def get_name(path):
    path_temp = re.split(r'\\', path)
    return path_temp


def create_url(bucket, region, folder, name_img):
    url = ('{}.s3-{}.amazonaws.com/{}/{}%2Ejpg'.format(bucket, region, folder, name_img))
    return url



if __name__ == '__main__':

    print('\nĐang chạy tool!\n')

    print('Đang tạo ảnh .....\n')

    if os.path.exists('result.csv'):
        os.remove('result.csv')

    if os.path.exists('Resource/Result'):
        shutil.rmtree('Resource/Result')

    # Create save folder
    path_save = 'Resource/Result'
    if not os.path.exists('Resource/Result'):
        os.makedirs('Resource/Result')

    # Get directory of design and mockup images
    designs = 'Resource/Designs'
    mockups = 'Resource/Mockups'

    mockups_img = get_image(mockups)
    design_img = get_image(designs)

    design_numb = len(design_img)
    numb = 1

    for design in design_img:

        # Create folder for every design after modifying
        design_name = get_name(design)[-1].split('.')[0]
        # design_path = path_save + '\\' + design_name
        print('{}: {}/{}'.format(design_name, numb, len(design_img)))
        numb += 1

        # Initialize function to run threads
        def make_img(mockup):
            mockup_name = get_name(mockup)
            bg = modify_image(design, mockup)
            width, height = bg.size
            new_bg = bg.resize((width//2, height//2))
            new_bg.save(path_save + '\\' + design_name + ' ' + mockup_name[-2] + ' ' + mockup_name[-1])

        t1 = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(make_img, mockups_img)

        t2 = time.perf_counter()
        print(round(t2 - t1, 2), 'seconds')

    if len(os.listdir('Resource/Result')) == 0:
        messagebox.showwarning(title='Error', message='Images not found!')
        messagebox.showinfo(title='Suggestion', message='Copy all images again!')
        quit()

    print('\nĐang xử lý url .....')

    list_name = [x.split('.')[0] for x in list_name]
    list_name = [[x, x.replace(' ', '%20')] for x in list_name]
    list_name = [[x[0], x[1].replace(',', '%2C')] for x in list_name]

    list_name = [[x[0], create_url(bucket, region, folder, x[1])] for x in list_name]

    length = len(list_name)

    list_name.sort(key=lambda x: x[0])

    for i in range(0, length, 5):
        get_color = []
        get_color.append(list_name[i + 4][1])
        get_color.append(list_name[i + 1][1])
        get_color.append(list_name[i + 2][1])
        get_color.append(list_name[i + 3][1])
        list_name[i].extend(get_color)

    list_name = [list_name[x * 5] for x in range(0, len(list_name) // 5)]

    count = 1
    indexing = 1
    for i in range(len(list_name) + len(list_name) // 6):
        if count == 7:
            count = 1
            indexing += 1

        if i % 7 == 0:
            parent = list_name[i + 1].copy()
            parent[0] = parent[0] + ' P'
            list_name.insert(i, parent)
        else:
            list_name[i][0] = list_name[i][0] + ' B{}'.format(indexing)
            count += 1

    for i in range(len(list_name)):
        list_name[i][0] = list_name[i][0].replace('-', ' ')


    result = pd.DataFrame(list_name, columns=['Product name',
                                              'Link black',
                                              'Link white',
                                              'Link navy',
                                              'Link royal blue',
                                              'Link sport grey'])

    result.to_csv('result.csv', mode = 'w')
    
    print('\nXONGGGGGG!')
    quit()

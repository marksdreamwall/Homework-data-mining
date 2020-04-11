import shutil
import os
from os import path
import PyPDF2
from PyPDF2.utils import PdfReadError
from PIL import Image
import pytesseract
from pymongo import MongoClient
import time

image_folder_path = '/Users/andrewvolkov/Documents/Prog/GitHub/Homework-data-mining/Image'
folder_path = '/Users/andrewvolkov/Documents/Prog/GitHub/Homework-data-mining/data_for_parse'


def all_files(fol_path):
    """ Создает список всех файлов с их полным путем """

    f_tree = []
    for itm in os.walk(fol_path):
        f_tree.append(itm)
    f_path = []
    for i in f_tree:
        for j in i[2]:
            f_path.append(i[0] + '/' + j)
    return f_path


# def sort_files(paths_list, root_path):
#     """Производит перемещение всех файлов из папок в папки по расширениям"""
#     for itm in paths_list:
#         name, ext = os.path.splitext(itm)
#         name = name.split('/')[-1]
#         ext = ext[1:]
#         if os.path.exists(root_path + '/' + ext):
#             shutil.move(itm, root_path + '/' + ext + '/' + name + '.' + ext)
#         else:
#             os.makedirs(root_path + '/' + ext)
#             shutil.move(itm, root_path + '/' + ext + '/' + name + '.' + ext)
#     print(1)


def extract_pdf_image(pdf_path):
    try:
        pdf_file = PyPDF2.PdfFileReader(open(pdf_path, 'rb'), strict=False)
    except PdfReadError as e:
        print(e)
        return None
    except FileNotFoundError as e:
        print(e)
        return None

    result = []

    for page_num in range(0, pdf_file.getNumPages()):
        page = pdf_file.getPage(page_num)
        page_object = page['/Resources']['/XObject'].getObject()

        if page_object['/Im0'].get('/Subtype') == '/Image':
            size = (
            page_object['/Im0']['/Width'], page_object['/Im0']['/Height'])
            data = page_object['/Im0']._data
            mode = 'RGB' if page_object['/Im0'][
                                '/ColorSpace'] == '/DeviceRGB' else 'p'

            decoder = page_object['/Im0']['/Filter']
            if decoder == '/DCTDecode':
                file_type = 'jpg'
            elif decoder == '/FlateDecode':
                file_type = 'png'
            elif decoder == '/JPXDecode':
                file_type = 'jp2'
            else:
                file_type = 'bmp'

            result_strict = {
                'page': page_num,
                'size': size,
                'data': data,
                'mode': mode,
                'file_type': file_type,
            }

            result.append(result_strict)

    return result


def save_pdf_image(f_name, f_path, *pdf_strict):
    file_paths = []
    for itm in pdf_strict:
        name = f'{f_name}_#_{itm["page"]}.{itm["file_type"]}'
        file_path = path.join(f_path, name)

        with open(file_path, 'wb') as image:
            image.write(itm['data'])
        file_paths.append(file_path)
    return file_paths


def extract_number(file_path):
    numbers = []
    img_obj = Image.open(file_path)
    text = pytesseract.image_to_string(img_obj, 'rus')
    pattern = 'заводской (серийный) номер'
    pattern_2 = 'заводской номер (номера)'

    for idx, line in enumerate(text.split('\n')):
        if line.lower().find(pattern) + 1 or line.lower().find(pattern_2) + 1:
            text_en = pytesseract.image_to_string(img_obj, 'eng')
            number = text_en.split('\n')[idx].split(' ')[-1]
            numbers.append((number, file_path))
    return numbers


if __name__ == '__main__':
    client = MongoClient('mongodb://localhost:27017/')
    db = client['serial_numbers']
    collection = db['parse_pdf_jpg']
    collection_errors = db['errors']
    result = {}
    f_list = all_files(folder_path)
    # sort_files(f_list, folder_path)
    for i in f_list:
        if i.split('/')[-1].split('.')[-1] == 'pdf':
            try:
                a = extract_pdf_image(i)
                b = save_pdf_image(i.split('/')[-1], image_folder_path, *a)
                c = [extract_number(itm) for itm in b]
                for serial in c:
                    collection.insert_one({'serial': serial[0][0],
                                           'path_to_file': i})
            except Exception as e:
                collection_errors.insert_one({'error': 'cant_parse_file',
                                              'path_to_file': i})


        elif i.split('/')[-1].split('.')[-1] == 'jpg':
            c = extract_number(i)
            for serial in c:
                collection.insert_one({'serial': serial[0],
                                       'path_to_file': i})

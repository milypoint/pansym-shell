'''
Создание описания профиля с поворотом рулевый поверхностей

Входной файл следующего формата с произвольным количеством точек

{ 1.0000 0.9949 0.9796 0.9544 0.9200 0.8770 0.8264 0.7691 0.7065 0.6397
 0.5702 0.4994 0.4287 0.3597 0.2939 0.2322 0.1757 0.1256 0.0828 0.0482
 0.0225 0.0063 0.0000 0.0039 0.0180 0.0422 0.0759 0.1186 0.1694 0.2272
 0.2907 0.3585 0.4290 0.5006 0.5721 0.6420 0.7089 0.7715 0.8285 0.8787
 0.9213 0.9552 0.9799 0.9950 1.0000

 0.0000-0.0004-0.0016-0.0035-0.0060-0.0091-0.0127-0.0166-0.0208-0.0251
-0.0294-0.0334-0.0368-0.0395-0.0414-0.0423-0.0419-0.0397-0.0357-0.0296
-0.0217-0.0118 0.0000 0.0128 0.0256 0.0382 0.0500 0.0604 0.0689 0.0751
 0.0785 0.0791 0.0767 0.0723 0.0662 0.0587 0.0503 0.0414 0.0324 0.0237
 0.0159 0.0093 0.0042 0.0011 0.0000}
'''

#fi угол поворота в градусах

import os
from math import *

def rotDots(fi, infile = False):	

	data_dir = getProjectDir() + 'data\\' #файл с данными
	input_filename = "aerofoil_in.dat" #входной файл с координатами точек профиля

	with open(data_dir + input_filename, 'r') as f:
		read_data = f.read() #чтение файла в массив

	read_data = read_data.replace('-', ' -').replace('\n', '').split(' ') #преобразования массива входных данных в список по разделителю " "
	del read_data[0] #удаление первого пустого элемента списка
	points_count = int(len(read_data)/2) #количество точек профиля

	indx = 0
	while indx < points_count:
		x = float(read_data[indx]) #значение х текущей точки
		y = float(read_data[indx + points_count]) #значение у текущей точки
		if x > 0.7: #проверка того, что точка находится на участке рулевой поверхности
			x_new = 0.7 + (x - 0.7)*cos(-fi*pi/180) + y*sin(-fi*pi/180) #поворот х текущей точки относительно центра поворота (0.7; 0)
			y_new = (x - 0.7)*sin(-fi*pi/180) + y*cos(-fi*pi/180) #поворот у текущей точки относительно центра поворота (0.7; 0) 
			read_data[indx] = str(round(x_new, 4)) #запись новой точки в список
			read_data[indx + points_count] = str(round(y_new, 4)) #запись новой точки в список
			while len(read_data[indx].replace('-', '')) < 6:
				read_data[indx] = read_data[indx] + '0' #добавление баластного нуля для соблюдения одинаковой длины строк
			while len(read_data[indx + points_count].replace('-', '')) < 6:
				read_data[indx + points_count] = read_data[indx + points_count] + '0'
		indx += 1

	indx = 0
	cur_lineitems_count = 0
	new_data = ' ' #новый список полученых точек
	for item in read_data:
		new_data = new_data + item + ' ' #после каждого значения ставим пробел
		cur_lineitems_count += 1
		if cur_lineitems_count  == 10:
			new_data = new_data + '\n ' #каждые 10 значений переносим на новую строку
			cur_lineitems_count = 0
		elif indx == points_count - 1:
			new_data = new_data + '\n\n '
			cur_lineitems_count = 0
		indx += 1

	new_data = new_data.replace(' -', '-') #удаляем лишние пробелы перед знаком минус

	if (infile == True):
		with open(data_dir + input_filename[:-4] + '_output.dat', 'w') as f:
			f.write(new_data)
	else:
		return new_data

def getProjectDir():
	'''
	Возвращает полный путь к корню проекта 
	'''
	project_name = 'pansym-shell'
	pdir = os.path.dirname(os.path.abspath(__file__)) 
	return pdir.split(project_name)[0] + project_name + '\\'


if __name__ == '__main__':
	print(rotDots(10, r'D:\Projects\pansym-shell\data'))
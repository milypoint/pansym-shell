import os
from os import listdir
from os.path import isfile, join
import re #Регулярные выражения для работы со строковыми шаблонами
import glob
from rotate_foilpoints import *
import numpy as np
import matplotlib.pyplot as plt

def fileNameDecode(fname):
	'''
	Функция для извлечения метаданных из имени файла.
	Возвращает данные последовательно.
	'''
	tamplate = r'rudpos=(?P<where>.*)_backwingspan=(?P<span>.*)_ruderratio=(?P<ratio>.*)_delta=(?P<delta>.*).ou'
	m = re.match(tamplate, fname)
	return m.group('where'), float(m.group('span')), float(m.group('ratio')), float(m.group('delta'))

def isChangeData(cur_data, last_data):
	for key, value in last_data.items():
		if cur_data[key] != value: return True
	return False

if __name__ == '__main__':

	oupath = getProjectDir() + 'data\\ou_files\\' #папка с выходными файлами
	filelist = [f for f in listdir(oupath) if isfile(join(oupath, f))] #получаем список файлов
	filelist.sort(key=lambda x: os.path.getctime(oupath + x)) #Сортируем по дате создания
	
	output_data = {} #словарь с результатом парсинга выходных файлов
	test_data = []

	for file in filelist:
		#Читаем данные из *.ou файла
		with open(oupath + file, 'r') as f:
			raw_data = f.read() #чтения выходного файла

		#Для скоросной системы координат
		raw_data = raw_data.split('MZV')[1].split('CX_TREN')[0] #из полученых данных вырезаем все, кроме нужного блока
		#Для связанной системы координат
		#raw_data = raw_data.split('cxcymz:SHAR')[1].split('CXV')[0].split('\n')[1]

		#из полученого блока извлекаем експоненциальные числа, которое являются коэффициентами сил и моменов:
		tamplate = '-?\ *[0-9]+\.?[0-9]*(?:[Ee]\ *-?\ *[0-9]+)?'
		coefs = [float(x) for x in re.findall(tamplate, raw_data)] #CXV CYV CZV MXV MYV MZV
		
		data = dict()
		#считываем метаданные с имени файла и записываем в словарь:
		data['rudpos'], data['backwingspan'], data['ruderratio'], data['delta'] = fileNameDecode(file) 
		data['coefs'] = coefs #записываем в словарь коеффициэнты сил и моментов

		#Тестовый кусок...
		test_data.append({	'rudpos' : data['rudpos'], 
							'backwingspan' : data['backwingspan'],
							'ruderratio' : data['ruderratio'],
							'delta' : data['delta'],
							'coefs' : data['coefs']})

		'''
		Далее создаем вложеный словарь. 
		Здесь создаются несуществующие ключи словаря, которые являются уровнями вложеного словаря
		'''
		if data['rudpos'] not in output_data:
			output_data[data['rudpos']] = dict()
		if data['backwingspan'] not in output_data[data['rudpos']]:
			output_data[data['rudpos']][data['backwingspan']] = dict()
		if data['ruderratio'] not in output_data[data['rudpos']][data['backwingspan']]:
			output_data[data['rudpos']][data['backwingspan']][data['ruderratio']] = dict()
		output_data[data['rudpos']][data['backwingspan']][data['ruderratio']][data['delta']] = data['coefs']
	
	bool_isFirstCycle = True
	new_test_data = []
	last_data = dict()

	for item in test_data:
		if bool_isFirstCycle == True:
			bool_isFirstCycle = False
			d, mx, mz = [], [], []
			for key, value in item.items():
				if key != 'delta' and key != 'coefs':
					last_data [key] = value

		if isChangeData(item, last_data) == True:
			new_item = dict()
			for key, value in last_data.items():
				new_item [key] = value
				last_data [key] = item[key]
			new_item['kx'] = round(np.polyfit(d, mx, 1)[0], 4) 
			new_item['kz'] = round(np.polyfit(d, mz, 1)[0], 4) 
			new_test_data.append(new_item)
			d, mx, mz = [], [], []
		d.append(item['delta'])
		mx.append(item['coefs'][3])
		mz.append(item['coefs'][5])

		if item == test_data[-1]:
			new_item = dict()
			for key, value in last_data.items():
				new_item [key] = value
				last_data [key] = item[key]
			new_item['kx'] = round(np.polyfit(d, mx, 1)[0], 4) 
			new_item['kz'] = round(np.polyfit(d, mz, 1)[0], 4) 
			new_test_data.append(new_item)

	'''
	!!!Попробовать использовать коэффициенты в ствязанной системе координат
	'''
	#for item in new_test_data:
		#print(item)
	'''
	Проходим по элементам словаря и заменяем его конечную часть на словарь с масивами,
	которые содержат углы отклонения рулей, коэффициенты моментов и расчитаные еффективности руля высоты и элерона
	'''
	for rudpos in output_data:
		for backwingspan in output_data[rudpos]:
			for ruderratio in output_data[rudpos][backwingspan]:
				#массивы коефициентов моментов для разных углов отклонения
				MX = [] 
				MZ = []
				Delta = []
				for delta in output_data[rudpos][backwingspan][ruderratio]:
					MX.append(output_data[rudpos][backwingspan][ruderratio][delta][3])
					MZ.append(output_data[rudpos][backwingspan][ruderratio][delta][5])
					Delta.append(delta)
				#output_data[rudpos][backwingspan][ruderratio] = {'MX' : MX, 'MZ' : MZ, 'Delta' : Delta}
				output_data[rudpos][backwingspan][ruderratio] = dict()
				#еффективность руля относительно оси ох (элерон):
				output_data[rudpos][backwingspan][ruderratio]['kx'] = round(np.polyfit(Delta, MX, 1)[0], 4) 
				#еффективность руля относительно оси оz (руль высоты):
				output_data[rudpos][backwingspan][ruderratio]['kz'] = round(np.polyfit(Delta, MZ, 1)[0], 4) 

	'''
	Преобразуем полученный словарь в удобный вид для далнейшего построения графиков
	'''
	data = []
	for rudpos in output_data:
		for backwingspan in output_data[rudpos]:
			for ruderratio in output_data[rudpos][backwingspan]:
				d =[]
				d.append(rudpos)
				d.append(backwingspan)
				d.append(ruderratio)
				d.append(abs(output_data[rudpos][backwingspan][ruderratio]['kx']))
				d.append(abs(output_data[rudpos][backwingspan][ruderratio]['kz']))
				data.append(d)
	#print(data)
	data.sort(key=lambda x: x[2])
	front = []
	back = []
	for line in data:
		if line[0] == 'front':
			front.append(line[1:])
		else:
			back.append(line[1:])
	
	plt.figure(1)
	plt.xlabel('l2/l1')
	plt.ylabel('Eff_x_first_wing')
	plt.title('Эффективность элерона на переднем крыле')
	plt.grid(True)

	plt.figure(2)
	plt.xlabel('l2/l1')
	plt.ylabel('Eff_z_first_wing')
	plt.title('Эффективность руля высоты на переднем крыле')
	plt.grid(True)

	first_cycle = True
	prev_ratio = None #previus ruder ratio
	for line in front: #[1.25, 30.0, -0.0104, 0.0336]
		if first_cycle == True:
			first_cycle = False
			x = [] #горизонтальная ось графика (l2/l1)
			y = [] #Вертикальная ось графика kx
			y2 = [] #Вертикальная ось графика kz
			curratio = line[1]
		if line[1] != curratio:
			curratio = line[1]
			#
			plt.figure(1)
			plt.annotate(str(prev_ratio)+'%', xy=(x[-1], y[-1]), xytext=(x[-1]+abs(x[-1]*0.01), y[-1]+abs(y[-1]*0.01)))
			plt.plot(x, y, 'ro', x, y, 'k')
			plt.figure(2)
			plt.annotate(str(prev_ratio)+'%', xy=(x[-1], y2[-1]), xytext=(x[-1]+abs(x[-1]*0.01), y2[-1]+abs(y2[-1]*0.01)))
			plt.plot(x, y2, 'ro', x, y2, 'k')
			#
			x = []
			y = []
			y2 = []
		x.append(line[0]/1.25)
		y.append(line[2])
		y2.append(line[3])
		prev_ratio = line[1]

	data_dir = getProjectDir() + 'data\\images\\'
	#
	plt.figure(1)
	plt.plot(x, y, 'ro', x, y, 'k')
	plt.annotate(str(line[1])+'%', xy=(x[-1], y[-1]), xytext=(x[-1]+abs(x[-1]*0.01), y[-1]+abs(y[-1]*0.01)))
	plt.savefig(data_dir + 'ox1_img.png')
	#
	plt.figure(2)
	plt.plot(x, y2, 'ro', x, y2, 'k')
	plt.annotate(str(line[1])+'%', xy=(x[-1], y2[-1]), xytext=(x[-1]+abs(x[-1]*0.01), y2[-1]+abs(y2[-1]*0.01)))
	plt.savefig(data_dir + 'oz1_img.png')

	plt.figure(3)	
	plt.xlabel('l2/l1')
	plt.ylabel('Eff_x_second_wing')
	plt.title('Эффективность элерона на заднем крыле')
	plt.grid(True)

	plt.figure(4)
	plt.xlabel('l2/l1')
	plt.ylabel('Eff_z_second_wing')
	plt.title('Эффективность руля высоты на заднем крыле')
	plt.grid(True)

	first_cycle = True
	prev_ratio = None #previus ruder ratio
	for line in back:
		if first_cycle == True:
			first_cycle = False
			x = []
			y = []
			y2 = []
			curratio = line[1]
		if line[1] != curratio:
			curratio = line[1]
			#
			plt.figure(3)
			plt.annotate(str(prev_ratio)+'%', xy=(x[-1], y[-1]), xytext=(x[-1]+abs(x[-1]*0.01), y[-1]+abs(y[-1]*0.01)))
			plt.plot(x, y, 'ro', x, y, 'k')
			plt.figure(4)
			plt.annotate(str(prev_ratio)+'%', xy=(x[-1], y2[-1]), xytext=(x[-1]+abs(x[-1]*0.01), y2[-1]+abs(y2[-1]*0.01)))
			plt.plot(x, y2, 'ro', x, y2, 'k')
			#
			x = []
			y = []
			y2 = []
		x.append(line[0]/1.25)
		y.append(line[2])
		y2.append(line[3])
		prev_ratio = line[1]

	#
	plt.figure(3)
	plt.plot(x, y, 'ro', x, y, 'k')
	plt.annotate(str(line[1])+'%', xy=(x[-1], y[-1]), xytext=(x[-1]+abs(x[-1]*0.01), y[-1]+abs(y[-1]*0.01)))
	plt.savefig(data_dir + 'ox2_img.png')
	#
	plt.figure(4)
	plt.plot(x, y2, 'ro', x, y2, 'k')
	plt.annotate(str(line[1])+'%', xy=(x[-1], y2[-1]), xytext=(x[-1]+abs(x[-1]*0.01), y2[-1]+abs(y2[-1]*0.01)))
	plt.savefig(data_dir + 'oz2_img.png')
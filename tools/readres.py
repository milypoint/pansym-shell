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
	'''
	Функция для проверки соответсвия данных словаря last_data с данным словаря cur_data.
	Словарь last_data является "подсловарём" cur_data.

	Возвращает True если данные не совпадают.
	'''
	for key, value in last_data.items():
		if cur_data[key] != value: return True
	return False

def calcEfficiency(data):
	'''
	Расчитывает еффективность руля по координатам ох и oz

	Принимает массив словарей с данными, которые содержат:
		delta - угол отклонения руля
		coefs - массив с коеффициентами сил и моментов

	Возвращает массив словарей с расчитанной еффективностю относительно соответствующий осей
	'''
	ndata = []
	last_data = dict()

	for item in data:
		if item == data[0]: #если первый словарь из массива, то создать объекты данных
			d, mx, mz = [], [], []
			for key, value in item.items():
				if key != 'delta' and key != 'coefs':
					last_data [key] = value

		if isChangeData(item, last_data) == True: #если данные, которые не входят в расчет еффективностей, 
		#изменились, то расчитать саму еффективность и сохранить
			new_item = dict()
			for key, value in last_data.items():
				new_item [key] = value
				last_data [key] = item[key]
			new_item['kx'] = round(np.polyfit(d, mx, 1)[0], 4) 
			new_item['kz'] = round(np.polyfit(d, mz, 1)[0], 4) 
			ndata.append(new_item)
			d, mx, mz = [], [], []
		d.append(item['delta'])
		mx.append(item['coefs'][3])
		mz.append(item['coefs'][5])

		if item == data[-1]: #если последний словарь из массива, то расчитать саму еффективность и сохранить
			new_item = dict()
			for key, value in last_data.items():
				new_item [key] = value
				last_data [key] = item[key]
			new_item['kx'] = round(np.polyfit(d, mx, 1)[0], 4) 
			new_item['kz'] = round(np.polyfit(d, mz, 1)[0], 4) 
			ndata.append(new_item)
	return ndata

class Figure:
	'''
	Класс, представляющий график, с несколькими кривыми.

	Свойства класса:
		self.fignumber - номер текущего графика в системе pyplot
		self.cfg - параметры графика (применяются при вызове метода self.plot())
	'''

	def __init__(self, fignumber):
		'''
		Создает объект изображения графика.
		Создает свойства self.fignumber, self.cfg, self.curves.
		'''
		self.fignumber = fignumber
		plt.figure(fignumber)
		self.cfg = {	'title' : None,
						'xlabel' : None,
						'ylabel' : None,
						'grid' : True}
			
		self.curves = [] #список массивов точек для разных кривых

	def config(self):
		'''
		Переносит свойства класса в свойства изображения
		'''
		plt.figure(self.fignumber)
		for key, value in self.cfg.items():
			if value != None:
				if key == 'title':
					plt.title(value)
				elif key == 'xlabel':
					plt.xlabel(value)
				elif key == 'ylabel':
					plt.ylabel(value)
				elif key == 'grid':
					plt.grid(value)

	def addCurve(self, xarr, yarr, annotate=None):
		'''
		Добавляет массивы точек кривой в общий список класса

		xarr - массив точек по горизонтальной оси
		yarr - массив точек по вертикальной оси
		annotate - подпись кривой на графике
		'''
		plt.figure(self.fignumber)
		self.curves.append({'x' : xarr, 'y' : yarr, 'annotate' : annotate})

	def plot(self, infile = None):
		'''
		Передает изображение графика на вывод: 
			в файл (если infile = "путь к файлу")
			выводит на экран (если infile = None, по умолчанию)
		'''
		self.config()
		for c in self.curves:
			plt.plot(c['x'], c['y'], 'ro', c['x'], c['y'], 'k')
			if c['annotate'] != None:
				plt.annotate(str(c['annotate'])+'%', xy=(c['x'][-1], c['y'][-1]), 
					xytext=(c['x'][-1]+abs(c['x'][-1]*0.01), c['y'][-1]+abs(c['y'][-1]*0.01)))
		if infile != None:
			plt.savefig(infile)
		else:
			plt.show()


if __name__ == '__main__':

	oupath = getProjectDir() + 'data\\ou_files\\' #папка с выходными файлами
	filelist = [f for f in listdir(oupath) if isfile(join(oupath, f))] #получаем список файлов
	filelist.sort(key=lambda x: os.path.getctime(oupath + x)) #Сортируем по дате создания
	
	data = [] #словарь с результатом парсинга выходных файлов

	for file in filelist:
		#Читаем данные из *.ou файла
		with open(oupath + file, 'r') as f:
			raw_data = f.read() #чтения выходного файла

		#Для скоросной системы координат
		raw_data = raw_data.split('MZV')[1].split('CX_TREN')[0] #из полученых данных вырезаем все, кроме нужного блока

		#из полученого блока извлекаем експоненциальные числа, которое являются коэффициентами сил и моменов:
		tamplate = '-?\ *[0-9]+\.?[0-9]*(?:[Ee]\ *-?\ *[0-9]+)?'
		coefs = [float(x) for x in re.findall(tamplate, raw_data)] #CXV CYV CZV MXV MYV MZV
		
		d = dict()
		#считываем метаданные с имени файла и записываем в словарь:
		d['rudpos'], d['backwingspan'], d['ruderratio'], d['delta'] = fileNameDecode(file) 
		d['coefs'] = coefs #записываем в словарь коеффициэнты сил и моментов

		data.append({	'rudpos' : d['rudpos'], 
							'backwingspan' : d['backwingspan'],
							'ruderratio' : d['ruderratio'],
							'delta' : d['delta'],
							'coefs' : d['coefs']})
	
	data = calcEfficiency(data)

	'''
	Далее генерируем графики
	'''
	figures = []

	for num in range(0, 4):
		figures.append(Figure(num))

	for item in data:
		if item == data[0]:
			last_data = {'rudpos' : item['rudpos'], 'ruderratio' : item['ruderratio']}
			backwingspan, kx, kz = [], [], []

		if isChangeData(item, last_data) == True:
			if last_data['rudpos'] == 'front':
				figures[0].addCurve(backwingspan, kx, last_data['ruderratio'])
				figures[1].addCurve(backwingspan, kz, last_data['ruderratio'])
			elif last_data['rudpos'] == 'back':
				figures[2].addCurve(backwingspan, kx, last_data['ruderratio'])
				figures[3].addCurve(backwingspan, kz, last_data['ruderratio'])
			last_data = {'rudpos' : item['rudpos'], 'ruderratio' : item['ruderratio']}
			backwingspan, kx, kz = [], [], []

		backwingspan.append(abs(item['backwingspan']/1.25))
		kx.append(abs(item['kx']))
		kz.append(abs(item['kz']))

		if item == data[-1]:
			if last_data['rudpos'] == 'front':
				figures[0].addCurve(backwingspan, kx, last_data['ruderratio'])
				figures[1].addCurve(backwingspan, kz, last_data['ruderratio'])
			elif last_data['rudpos'] == 'back':
				figures[2].addCurve(backwingspan, kx, last_data['ruderratio'])
				figures[3].addCurve(backwingspan, kz, last_data['ruderratio'])

	data_dict = getProjectDir() + 'data/images/'
	for fig in figures:
		if fig == figures[0]:
			fig.cfg['title'] = 'Эффективность элерона на переднем крыле'
			fig.cfg['ylabel'] = 'eff_ox'
			figname = data_dict + 'figure_1_Эффективность элерона на переднем крыле.png' 
		elif fig == figures[1]:
			fig.cfg['title'] = 'Эффективность руля высоты на переднем крыле'
			fig.cfg['ylabel'] = 'eff_oz'
			figname = data_dict + 'figure_2_Эффективность руля высоты на переднем крыле.png' 
		elif fig == figures[2]:
			fig.cfg['title'] = 'Эффективность элерона на заднем крыле'
			fig.cfg['ylabel'] = 'eff_ox'
			figname = data_dict + 'figure_3_Эффективность элерона на заднем крыле.png' 
		elif fig == figures[3]:
			fig.cfg['title'] = 'Эффективность руля высоты на заднем крыле'
			fig.cfg['ylabel'] = 'eff_oz'
			figname = data_dict + 'figure_4_Эффективность руля высоты на заднем крыле.png' 
		fig.cfg['xlabel'] = 'L2/L1'
		fig.plot(figname)
import os
from os import listdir
from os.path import isfile, join
import re #Регулярные выражения для работы со строковыми шаблонами
import glob
from rotate_foilpoints import *
import numpy as np
import matplotlib.pyplot as plt
from itertools import groupby
from operator import itemgetter

def iprint(data, split=False):
	for item in data:
		print(item)
		if split:
			print()

def mkdir(dir_name):
	if not os.path.exists(dir_name):
		os.makedirs(dir_name)

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

def sortByGroup(data, group_keys, sort_key=None, split=False):
	'''
	Групирует данные по ключам group_keys, сортирует группы по ключу sort_key (опционально).

	Вход:
		data - список словарей. Словари должны иметь все ключи, в ходящие в признак группы. 
		group_keys - список ключей словаря, по которым происходит группирование
		sort_key - необязательный параметр, ключ сортировки внутри каждой группы
		split - если True, то возвращается список, содержащий группы словарей. Иначе возвращается список словарей.

	Выход:
		Список словарей, упорядоченный по (отсортированным группам, если указан ключ сортировки) группам 
	'''
	grouper = itemgetter(*group_keys)
	grouped_data = []

	for key, grp in groupby(sorted(data, key = grouper), grouper):
		group = [i for i in grp]
		if sort_key != None:
			group.sort(key = lambda k: k[sort_key])
		if split == False:
			grouped_data += group
		else:
			grouped_data.append(group)

	return grouped_data

def calcEfficiency(data):
	'''
	Расчитывает еффективность руля по координатам ох и oz

	Принимает массив словарей с данными, которые содержат:
		delta - угол отклонения руля
		coefs - массив с коеффициентами сил и моментов

	Возвращает массив словарей с расчитанной еффективностю относительно соответствующий осей
	'''
	#Группируем данные, сортируем по углу отклонения и разделяем группы:
	groups = sortByGroup(data, ['rudpos', 'backwingspan', 'ruderratio'], 'delta', True)

	ndata = []

	for group in groups:
		d, mx, mz = [], [], []
		temp_dict = { k:v for k,v in group[0].items() if k != 'delta' and k != 'coefs'}
		for item in group:
			d.append(item['delta'])
			mx.append(item['coefs'][3])
			mz.append(item['coefs'][5])
		#Сдвигаем значения коэф. момента на величину равную коэф. при нулевом отклонении руля
		#где [i for i,x in enumerate(d) if x == 0][0] - определение индекса массива нулевого отклонения
		mx = [round(x - mx[ [i for i,x in enumerate(d) if x == 0][0] ], 4) for x in mx]
		mz = [round(x - mz[ [i for i,x in enumerate(d) if x == 0][0] ], 4) for x in mz]
		#список индексов точек, входящих в аппроксимацию:
		aprx_i = [i for i,x in enumerate(d) if x >=-10 and x <=10] 
		#Списки точек, входящих в аппроксимацию:
		aprx_d = d[aprx_i[0] : aprx_i[-1] + 1]
		aprx_mx = mx[aprx_i[0] : aprx_i[-1] + 1]
		aprx_mz = mz[aprx_i[0] : aprx_i[-1] + 1]
		#Сохраняем данные:
		temp_dict['kx'] = round(np.polyfit(aprx_d, aprx_mx, 1)[0], 4) 
		temp_dict['kz'] = round(np.polyfit(aprx_d, aprx_mz, 1)[0], 4) 
		temp_dict['d'] = d
		temp_dict['mx'] = mx
		temp_dict['mz'] = mz
		temp_dict['aprx_d'] = aprx_d
		temp_dict['aprx_mx'] = aprx_mx
		temp_dict['aprx_mz'] = aprx_mz
		ndata.append(temp_dict)

	return ndata

def genMainFigs(data):

	#Группируем данные по ключам, которые не меняются для всех точек одной кривой
	data = sortByGroup(data, ['rudpos', 'ruderratio'], split=True)
	images_dir = getProjectDir() + 'data/images/' #директория, в которую записать графики
	mkdir(images_dir)

	for group in data:
		x, kx, kz = [], [], []

		for item in group:
			x.append(abs(item['backwingspan']/1.25))
			kx.append(abs(item['kx']))
			kz.append(abs(item['kz']))

		if group[0]['rudpos'] == 'front':
			plt.figure(0)
			plt.plot(x, kx, 'ro', x, kx, 'k')
			plt.annotate(str(group[0]['ruderratio'])+'%', xy=(x[-1], kx[-1]), 
				xytext=(x[-1]+abs(x[-1]*0.01), kx[-1]+abs(kx[-1]*0.01)))

			plt.figure(1)
			plt.plot(x, kz, 'ro', x, kz, 'k')
			plt.annotate(str(group[0]['ruderratio'])+'%', xy=(x[-1], kz[-1]), 
				xytext=(x[-1]+abs(x[-1]*0.01), kz[-1]+abs(kz[-1]*0.01)))
		elif group[0]['rudpos'] == 'back':
			plt.figure(2)
			plt.plot(x, kx, 'ro', x, kx, 'k')
			plt.annotate(str(group[0]['ruderratio'])+'%', xy=(x[-1], kx[-1]), 
				xytext=(x[-1]+abs(x[-1]*0.01), kx[-1]+abs(kx[-1]*0.01)))

			plt.figure(3)
			plt.plot(x, kz, 'ro', x, kz, 'k')
			plt.annotate(str(group[0]['ruderratio'])+'%', xy=(x[-1], kz[-1]), 
				xytext=(x[-1]+abs(x[-1]*0.01), kz[-1]+abs(kz[-1]*0.01)))
	
	#Конфигурируем графики:

	plt.figure(0)
	plt.title('Эффективность элерона на переднем крыле')
	plt.ylabel('eff_ox')
	plt.xlabel('L2/L1')
	plt.grid(True)
	figname = images_dir + 'figure_1_Эффективность элерона на переднем крыле.png' 
	plt.savefig(figname)

	plt.figure(1)
	plt.title('Эффективность руля высоты на переднем крыле')
	plt.ylabel('eff_oz')
	plt.xlabel('L2/L1')
	plt.grid(True)
	figname = images_dir + 'figure_2_Эффективность руля высоты на переднем крыле.png' 
	plt.savefig(figname)

	plt.figure(2)
	plt.title('Эффективность элерона на заднем крыле')
	plt.ylabel('eff_ox')
	plt.xlabel('L2/L1')
	plt.grid(True)
	figname = images_dir + 'figure_3_Эффективность элерона на заднем крыле.png' 
	plt.savefig(figname)

	plt.figure(3)
	plt.title('Эффективность руля высоты на заднем крыле')
	plt.ylabel('eff_oz')
	plt.xlabel('L2/L1')
	plt.grid(True)
	figname = images_dir + 'figure_4_Эффективность руля высоты на заднем крыле.png' 
	plt.savefig(figname)

def genMXMZFigs(data):

	images_dir = getProjectDir() + 'data/images/mxmz_delta/' #директория, в которую записать графики
	mkdir(images_dir)

	for item in data: #data[:int(len(data)/4) * 4 : int(len(data)/4)] #делаем 8 графиков для разных случаев
		plt.figure()
		plt.suptitle('Значения к-ов для:положение руля=' + str(item['rudpos']) + 
			'\nL2/L1=' + str(item['backwingspan']/1.25) +
			'\nОтносительный размах руля=' + str(item['ruderratio']) + str('%'))
		plt.xlabel('Delta')
		plt.ylabel('Mx, Mz')
		plt.grid(True)		
		#Далее создаем массивы, содержащие значения коэф-ов при линейной аппроксимации

		mx = [np.polyfit(item['aprx_d'], item['aprx_mx'], 1)[0] * x + np.polyfit(item['aprx_d'], item['aprx_mx'], 1)[1] for x in item['aprx_d']]
		mz = [np.polyfit(item['aprx_d'], item['aprx_mz'], 1)[0] * x + np.polyfit(item['aprx_d'], item['aprx_mz'], 1)[1] for x in item['aprx_d']]
		plt.plot(item['d'], item['mx'], 'rx')
		plt.plot(item['aprx_d'], mx, 'r-', label='Mx')		
		plt.plot(item['d'], item['mz'], 'bx')
		plt.plot(item['aprx_d'], mz, 'b-', label='Mz')
		plt.legend()

		plt.savefig(images_dir + 'rudpos='+ str(item['rudpos']) + 
			' spanratio=' + str(item['backwingspan']/1.25) +
			' ruderratio=' + str(item['ruderratio']) + '.png')

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
	#filelist.sort(key=lambda x: os.path.getctime(oupath + x)) #Сортируем по дате создания
	
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
	#Считаем еффективность руля:
	data = calcEfficiency(data)

	#iprint(sortByGroup(data, ['rudpos', 'ruderratio'], split=True), True)
	data = sortByGroup(data, ['rudpos', 'ruderratio'])

	
	'''	
	Далее генерируем графики
	'''
	genMainFigs(data)

	genMXMZFigs(data)

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

	#генерируем графики коэф-ов моментов от угла отклонения
	'''

	'''
	for item in data: #data[:int(len(data)/4) * 4 : int(len(data)/4)] #делаем 8 графиков для разных случаев
		plt.figure()
		plt.suptitle('Значения к-ов для:положение руля=' + str(item['rudpos']) + 
			'\nL2/L1=' + str(item['backwingspan']/1.25) +
			'\nОтносительный размах руля=' + str(item['ruderratio']) + str('%'))
		plt.xlabel('Delta')
		plt.ylabel('Mx, Mz')
		plt.grid(True)		
		#Далее создаем массивы, содержащие значения коэф-ов при линейной аппроксимации

		mx = [np.polyfit(item['aprx_d'], item['aprx_mx'], 1)[0] * x + np.polyfit(item['aprx_d'], item['aprx_mx'], 1)[1] for x in item['aprx_d']]
		mz = [np.polyfit(item['aprx_d'], item['aprx_mz'], 1)[0] * x + np.polyfit(item['aprx_d'], item['aprx_mz'], 1)[1] for x in item['aprx_d']]
		plt.plot(item['d'], item['mx'], 'rx')
		plt.plot(item['aprx_d'], mx, 'r-', label='Mx')		
		plt.plot(item['d'], item['mz'], 'bx')
		plt.plot(item['aprx_d'], mz, 'b-', label='Mz')
		plt.legend()

		plt.savefig(data_dict + 'mxmz_delta/' + 'rudpos='+ str(item['rudpos']) + 
			' spanratio=' + str(item['backwingspan']/1.25) +
			' ruderratio=' + str(item['ruderratio']) + '.png')
	'''
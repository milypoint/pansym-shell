"""Содержит класы с шаблонами текстовых блоков для генерации *.IN файла для PANSYM"""

import numpy as np
import math

from utilities import *

def genNI(ni_count, type_gen='linear', sym=False): #генерирует текст с разбивкой сетки по розмаху
	'''
	Функция генерирует массив с относительными координатами точек, 
	которые определяют распределение сетки по размаху на текущем участке крыла.

	type_gen='linear' - линейное распределение (по умолчанию)
	type_gen='cos' - распределение по косинусу
	
	Симметрия для нелинейного распределения:
	sym=False - распределение без симетрии (по умолчанию)
	sym=True - распределение симетрично относительно середины
	'''
	if type_gen == 'linear':
		return [round(x, 4) for x in np.linspace(0, 1, ni_count)]

	elif type_gen == 'cos':
		#генерируем список точек для косинусного распределения сетки
		if sym == False: #если распределение несиметричное
			return [round(math.cos(x), 4) for x in np.linspace(math.pi/2, 0, ni_count)]
		else: #если распределение симетричное
			return [round(0.5 + math.cos(x)/2, 4) for x in np.linspace(math.pi, 0, ni_count)]

def genTextNI(ni_arr):
	'''
	Функция генерирует текстовый блок с относительными координатами точек, 
	определяющих распределение сетки по размаху текущего участка крыла.

	Вход:

	ni_arr - массив точек

	Выход:

	Текстовый блок удовлетворяющий синтаксис Pansym
	'''
	text = ''
	tamplate = '%-7s'
	cur_i = 0
	for item in ni_arr:
		if cur_i == 10:
			text += '\n'
			cur_i = 0
		text += tamplate % doLenTiny(item, 6)
		cur_i += 1
	return text

class TextBlock():
	"""Базовый класс для текстового блока"""

	def __init__(self, data):
		self.text = self.block % data 

	def getText(self):
		return self.text		

class FirstBlock(TextBlock): #Пример: [%(name)-7s]: name - поле словаря, '-' - выравнивание по левому краю, 7 - ширина поля в семь знаков
	block = """--- %(name)s ---
suMekRprNchRreGplVreAitRdsGgrFneLlnTprHviS
  1  0  0 -1  1  0  1  0  0  1  0  0  0  0
< Sk  >< Bk  >< Lk  >< Xc  >< Yc  >< Zc  >< rvr >< dp  >< xend>< Smid><dAlfk><Cx0  >
%(Sk)-7s%(Bk)-7s%(Lk)-7s%(Xc)-7s%(Yc)-7s%(Zc)-7s 50.5   4.     40.    0.     0.     .0 """	

class AerofoilBlock(TextBlock):
	block = """--- aerofoil %(name)s ---
  0  0%(np)-3s 2  0 %(nu)-3s  0  0  0
NE NTE NP IB IK NU IS IM IP
< XY  ><     ><     ><     ><     ><     ><     ><     ><     ><     >
%(xy)s """

class FuselagBlock(TextBlock):
	def __init__(self):
		self.text = """ NE IT IB NS NU II SI IN NI IC IM IP IM ICO NCO(3)
  1  1  2 19 16  0 00  0  0  0  1  0  0  0  0     
--- FUSELAG ---
<Xf   ><     ><     ><     ><     ><     ><     ><     ><     ><     >
 0.     0.05   0.15   0.3    0.45   0.65   0.95   1.3    1.7    2.1
 2.5    3.5    8.3    9.1    9.9    10.7   11.5   12.5   13 
<Yf   ><     ><     ><     ><     ><     ><     ><     ><     ><     >
0.0

<Zf   ><     ><     ><     ><     ><     ><     ><     ><     ><     >
0.00

<Rf   ><     ><     ><     ><     ><     ><     ><     ><     ><     >
 0.     0.1104 0.2406 0.3782 0.4729 0.5546 0.642  0.707  0.757  0.788
 0.8    0.8    0.7834 0.7328 0.648  0.5286 0.3762 0.1906 0.02
<XM   ><YM   ><ZM   >
0.2     0.2    0.2 """


class WingBlock(TextBlock):
	block = """--- %(name)-10s ---
%(ne)-3s 2  0  2 -16 1 %(ni)-3s                        0   0        1  
 NE IT IB NS NU II NI UI NL IC IM IP IM ICO   ICOE
< NP  >< Xm  >< Ym  >< Zm  ><Ch m >< Fi  >
%(np)-7s%(Xm)-7s%(Ym)-7s%(Zm1)-7s%(Ch)-7s%(Fi)-7s

%(np)-7s%(Xm)-7s%(Ym)-7s%(Zm2)-7s%(Ch)-7s%(Fi)-7s
< z   ><     ><     ><     ><     ><     ><     ><     ><     ><     >"""
	
	def __init__(self, data):
		data['np'] = '1'
		self.data = data
		self.data['ni'] = self.genNICount(self.data)
		self.text = (self.block + '\n' + genTextNI(genNI(self.data['ni'], 'cos'))) % data

	def genNICount(self, data):
		ni = int((float(data['Zm2']) - float(data['Zm1'])) *10)
		return ni if ni > 10 else 10

class WingBlock2(WingBlock):

	def __init__(self, data):
		inside_data = self.data4Part(data, 'inside')
		inside_data['ni'] = self.genNICount(inside_data)
		outside_data = self.data4Part(data, 'outside')
		outside_data['ni'] = self.genNICount(outside_data)

		self.text = (self.block + '\n' + genTextNI(genNI(inside_data['ni'], 'cos'))) % inside_data
		self.text += '\n'
		self.text += (self.block + '\n' + genTextNI(genNI(outside_data['ni'], 'cos', sym='True'))) % outside_data

	def data4Part(self, data, part):
		'''
		Функция принимает словарь для всего крыла и возвращает словарь для одной части

		Вход:
		data - Словарь с данными для всего крыла
		part = 'inside', 'outside' - часть крыла, для которой генерируется словарь

		Выход:
		Словарь с данными для одной части крыла
		''' 

		new_data = dict()
		if part == 'inside':
			for key, value in data.items():
				if key == 'Zm0':
					new_data['Zm1'] = value
				elif key == 'Zm1':
					new_data['Zm2'] = value
				elif key == 'Zm2':
					pass
				elif key == 'name':
					new_data[key] = value + ' part 1'
				elif key == 'ne' and value.find('-') != -1:
					new_data[key] = value.replace('-', '')
				else:
					new_data[key] = value
			new_data['np'] = '1'
		elif part == 'outside':
			for key, value in data.items():
				if key == 'ne':
					if value.find('-') != -1:
						new_data[key] = str(int(value) - 1)
					else:
						new_data[key] = str(int(value) + 1) 
				elif key == 'name':
					new_data[key] = value + ' part 2'
				else:
					new_data[key] = value
			new_data['np'] = '2'
			
		return new_data


class EndBlock(TextBlock):
	block = """ANGPEL
 0.    2.25    0.0    0.
KRIGHTS
  1  1  0
Mach   Alf    Beta   Hekr   W1     W2     V8     Reinol
%(Mach)-7s2.     0.0    .50     .50    .50    6. 
<     ><     ><     ><     ><     ><     ><     ><     ><     ><     >"""

if __name__ == '__main__':
	
	print(genTextNI(genNI(20, 'cos', True)))

	


	
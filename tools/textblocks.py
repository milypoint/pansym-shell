"""Содержит класы с шаблонами текстовых блоков для генерации *.IN файла для PANSYM"""

import numpy as np
import math
class TextBlock():
	"""Базовый класс для текстового блока"""

	def __init__(self, data):
		self.text = self.__doc__ % data 

	def getText(self):
		return self.text		

class FirstBlock(TextBlock): #Пример: [%(name)-7s]: name - поле словаря, '-' - выравнивание по левому краю, 7 - ширина поля в семь знаков
	"""--- %(name)s ---
suMekRprNchRreGplVreAitRdsGgrFneLlnTprHviS
  1  0  0 -1  1  0  1  0  0  1  0  0  0  0
< Sk  >< Bk  >< Lk  >< Xc  >< Yc  >< Zc  >< rvr >< dp  >< xend>< Smid><dAlfk><Cx0  >
%(Sk)-7s%(Bk)-7s%(Lk)-7s%(Xc)-7s%(Yc)-7s%(Zc)-7s 50.5   4.     40.    0.     0.     .0 """	

class AerofoilBlock(TextBlock):
	"""--- aerofoil %(name)s ---
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
	"""--- %(name)-10s ---
%(ne)-3s 2  0 %(ns)-3s-16 1  20                        0   0        1  
 NE IT IB NS NU II NI UI NL IC IM IP IM ICO   ICOE
< NP  >< Xm  >< Ym  >< Zm  ><Ch m >< Fi  >
 1     %(Xm)-7s%(Ym)-7s%(Zm1)-7s%(Ch)-7s%(Fi)-7s

 1     %(Xm)-7s%(Ym)-7s%(Zm2)-7s%(Ch)-7s%(Fi)-7s
< z   ><     ><     ><     ><     ><     ><     ><     ><     ><     >
0.     0.0526 0.1052 0.1578 0.2105 0.2631 0.3157 0.3684 0.4210 0.4736 
0.5263 0.5789 0.6315 0.6842 0.7368 0.7894 0.8421 0.8947 0.9473 1.     """

class WingBlock2(TextBlock):
	"""--- %(name)s ---
%(ne)-3s 2  0 %(ns)-3s-16 1  20                        0   0        1  
 NE IT IB NS NU II NI UI NL IC IM IP IM ICO   ICOE
< NP  >< Xm  >< Ym  >< Zm  ><Ch m >< Fi  >
 1     %(Xm)-7s%(Ym)-7s%(Zm0)-7s%(Ch)-7s%(Fi)-7s

 1     %(Xm)-7s%(Ym)-7s%(Zm1)-7s%(Ch)-7s%(Fi)-7s

 2     %(Xm)-7s%(Ym)-7s%(Zm1)-7s%(Ch)-7s%(Fi)-7s

 2     %(Xm)-7s%(Ym)-7s%(Zm2)-7s%(Ch)-7s%(Fi)-7s
< z   ><     ><     ><     ><     ><     ><     ><     ><     ><     >
0.     0.0526 0.1052 0.1578 0.2105 0.2631 0.3157 0.3684 0.4210 0.4736 
0.5263 0.5789 0.6315 0.6842 0.7368 0.7894 0.8421 0.8947 0.9473 1.     """
  

class EndBlock(TextBlock):
	"""ANGPEL
 0.    2.25    0.0    0.
KRIGHTS
  1  1  0
Mach   Alf    Beta   Hekr   W1     W2     V8     Reinol
%(Mach)-7s2.     0.0    .50     .50    .50    6. 
<     ><     ><     ><     ><     ><     ><     ><     ><     ><     >"""

def doLenTiny7(s): #обрезает строку в 7 знаков
	s = str(s)
	if len(s) > 7:
		return s[:7]
	else:
		return s

def doLenTiny6(s): #обрезает строку в 7 знаков
	s = str(s)
	if len(s) > 6:
		return s[:6]
	else:
		return s

def doLenTiny3(s): #обрезает строку в 3 знака
	s = str(s)
	if len(s) > 3:
		return s[:3]
	else:
		return s

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
		return np.linspace(0, 1, ni_count)

	elif type_gen == 'cos':
		list_angles = [x for x in np.linspace(math.pi/2, 0 if sum==False else -math.pi/2, ni_count)]
		ni_arr = []
		for item in list_angles:
			if item == list_angles[0]:
				last = math.cos(item)
				ni_arr.append(round(math.cos(item), 4))
			else:
				ni_arr.append(round(math.cos(item), 4))
				last = math.cos(item)
		if sym == False:
			return ni_arr
		else:
			#обрезаем массив по середине (включая середину для непарного количества элементов)
			ni_arr = ni_arr[:int(len(ni_arr)/2) + (1 if ni_count%2 != 0 else 0)]
			#делим надвое каждый элемент массива
			ni_arr = [x/2 for x in ni_arr]
			#добавлям к массиву "симметричную" часть
			ni_arr += [0.5 + 0.5 - x for x in ni_arr[::-1]]
			#возвращаем значение (если непарное кол-во элементов - удаляем дублирущийся элемент в середине массива)
			return(ni_arr if ni_count%2==0 else ni_arr[:int(len(ni_arr)/2)] + ni_arr[int(len(ni_arr)/2)+1:])

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
		text += tamplate % doLenTiny6(item)
		cur_i += 1
	return text


if __name__ == '__main__':
	
	print(genTextNI(genNI(21, 'cos', True)))
	


	
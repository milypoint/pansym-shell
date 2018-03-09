'''
Генерация расчета с использование модуля Pansym
'''
from textblocks import *
from rotate_foilpoints import *
import time

if __name__ == '__main__':

	bool_do_calc = True #Нужно ли делать основной расчет (использовать для отладки)

	Mach = 0.06 #число Маха

	b = 0.25 #Хорда крыла (в даной задаче для переднего и заднего одинакова)
	x_1 = 0.5 #Положение передней кропки первого крыла по оси Х
	x_2 = 1.5 #Положение передней кропки второго крыла по оси Х
	y_1 = 0.125 #Положение передней кропки второго крыла по оси У
	y_2 = - y_1
	f_wingspan = 5 * b #Размах переднего крыла

	#ranges:
	#e_wingspan = [x / 100 for x in range(int(f_wingspan * 100), int(f_wingspan*160), 10)]
	e_wingspan = [ f_wingspan * x / 100 for x in range(100, 165, 5)]
	rudders_ratio = [x for x in range(30, 90, 20)] 
	where_rudders = [x for x in range(1, 3)]
	delta = [x for x in range(-20, 30, 10)] #угол отклонения рулей

	print('\n --- Ranges --- \n')
	print('Back wingspan: ' + str(e_wingspan))
	print('Rudders ratio: ' + str(rudders_ratio))
	print('Ruders position: ' + str(where_rudders))
	print('Delta: ' + str(delta) + '\n')

	centerOfMass = { 'x' : ((x_2 + 0.25*b) - (x_1 + 0.25*b))*0.45 + x_1 + 0.25*b, 'y' : 0, 'z' : 0}

	calc_count = 0
	for w_r in where_rudders:
		for r_r in rudders_ratio:
			for e_w in e_wingspan:
				for d in delta:
					calc_count += 1

	print('Cycles count: ' + str(calc_count))
	
	calc_count = 1
	time_count = time.clock() #инициализируемсчетчик времени
	for w_r in where_rudders:
		for r_r in rudders_ratio:
			for e_w in e_wingspan:
				for d in delta:
					sumtext = ''
					#Создаем словарь для вставки в блок с управляющей информацией
					data = dict()
					data['name'] = 'tandem'
					data['Sk'] = doLenTiny7(f_wingspan * b + e_w * b)
					data['Bk'] = doLenTiny7(b)
					data['Lk'] = doLenTiny7((f_wingspan + e_w)/2)
					data['Xc'] = doLenTiny7(centerOfMass['x'])
					data['Yc'] = doLenTiny7(centerOfMass['y'])
					data['Zc'] = doLenTiny7(centerOfMass['z'])
					first_block = FirstBlock(data)
					sumtext += first_block.getText() + '\n'

					#Создаем словарь для вставки в блок с профилем
					data = dict()
					data['name'] = 'SD 8040'
					data['np'] = doLenTiny3(1)
					data['nu'] = doLenTiny3(45)
					data['xy'] = rotDots(0)
					foil_1 = AerofoilBlock(data)
					sumtext += foil_1.getText() + '\n'

					#Создаем словарь для вставки в блок с профилем с откошеной кромкой
					data = dict()
					data['name'] = 'SD 8040 with deflected edge on angle ' + str(d)
					data['np'] = doLenTiny3(2)
					data['nu'] = doLenTiny3(45)
					data['xy'] = rotDots(d)
					foil_1 = AerofoilBlock(data)
					sumtext += foil_1.getText() + '\n'

					#текстовый блок с указанием фюзеляжа генерируем без вставок
					fus = FuselagBlock()
					sumtext += fus.getText() + '\n'

					cur_ne = 2
					
					#Создаем словарь для вставки в блок с крылом
					if w_r == 1: #если рули на переднем крыле
						
						#для первого крыла
						data = dict()
						data['name'] = 'first wing with deflected edge'
						data['ne'] = doLenTiny3(cur_ne); cur_ne += 1
						data['ns'] = doLenTiny3(4)
						data['ni'] = doLenTiny3(19)
						data['Xm'] = doLenTiny7(x_1)
						data['Ym'] = doLenTiny7(y_1)
						data['Zm0'] = doLenTiny7(0)						
						data['Zm1'] = doLenTiny7(f_wingspan - f_wingspan*r_r/100)
						data['Zm2'] = doLenTiny7(f_wingspan)
						data['Ch'] = doLenTiny7(b)
						data['Fi'] = doLenTiny7(2)

						f_wing = WingBlock2(data)
						sumtext += f_wing.getText() + '\n'

						#для второго крыла
						data = dict()
						data['name'] = 'second wing'
						data['ne'] = doLenTiny3(-cur_ne); cur_ne += 1
						data['ns'] = doLenTiny3(2)
						data['ni'] = doLenTiny3(19)
						data['Xm'] = doLenTiny7(x_2)
						data['Ym'] = doLenTiny7(y_2)
						data['Zm1'] = doLenTiny7(0)
						data['Zm2'] = doLenTiny7(e_w)
						data['Ch'] = doLenTiny7(b)
						data['Fi'] = doLenTiny7(0)

						e_wing = WingBlock(data)
						sumtext += e_wing.getText() + '\n'
					else: #если рули на заднем крыле
						#для первого крыла
						data = dict()
						data['name'] = 'first wing'
						data['ne'] = doLenTiny3(cur_ne); cur_ne += 1
						data['ns'] = doLenTiny3(2)
						data['ni'] = doLenTiny3(19)
						data['Xm'] = doLenTiny7(x_1)
						data['Ym'] = doLenTiny7(y_1)
						data['Zm1'] = doLenTiny7(0)
						data['Zm2'] = doLenTiny7(f_wingspan)
						data['Ch'] = doLenTiny7(b)
						data['Fi'] = doLenTiny7(2)

						f_wing = WingBlock(data)
						sumtext += f_wing.getText() + '\n'

						#для второго крыла
						data = dict()
						data['name'] = 'second wing with deflected edge'
						data['ne'] = doLenTiny3(-cur_ne); cur_ne += 1
						data['ns'] = doLenTiny3(4)
						data['ni'] = doLenTiny3(19)
						data['Xm'] = doLenTiny7(x_2)
						data['Ym'] = doLenTiny7(y_2)
						data['Zm0'] = doLenTiny7(0)		
						#Замечание!				
						#data['Zm1'] = doLenTiny7(e_w - e_w*r_r/100) #отношение относительно текущего крыла
						data['Zm1'] = doLenTiny7(f_wingspan - f_wingspan*r_r/100) #отношение относительно переднего крыла
						data['Zm2'] = doLenTiny7(e_w)
						data['Ch'] = doLenTiny7(b)
						data['Fi'] = doLenTiny7(0)

						f_wing = WingBlock2(data)
						sumtext += f_wing.getText() + '\n'

					#Для последнего блока
					data = dict()
					data['Mach'] = doLenTiny7(Mach)
					endblock = EndBlock(data)
					sumtext += endblock.getText() + '\n'

					'''
					На данном этапе блок текса пригоден для использование для расчета
					Далее запишем текстовый блок в соответсвующий файл
					'''
					if bool_do_calc == True:
						pansym_dir = '\\PANSYM'
						cur_dir = os.path.dirname(os.path.abspath(__file__))
						data_dir = '\\output_files'
						#Сгенерируем имя файла, которое содержит параметры расчета
						file_name = 'rudpos=%(where)s_backwingspan=%(span)s_ruderratio=%(ratio)s_delta=%(delta)s'
						data = dict()
						data['where'] = 'front' if w_r == 1 else 'back' #расположение руля - на переднем или заднем крыле
						data['span'] = str(e_w) #размах заднего крыла (размах переднего строго задан и не изменяется)
						data['ratio'] = str(r_r) #процентное соотношение размаха крыла с размахом руля, расположеном на нем
						data['delta'] = str(d) #угол отклонения руля

						#запись текстового блока в файл для расчета
						with open(cur_dir + pansym_dir + '\\' + 'tandem' + '.in', 'w') as f:
							f.write(sumtext) #запись текстового блока в файл 

						#запускаем модуль пансима
						import subprocess
						filepath = cur_dir + "/PANSYM/run_pan.bat"
						p = subprocess.Popen(filepath, shell=True, stdout = subprocess.PIPE)
						stdout, stderr = p.communicate()
						print(p.returncode) # is 0 if success

						#Копируем файл с результатами в соответствующую папку
						with open(cur_dir + pansym_dir + '\\' + 'tandem' + '.ou', 'r') as f:
							out_data = f.read() #чтение из выходного файла *.ou 

						os.remove(cur_dir + pansym_dir + '\\' + 'tandem' + '.ou')#удаляем на всякий случай файл с результатом расчета

						with open(cur_dir + data_dir + '\\' + file_name % data + '.ou', 'w') as f:
							f.write(out_data) #запись текстового блока в файл в соответствующей директории со всеми выходными файлами

						#Счетчики:
						print('Cycle time: ' + str(round(time.clock() - time_count, 2)) + ' sec')
						time_count = time.clock()
						print('Cycle number: ' + str(calc_count))
						calc_count += 1
'''
Генерация расчета с использование модуля Pansym
'''
import time
import subprocess #для запуска батника
import multiprocessing
from os import getpid
import zipfile

from utilities import *
from textblocks import *
from rotate_foilpoints import *


def runPansymBat(batfile):
	'''
	Функция для запуска *.bat файла
	batfile - полный путь к файлу
	'''
	p = subprocess.Popen(batfile, shell=True, stdout = subprocess.PIPE)
	stdout, stderr = p.communicate()
	print(p.returncode) # is 0 if success

def pansymWorker(data): 
	'''
	Функция для расчета в пансиме по входным данным.
	data - словарь, содержащий поля:
		sumtext - текстовый блок для записи в *.in файл
		file_name - имя файла, содержащее метаданные, для записи в папку с *.ou файлами
	'''
	sumtext = data['sumtext']
	ou_filename = data['file_name']
	process_id = getpid()
	pansym_dir = getProjectDir() + 'tools\\PANSYM\\'
	ou_dir = getProjectDir() + '\\data\\ou_files\\'
	temp_pansym_dir = pansym_dir + 'Temp\\' + str(process_id)
	#Создаем временную папку для Пансима
	if not os.path.exists(temp_pansym_dir):
		os.makedirs(temp_pansym_dir)
		#Розпаковываем модуль мансима и батник во временную папку
		zip_ref = zipfile.ZipFile(pansym_dir + 'Pansym98.zip', 'r')
		zip_ref.extractall(temp_pansym_dir)
		zip_ref.close()

	#запись текстового блока в файл для расчета
	with open(temp_pansym_dir + '\\' + 'tandem' + '.in', 'w') as f:
		f.write(sumtext)

	#запускаем модуль пансима
	runPansymBat(temp_pansym_dir + r"\run_pan.bat")

	#Копируем файл с результатами в соответствующую папку
	with open(temp_pansym_dir + r'\tandem.ou', 'r') as f:
		out_data = f.read() #чтение из выходного файла *.ou 
	os.remove(temp_pansym_dir + r'\tandem.ou') #удаляем на всякий случай файл с результатом расчета

	mkdir(ou_dir)
	with open(ou_dir + '\\' + ou_filename, 'w') as f:
		f.write(out_data) #запись текстового блока в файл в соответствующей директории со всеми выходными файлами

if __name__ == '__main__':

	BEFORE = time.clock()

	bool_do_calc = True #Нужно ли делать основной расчет (использовать для отладки)

	Mach = 0.06 #число Маха
	b = 0.25 #Хорда крыла (в даной задаче для переднего и заднего одинакова)
	x_1 = 0.5 #Положение передней кропки первого крыла по оси Х
	x_2 = 1.5 #Положение передней кропки второго крыла по оси Х
	y_1 = 0.125 #Положение передней кропки второго крыла по оси У
	y_2 = - y_1
	f_wingspan = 5 * b #Размах переднего крыла

	#ranges:
	e_wingspan = [ f_wingspan * x / 100 for x in range(100, 170, 10)]
	rudders_ratio = [x for x in range(30, 90, 20)] 
	where_rudders = [x for x in range(1, 3)]
	delta = [x for x in range(-25, 30, 5)] #угол отклонения рулей

	print('\n --- Ranges --- \n')
	print('Back wingspan: ' + str(e_wingspan))
	print('Rudders ratio: ' + str(rudders_ratio))
	print('Ruders position: ' + str(where_rudders))
	print('Delta: ' + str(delta) + '\n')

	calc_count = 0
	for w_r in where_rudders:
		for r_r in rudders_ratio:
			for e_w in e_wingspan:
				for d in delta:
					calc_count += 1

	print('Cycles count: ' + str(calc_count))

	proceses_data = []#данные для каждого расчета (процесса)

	calc_count = 1
	time_count = time.clock() #инициализируем счетчик времени

	for w_r in where_rudders:
		for r_r in rudders_ratio:
			for e_w in e_wingspan:
				for d in delta:
					sumtext = ''
					#центр масс расчитывается в зависимости от соотношения размахов крыльев
					centerOfMass = { 	'x' : ((x_2 + 0.25*b) - (x_1 + 0.25*b))*(e_w/(e_w + 1.25) - 0.05) + x_1 + 0.25*b, 
										'y' : 0, 
										'z' : 0}
					#Создаем словарь для вставки в блок с управляющей информацией
					data = dict()
					data['name'] = 'tandem'
					data['Sk'] = doLenTiny(f_wingspan*b + e_w*b, 7)
					data['Bk'] = doLenTiny(2*b, 7)
					data['Lk'] = doLenTiny((f_wingspan + e_w)/2, 7)
					data['Xc'] = doLenTiny(centerOfMass['x'], 7)
					data['Yc'] = doLenTiny(centerOfMass['y'], 7)
					data['Zc'] = doLenTiny(centerOfMass['z'], 7)
					first_block = FirstBlock(data)
					sumtext += first_block.getText() + '\n'

					#Создаем словарь для вставки в блок с профилем
					data = dict()
					data['name'] = 'SD 8040'
					data['np'] = doLenTiny(1, 3)
					data['nu'] = doLenTiny(45, 3)
					data['xy'] = rotDots(0)
					foil_1 = AerofoilBlock(data)
					sumtext += foil_1.getText() + '\n'

					#Создаем словарь для вставки в блок с профилем с откошеной кромкой
					data = dict()
					data['name'] = 'SD 8040 with deflected edge on angle ' + str(d)
					data['np'] = doLenTiny(2, 3)
					data['nu'] = doLenTiny(45, 3)
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
						data['ne'] = doLenTiny(cur_ne, 3); cur_ne += 2
						data['ni'] = doLenTiny(20, 3)
						data['Xm'] = doLenTiny(x_1, 7)
						data['Ym'] = doLenTiny(y_1, 7)
						data['Zm0'] = doLenTiny(0, 7)
						data['Zm1'] = doLenTiny(f_wingspan - f_wingspan*r_r/100, 7)
						data['Zm2'] = doLenTiny(f_wingspan, 7)
						data['Ch'] = doLenTiny(b, 7)
						data['Fi'] = doLenTiny(2, 7)

						f_wing = WingBlock2(data)
						sumtext += f_wing.getText() + '\n'

						#для второго крыла
						data = dict()
						data['name'] = 'second wing'
						data['ne'] = doLenTiny(-cur_ne, 3); cur_ne += 1
						data['ni'] = doLenTiny(20, 3)
						data['Xm'] = doLenTiny(x_2, 7)
						data['Ym'] = doLenTiny(y_2, 7)
						data['Zm1'] = doLenTiny(0, 7)
						data['Zm2'] = doLenTiny(e_w, 7)
						data['Ch'] = doLenTiny(b, 7)
						data['Fi'] = doLenTiny(0, 7)

						e_wing = WingBlock(data)
						sumtext += e_wing.getText() + '\n'
					else: #если рули на заднем крыле
						#для первого крыла
						data = dict()
						data['name'] = 'first wing'
						data['ne'] = doLenTiny(cur_ne, 3); cur_ne += 1
						data['ni'] = doLenTiny(20, 3)
						data['Xm'] = doLenTiny(x_1, 7)
						data['Ym'] = doLenTiny(y_1, 7)
						data['Zm1'] = doLenTiny(0, 7)
						data['Zm2'] = doLenTiny(f_wingspan, 7)
						data['Ch'] = doLenTiny(b, 7)
						data['Fi'] = doLenTiny(2, 7)

						f_wing = WingBlock(data)
						sumtext += f_wing.getText() + '\n'

						#для второго крыла
						data = dict()
						data['name'] = 'second wing with deflected edge'
						data['ne'] = doLenTiny(-cur_ne, 3); cur_ne += 2
						data['ni'] = doLenTiny(20, 3)
						data['Xm'] = doLenTiny(x_2, 7)
						data['Ym'] = doLenTiny(y_2, 7)
						data['Zm0'] = doLenTiny(0, 7)		
						data['Zm1'] = doLenTiny(e_w - f_wingspan*r_r/100, 7) #отношение относительно переднего крыла
						data['Zm2'] = doLenTiny(e_w, 7)
						data['Ch'] = doLenTiny(b, 7)
						data['Fi'] = doLenTiny(0, 7)

						e_wing = WingBlock2(data)
						sumtext += e_wing.getText() + '\n'

					#Для последнего блока
					data = dict()
					data['Mach'] = doLenTiny(Mach, 7)
					endblock = EndBlock(data)
					sumtext += endblock.getText() + '\n'

					'''
					На данном этапе блок текса готов для использование для расчета
					Далее запишем текстовый блок в соответсвующий файл
					'''
					if bool_do_calc == True:

						#Сгенерируем имя файла, которое содержит параметры расчета
						data = dict()
						data['where'] = 'front' if w_r == 1 else 'back' #расположение руля - на переднем или заднем крыле
						data['span'] = str(e_w) #размах заднего крыла (размах переднего строго задан и не изменяется)
						data['ratio'] = str(r_r) #процентное соотношение размаха крыла с размахом руля, расположеном на нем
						data['delta'] = str(d) #угол отклонения руля
						file_name = 'rudpos=%(where)s_backwingspan=%(span)s_ruderratio=%(ratio)s_delta=%(delta)s' % data + '.ou'
						
						proceses_data.append({'sumtext':sumtext, 'file_name':file_name, 'calc_count':calc_count})
	
	rmdir(getProjectDir() + '\\data\\ou_files')
	pool = multiprocessing.Pool()
	pool.map(pansymWorker, proceses_data)
	rmdir(getProjectDir() + 'tools\\PANSYM\\Temp')

	print('Program finished in ' + str(round(time.clock() - BEFORE, 1)) + 's')	
import os
import shutil

def doLenTiny(s, slen):
	'''
	Возвращает строку s длинной не более slen знаков
	'''
	s = str(s)
	if len(s) > slen:
		return s[:slen]
	else:
		return s

def getProjectDir():
	'''
	Возвращает полный путь к корню проекта. 
	Файл с этой функцией должен находится в папке на уровень ниже относительно
	папки проекта.
	'''
	pdir = os.path.dirname(os.path.abspath(__file__)) 

	return pdir[:-pdir[::-1].find('\\')] 

def iprint(data, split=False):
	'''
	Выводит в консоль элементы списка.
	Разделяет элементы пустой строкой если split = True
	'''
	for item in data:
		print(item)
		if split:
			print()

def mkdir(dir_name):
	'''
	Создает директорию dir_name
	'''
	if not os.path.exists(dir_name):
		os.makedirs(dir_name)

def rmdir(dir_name):
	'''
	Удаляет директорию dir_name
	'''
	if os.path.exists(dir_name):
		shutil.rmtree(dir_name)	
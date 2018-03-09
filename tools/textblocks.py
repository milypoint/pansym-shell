"""Содержит класы с шаблонами текстовых блоков для генерации *.IN файла для PANSYM"""

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
%(ne)-3s 2  0 %(ns)-3s-16 1 %(ni)-3s                        0   0        1  
 NE IT IB NS NU II NI UI NL IC IM IP IM ICO   ICOE
< NP  >< Xm  >< Ym  >< Zm  ><Ch m >< Fi  >
 1     %(Xm)-7s%(Ym)-7s%(Zm1)-7s%(Ch)-7s%(Fi)-7s

 1     %(Xm)-7s%(Ym)-7s%(Zm2)-7s%(Ch)-7s%(Fi)-7s
< z   ><     ><     ><     ><     ><     ><     ><     ><     ><     >
0.0    0.0555  0.1111 0.1666 0.2222 0.2777 0.3333 0.3888 0.4444 0.5000
0.5555 0.6111  0.6666 0.7222 0.7777 0.8333 0.8888 0.9444 1.0"""

class WingBlock2(TextBlock):
	"""--- %(name)s ---
%(ne)-3s 2  0 %(ns)-3s-16 1 %(ni)-3s                        0   0        1  
 NE IT IB NS NU II NI UI NL IC IM IP IM ICO   ICOE
< NP  >< Xm  >< Ym  >< Zm  ><Ch m >< Fi  >
 1     %(Xm)-7s%(Ym)-7s%(Zm0)-7s%(Ch)-7s%(Fi)-7s

 1     %(Xm)-7s%(Ym)-7s%(Zm1)-7s%(Ch)-7s%(Fi)-7s

 2     %(Xm)-7s%(Ym)-7s%(Zm1)-7s%(Ch)-7s%(Fi)-7s

 2     %(Xm)-7s%(Ym)-7s%(Zm2)-7s%(Ch)-7s%(Fi)-7s
< z   ><     ><     ><     ><     ><     ><     ><     ><     ><     >
0.0    0.0555  0.1111 0.1666 0.2222 0.2777 0.3333 0.3888 0.4444 0.5000
0.5555 0.6111  0.6666 0.7222 0.7777 0.8333 0.8888 0.9444 1.0"""
  

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

def doLenTiny3(s): #обрезает строку в 3 знака
	s = str(s)
	if len(s) > 3:
		return s[:3]
	else:
		return s


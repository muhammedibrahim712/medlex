from pdf2image import *

def test():
	cnt, files = pdf2image('2017.12.02_Nees-ricardo hernandez3-interview.pdf')
	print(str(cnt))
	print(files)

if __name__ == '__main__':
	test()


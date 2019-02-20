import PIL
import os, sys
from os import path
import subprocess
import argparse
from fpdf import fpdf
import shutil
from django.conf import settings

def delete_files(folder):	
	for the_file in os.listdir(folder):
	    file_path = os.path.join(folder, the_file)
	    try:
	        if os.path.isfile(file_path):
	            os.unlink(file_path)
	        #elif os.path.isdir(file_path): shutil.rmtree(file_path)
	    except Exception as e:
	        print(e)

def pdf2image(pdf_name):
	images_folder = os.path.join(settings.STATIC_ROOT, 'pdf_image')
	pdf_path = os.path.join(settings.STATIC_ROOT, 'pdf', pdf_name)

	delete_files(images_folder)
	
	cmd = 'convert -alpha activate -density ' + '150' + ' \"' + pdf_path + '\" \"' + images_folder + '\\a.png\"'

	p = subprocess.Popen(cmd, shell=True)
	p.communicate()

	files = []
	for f in os.listdir(images_folder + "\\"):
		l = len(f)
		if f[l-4:] == ".png":
			files.append(f)

	if len(files) == 1:
		os.rename(images_folder + '\\a.png', images_folder + '\\a-0.png')
		files = [];
		files.append('a-0.png')

	return files

# if __name__ == '__main__':

# 	pdf_path = "2017.12.02_Nees-ricardo hernandez3-interview.pdf"
# 	# pdf_path = "case law 3.pdf"
# 	# pdf_path = "Case Chronology.pdf"

# 	cnt, files = pdf2image(pdf_path)
# 	print(str(cnt))
# 	print(files)
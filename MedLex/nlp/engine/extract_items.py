from .extract import *
import PIL
import os
import subprocess
import argparse
import cv2
import pytesseract
from PIL import Image
import re
from datetime import datetime
from dateutil.parser import parse
from django.conf import settings
from dateutil import parser
# import datefinder

def is_date(string):
	try:
		parse(string)
		return True
	except ValueError:
		return False

def isDigitLetter(c):
	if c >='0' and c <= '9':
		return True
	if c >='a' and c <= 'z':
		return True
	if c >= 'A' and c <= 'Z':
		return True

	return False

# Get all words and its positions
def extract_items(img_name, tag_map, page_num, year_criteria = -1):
	year_criteria = int(year_criteria)
	print(year_criteria)

	redaction_list = []

	img_path = os.path.join(settings.STATIC_ROOT, 'pdf_image', img_name)
	img = cv2.imread(img_path)

	# Convert image from RGB to GRAY
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	# apply thresholding to preprocess the image
	gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

	# save gray image as temp image and delete this temp image after ocr
	filename = "{}.png".format(os.getpid())
	cv2.imwrite(filename, gray)

	tmp_im = Image.open(filename)
	text = pytesseract.image_to_data(tmp_im)
	im_width, im_height = tmp_im.size

	split_data = re.split('\t|\n', text)
	ele_cnt = len(split_data)

	os.remove(filename)

	# get the word and its position list
	words = []
	positions = []

	cur_ind = 12
	while(cur_ind < ele_cnt - 12):
		if split_data[cur_ind + 1] == "-1":
			cur_ind = cur_ind + 12
			continue

		tmp_word = split_data[cur_ind + 11].strip(' \t\n\r')

		tmp_pos = []
		tmp_pos.append(int(split_data[cur_ind + 6]))
		tmp_pos.append(int(split_data[cur_ind + 7]))
		tmp_pos.append(int(split_data[cur_ind + 8]))		
		tmp_pos.append(int(split_data[cur_ind + 9]))

		if tmp_word != '' and tmp_pos[0] >= 200:
			words.append(tmp_word)
			positions.append(tmp_pos)
			# print(tmp_word)
			# print(str(tmp_pos[0]))			

		cur_ind = cur_ind + 12

	words_cnt = len(words)
	# print(str(words_cnt))

	
	# get the text of image in img_path
	txt = ""
	cnt = 0

	for w in words:			
		txt = txt + " " + w
		cnt = cnt + 1

	print(txt)

	
	# get the name list from the text
	if('Names' in tag_map):
		print("NAMES:")

		names = name_extract(txt)
		full_names = []

		ind = 0
		cur_name = ''
		while(True):
			if ind >= cnt:
				break

			if isDigitLetter(words[ind][len(words[ind]) - 1]) == False and words[ind][:len(words[ind])-1] in names:
				cur_name = cur_name + ' ' + words[ind][:len(words[ind])-1]
				full_names.append(cur_name.strip())
				cur_name = ''
				ind = ind + 1
				continue

			if words[ind] in names:
				cur_name = cur_name + ' ' + words[ind]
			else:
				if cur_name != '':
					full_names.append(cur_name.strip())
					cur_name = ''

			ind = ind + 1

		print(full_names)
		for str in full_names:
			redaction_object = {}
			redaction_object['str'] = str
			redaction_object['tag_id'] = tag_map['Names']
			redaction_object['page'] = page_num
			redaction_list.append(redaction_object)


	# get the birthday list from the text
	if('Date of birth' in tag_map):
		print("DATES: ")
		dates = []

		date_w = ''
		pre_w = ''
		ind = 0
		while(True):
			if ind >= words_cnt:
				break
			if is_date(date_w + ' ' + words[ind]) == False:
				ind = ind + 1
				continue
			while(is_date(date_w + ' ' + words[ind]) == True):
				date_w = date_w + ' ' + words[ind]
				ind = ind + 1
				if ind >= words_cnt:
					break

			if len(date_w) > 5 and date_w != '':
				year_ = datetime.today().year - parse(date_w.strip()).year
				if year_ > year_criteria:				
					dates.append(date_w.strip())
				# dt = parser.parse(date_w)
				# dates.append(datetime.strftime(dt,'%b %d, %Y'))

			date_w = ''
			ind = ind + 1

		print(dates)
		for str in dates:
			redaction_object = {}
			redaction_object['str'] = str
			redaction_object['tag_id'] = tag_map['Date of birth']
			redaction_object['page'] = page_num
			redaction_list.append(redaction_object)


	# get the email list from the text
	if('Email addresses' in tag_map):
		print("e-mail: ")

		emails = email_extract(txt)
		for str in emails:
			redaction_object = {}
			redaction_object['str'] = str
			redaction_object['tag_id'] = tag_map['Email addresses']
			redaction_object['page'] = page_num
			redaction_list.append(redaction_object)
		print(emails)

	
	# get the address list from the text
	if ('Addresses' in tag_map):
		print("Addresses: ")

		addresses = address_extract(txt)
		for str in addresses:
			redaction_object = {}
			redaction_object['str'] = str
			redaction_object['tag_id'] = tag_map['Addresses']
			redaction_object['page'] = page_num
			redaction_list.append(redaction_object)
		print(addresses)
	
	if('Phone numbers' in tag_map):
		print("PhoneNum: ")

		t_phonenums = phonenum_extract(txt)
		phonenums = []
		for phonenum in t_phonenums:
			# print(type(phonenum))
			# print(phonenum.group(0))
			phonenums.append(phonenum)

		for str in phonenums:
			redaction_object = {}
			redaction_object['str'] = str
			redaction_object['tag_id'] = tag_map['Phone numbers']
			redaction_object['page'] = page_num
			redaction_list.append(redaction_object)
		print(phonenums)

	if('Social security number' in tag_map):
		print("SSN: ")

		t_ssns = SSN_extract(txt)
		SSNs = []
		for ssn in t_ssns:
			if ssn in words or (ssn + ",") in words or (ssn + ".") in words or (ssn + ":") in words:
				SSNs.append(ssn)
		for str in SSNs:
			redaction_object = {}
			redaction_object['str'] = str
			redaction_object['tag_id'] = tag_map['Social security number']
			redaction_object['page'] = page_num
			redaction_list.append(redaction_object)
		print(SSNs)


	# print("BAN: ")

	# bans = BAN_extract(txt)
	# for ban in bans:
	# 	print(ban)
	
	if('Passport' in tag_map):
		print("Passport: ")

		t_passports = passport_extract(txt)
		passports = []
		for pp in t_passports:
			if pp in words or (pp + ",") in words or (pp + ".") in words or (pp + ":") in words:
				passports.append(pp)

		for str in passports:
			redaction_object = {}
			redaction_object['str'] = str
			redaction_object['tag_id'] = tag_map['Passport']
			redaction_object['page'] = page_num
			redaction_list.append(redaction_object)
		print(passports)				


	if('Driver license numbers' in tag_map):		
		print("Driver License Number: ")

		t_dlns = DLN_extract(txt)
		dlns = []
		for dln in t_dlns:
			if dln in words or (dln + ",") in words or (dln + ".") in words or (dln + ":") in words:
				dlns.append(dln)

		for str in dlns:
			redaction_object = {}
			redaction_object['str'] = str
			redaction_object['tag_id'] = tag_map['Driver license numbers']
			redaction_object['page'] = page_num
			redaction_list.append(redaction_object)
		print(passports)				


	if('Time of day' in tag_map):
		print("Time of Day: ")

		t_tods = time_extract(txt)
		tods = []
		for tod in t_tods:
			if tod in words or (tod + ",") in words or (tod + ".") in words or (tod + ":") in words:
				tods.append(tod)

		for str in tods:
			redaction_object = {}
			redaction_object['str'] = str
			redaction_object['tag_id'] = tag_map['Time of day']
			redaction_object['page'] = page_num
			redaction_list.append(redaction_object)
		print(passports)

	if('Prison name' in tag_map):		
		print("List of Federal Prison: ")
		t_fpls = FPL_extract(txt)
		fpls = []
		for fpl in t_fpls:
			if fpl in words or (fpl + ",") in words or (fpl + ".") in words or (fpl + ":") in words:
				fpls.append(fpl)

		for str in fpls:
			redaction_object = {}
			redaction_object['str'] = str
			redaction_object['tag_id'] = tag_map['Prison name']
			redaction_object['page'] = page_num
			redaction_list.append(redaction_object)
		print(passports)


	if('Jail name' in tag_map):		
		print("List of State Prison: ")
		t_spls = SPL_extract(txt)
		spls = []
		for spl in t_spls:
			if spl in words or (spl + ",") in words or (spl + ".") in words or (spl + ":") in words:
				spls.append(spl)

		for str in spls:
			redaction_object = {}
			redaction_object['str'] = str
			redaction_object['tag_id'] = tag_map['Jail name']
			redaction_object['page'] = page_num
			redaction_list.append(redaction_object)
		print(passports)


	if('FBI Number' in tag_map):
		print("FBI Number: ")

		t_fbi_nums = FPN_extract(txt)
		fbi_nums = []

		for fbi_num in t_fbi_nums:
			if fbi_num in words or (fbi_num + ",") in words or (fbi_num + ".") in words or (fbi_num + ":") in words:
				fbi_nums.append(fbi_num)

		for str in fbi_nums:
			redaction_object = {}
			redaction_object['str'] = str
			redaction_object['tag_id'] = tag_map['FBI Number']
			redaction_object['page'] = page_num
			redaction_list.append(redaction_object)
		print(fbi_nums)

	return txt, redaction_list

# if __name__ == '__main__':
# 	img_path = "images/a-0.png"
# 	extract_items(img_path)


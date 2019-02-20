import nltk
from nltk.tag.stanford import StanfordNERTagger
import os
import datefinder
from optparse import OptionParser
import os.path
import re
import pyap
from date_extractor import extract_dates
import pandas as pd
from django.conf import settings
import xlrd

# function extracting name from the text using StanfordNERTagger(NER - Named Entity Recognition)
def name_extract(text):	
	java_path = "C:/Program Files/Java/jdk1.8.0_151/bin/java.exe"
	os.environ['JAVAHOME'] = java_path
	print(nltk.__version__)

	jar = os.path.join(settings.STATIC_ROOT, '../engine/stanford-ner/stanford-ner-3.9.2.jar')
	model = os.path.join(settings.STATIC_ROOT, '../engine/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz')

	st = StanfordNERTagger(model, jar)

	name_list = []
	
	for sent in nltk.sent_tokenize(text):
		tokens = nltk.tokenize.word_tokenize(sent)
		tags = st.tag(tokens)		
		for tag in tags:
			if tag[1] == 'PERSON':
				# print(tag[0])
				name_list.append(tag[0])
	return name_list

# function extracting the date from the text
def date_extract(text):	

	# matches = datefinder.find_dates(text)
	# matches = dparser.parse(text, fuzzy=True)
	dates = extract_dates(text, return_precision=True)

	return dates

# function extracting the email from the text
def email_extract(text):

	regex = re.compile(("([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
                    "{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
                    "\sdot\s)*)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"))

	# Returns an iterator of matched emails found in string s
	# Removing lines that start with '//' because the regular expression
	# mistakenly mathces patterns like 'http://foo@bar.com' as '//foo@bar.com'
	matches = []

	for email in re.findall(regex, text.lower()):
		if not email[0].startswith('//'):
			matches.append(email[0])


	# return (email[0] for email in re.findall(regex, text.lower()) if not email[0].startswith('//'))
	return matches

# function extracting address from the text
def address_extract(text):
	addresses = pyap.parse(text, country='US')

	# for address in addresses:
	# 	print(address)
	# 	print(address.as_dict())

	return addresses

# function extracting phonenum from the text
def phonenum_extract(text):
	# regExp = re.compile(("\(?\b[2-9][0-9]{2}\)?[-. ]?[2-9][0-9]{2}[. ]?[0-9]{4}\b"))
	# regExp = re.compile("\+?\d{0,3}\D{0,2}\d{3}\D{0,2}\d{3}\D\d{4}")
	regExp = re.compile("\+?(1\s?)?((\([0-9]{3}\))|[0-9]{3})[\s\-]?[0-9]{3}[\s\-]?[0-9]{4}")

	# regExp = re.compile(("\D?(\d{0,3}?)\D{0,2}(\d{3})?\D{0,2}(\d{3})\D?(\d{4})$"))

	# text1 = "gfdhg (503) 985 7823 fdjasklfjskdla fdsa (234) 456 6789 sadasda (123) 345 7823"
	# text1 = "(503) 985 7823, (234)-435-1234"
	matches = []

	for rlt in re.finditer(regExp, text):
		matches.append(rlt.group(0))
		# print(rlt)
	
	return matches

def SSN_extract(text):
	regExp = re.compile("\d{3}[-]\d{2}[-]\d{4}")

	matches = []

	for rlt in re.finditer(regExp, text):
		matches.append(rlt.group(0))

	return matches

def BAN_extract(text):
	regExp = re.compile("\d{4}[\s]?\d{4}[\s]?\d*[\s]?\d*[\s]?\d*")

	matches = []

	for rlt in re.finditer(regExp, text):
		matches.append(rlt.group(0))

	return matches

def passport_extract(text):
	regExp = re.compile("[a-zA-Z0-9]{2}\d{4,7}")

	matches = []

	for rlt in re.finditer(regExp, text):
		matches.append(rlt.group(0))

	return matches

def DLN_extract(text):
	regExp = re.compile("[a-zA-Z]{0,2}\d{1,3}[a-zA-Z]{0,3}\d{1,17}[a-zA-Z]{0,1}")

	matches = []

	for rlt in re.finditer(regExp, text):
		matches.append(rlt.group(0))

	return matches

def time_extract(text):
	regExp = re.compile("\d{1,2}[:]\d{1,2}([:]\d{1,2})?[\s]?([AaPp][Mm])?")

	matches = []

	for rlt in re.finditer(regExp, text):
		matches.append(rlt.group(0))

	return matches

def FPN_extract(text):
	regExp = re.compile("\d{5}[-][0]\d{2}")

	matches = []

	for rlt in re.finditer(regExp, text):
		matches.append(rlt.group(0))

	return matches

def get_data_from_xlsx(file, sheet_name, col_name):
	df = pd.read_excel(file, sheet_name)

	df_str = ""
	for ele in df[col_name][1:]:
		if str(ele) != "nan":
			df_str = df_str + str(ele) + ";"

	tmp_list = df_str.split(";")
	list_size = len(tmp_list)

	for i in range(list_size):
		tmp_list[i] = tmp_list[i].strip()

	res = []
	for ele in tmp_list:
		if ele != "":
			res.append(ele)

	return res


def canFind(text, item_data):

	word_list = re.split(' ', text)
	item_list = re.split(' ', item_data)

	wl_cnt = len(word_list)
	il_cnt = len(item_list)

	res_list = []

	for i in range(wl_cnt - il_cnt + 1):
		isOK = True
		for j in range(il_cnt):
			if nltk.edit_distance(word_list[i+j].lower(), item_list[j].lower()) > 1:
				isOK = False
				break

		if isOK == True:
			res = word_list[i]
			for j in range(il_cnt - 1):
				res = res + " " + word_list[i + 1 + j]

			res_list.append(res)


	return res_list


def FPL_extract(text):
	matches = []

	try:
		file = os.path.join(settings.STATIC_ROOT, '../engine/Redaction Patterns.xlsx')
		xl = pd.ExcelFile(file)
		sheet_name_list = xl.sheet_names

		fpl_list = get_data_from_xlsx(file, sheet_name_list[2], "Unnamed: 1")

		fpl_cnt = len(fpl_list)

		for i in range(fpl_cnt):
			tmp_match = canFind(text, fpl_list[i])
			for j in range(len(tmp_match)):
				matches.append(tmp_match[j])
		
	except:
		print(file + " not found")

	return matches


def SPL_extract(text):
	matches = []

	try:		
		file = os.path.join(settings.STATIC_ROOT, '../engine/Redaction Patterns.xlsx')
		xl = pd.ExcelFile(file)
		sheet_name_list = xl.sheet_names

		spl_list = get_data_from_xlsx(file, sheet_name_list[4], "Unnamed: 1")
		spl_cnt = len(spl_list)

		for i in range(spl_cnt):
			tmp_match = canFind(text, spl_list[i])
			for j in range(len(tmp_match)):
				matches.append(tmp_match[j])

	except:
		print(file + " not found")

	return matches

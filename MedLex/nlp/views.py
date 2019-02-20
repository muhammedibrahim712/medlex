from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from os import listdir
from os.path import join, isfile
from django.conf import settings
from nlp.models import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core import serializers
import json
from .engine.pdf2image import *
from .engine.extract_items import *

# Create your views here.


def home(request):
	# return HttpResponse('<h1>Blog Home</h1>')

	pdffiles = []

	file_path = os.path.join(settings.STATIC_ROOT, 'pdf')

	for f in listdir(file_path):
		if isfile(join(file_path, f)):
			if f.endswith(".pdf"):
				pdffiles.append(f)

	# print(pdffiles)
	# search_str = "inv"

	# for f in pdffiles:
	# 	if search_str.lower() in f.lower():
	# 		print(f)
	return render(request, 'home.html', {'pdf_list': pdffiles})


def medlex_settings(request):
	return render(request, 'setting.html')


def medlex_redaction(request):
	tag_list = Tag.objects.values_list('name', flat=True)
	for e in Setting.objects.filter(setting_key='page_count'):
		page_count = e.setting_value
		break
	return render(request, 'redaction.html', {'tag_list': tag_list, 'page_count': page_count})


@csrf_exempt
def save_tag_list(request):
	result = {
		"type": "failed",
		"message": ""
	}
	if request.method == "POST":
		tag_string = request.POST['tagString']
		tag_array = json.loads(tag_string)
		Tag.objects.all().delete()
		for tag_name in tag_array:
			tag_object = Tag(name=tag_name)
			tag_object.save()

		extract_result = extract_items_from_images()
		if extract_result == True:
			result = {
				"type": "success",
				"message": ""
			}
		else:
			result = {
				"type": "failed",
				"message": "Extraction Failed"
			}
	return JsonResponse(result)


def remove_duplicates(input_list):
	output_list = []
	for value_object in input_list:
		if value_object in output_list:
			continue
		output_list.append(value_object)
	return output_list


def extract_items_from_images():
	image_list = Doc.objects.values_list('name', flat=True)
	tag_set = Tag.objects.all()
	tag_map = {}
	redaction_list = []
	sentence_list = []

	year_limit_set = Setting.objects.filter(setting_key='year_limit')
	year_limit = -1
	for tmp in year_limit_set:
		year_limit = tmp.setting_value
		break

	for tag in tag_set:
		tag_map[str(tag.name)] = tag.id

	for image_name in image_list:
		image_origin_name, image_extension = image_name.split('.')
		prefix, page_num = image_origin_name.split('-')
		content, redaction_list_temp = extract_items(image_name, tag_map, page_num, year_limit)

		redaction_list = redaction_list + redaction_list_temp

		sentence_object = {}
		sentence_object['sentence'] = content
		sentence_object['page'] = page_num
		sentence_list.append(sentence_object)

	Sentence.objects.all().delete()
	for sentence_object in sentence_list:
		Sentence(sentence=sentence_object['sentence'], page=sentence_object['page']).save()
	Setting.objects.filter(setting_key='page_count').update(setting_value=len(sentence_list))

	redaction_list = remove_duplicates(redaction_list)

	Redaction.objects.all().delete()
	for redaction_object in redaction_list:
		Redaction(str=redaction_object['str'], tag_id=redaction_object['tag_id'], page=redaction_object['page']).save()
	return True

@csrf_exempt
def save_year_limit(request):
	result = {
		"type": "failed",
		"message": ""
	}
	if request.method == "POST":
		year_limit = request.POST['yearLimit']
		Setting.objects.filter(setting_key='year_limit').update(setting_value=year_limit)
		result = {
			"type": "success",
			"message": ""
		}
	return JsonResponse(result)


@csrf_exempt
def save_pdf_list(request):
	result = {
		"type": "failed",
		"message": ""
	}
	if request.method == "POST":
		pdf_string = request.POST['pdfNameString']
		pdf_array = json.loads(pdf_string)

		for pdf_name in pdf_array:
			selected_pdf_name = pdf_name
			break
		
		image_name_array = pdf2image(selected_pdf_name)

		Doc.objects.all().delete()
		for image_name in image_name_array:
			doc_object = Doc(name=image_name)
			doc_object.save()

		result = {
			"type": "success",
			"message": ""
		}	
	return JsonResponse(result)


@csrf_exempt
def get_sentence_list(request):

	sentence_list = []
	if request.method == "POST":
		page_num = request.POST['page']
		sentence_set = Sentence.objects.filter(page=page_num)
		for sentence_object in sentence_set:
			sentence_list.append(sentence_object.sentence)
		# sentence_list = ["Vasiliy is an architect, mvulti-platform developer, hobbyist UI designer, and entrepreneur. He's an all-in-one performer and perfectionist in a great way. With more than sixteen years of experience in web programming and managing development teams, he\'s excited about the way the web is evolving and likes to be on the bleeding edge of modern technology."]
	result = {
		'sentence_list': sentence_list
	}
	return JsonResponse(result)


@csrf_exempt
def get_redaction_list_page(request):
	result = []
	redaction_list = []
	tag_list = []
	if request.method == "POST":
		page_num = request.POST['page']
		redaction_list = Redaction.objects.filter(page=page_num).all()
		tag_list = Tag.objects.all()
	redaction_list_json = serializers.serialize('json', redaction_list)
	tag_list_json = serializers.serialize('json', tag_list)
	result = {
		'redaction_list_json': redaction_list_json,
		'tag_list_json': tag_list_json
	}
	return JsonResponse(result)


@csrf_exempt
def get_redaction_list_report(request):
	result = []
	redaction_list = []
	tag_list = []
	if request.method == "POST":
		redaction_list = Redaction.objects.all().order_by('page')
		tag_list = Tag.objects.all()
	redaction_list_json = serializers.serialize('json', redaction_list)
	tag_list_json = serializers.serialize('json', tag_list)
	result = {
		'redaction_list_json': redaction_list_json,
		'tag_list_json': tag_list_json
	}
	return JsonResponse(result)


@csrf_exempt
def get_redaction_list(request):
	result = []
	redaction_list = []
	tag_list = []
	if request.method == "POST":
		redaction_list = Redaction.objects.all().order_by('page')
		tag_list = Tag.objects.all()
	redaction_list_json = serializers.serialize('json', redaction_list)
	tag_list_json = serializers.serialize('json', tag_list)
	result = {
		'redaction_list_json': redaction_list_json,
		'tag_list_json': tag_list_json
	}
	return JsonResponse(result)


@csrf_exempt
def accept_redaction(request):
	result = {
		"type": "failed",
		"message": ""
	}

	if request.method == "POST":
		redaction_id = request.POST['redactionId']
		Redaction.objects.filter(id=redaction_id).update(state=1)
		result = {
			"type": "success",
			"message": ""
		}
	return JsonResponse(result)


@csrf_exempt
def accept_all_redaction(request):
	result = {
		"type": "failed",
		"message": ""
	}

	if request.method == "POST":
		page = request.POST['page']
		Redaction.objects.filter(page=page).update(state=1)
		result = {
			"type": "success",
			"message": ""
		}
	return JsonResponse(result)


@csrf_exempt
def remove_redaction(request):
	result = {
		"type": "failed",
		"message": ""
	}
	if request.method == "POST":
		redaction_id = request.POST['redactionId']
		Redaction.objects.filter(id=redaction_id).delete()
		result = {
			"type": "success",
			"message": ""
		}
	return JsonResponse(result)

@csrf_exempt
def remove_all_redaction(request):
	result = {
		"type": "failed",
		"message": ""
	}
	if request.method == "POST":
		page = request.POST['page']
		Redaction.objects.filter(page=page).delete()
		result = {
			"type": "success",
			"message": ""
		}
	return JsonResponse(result)


@csrf_exempt
def add_redaction(request):
	result = {
		"type": "failed",
		"message": ""
	}
	if request.method == "POST":
		redaction_str = request.POST['str']
		tag_name = request.POST['tagName']
		page = request.POST['page']
		tag_set = Tag.objects.filter(name=tag_name)
		for t in tag_set:
			tag = t
			break
		redaction_object = Redaction(str=redaction_str, tag=tag, page=page, state=0)
		redaction_object.save()
		result = {
			"type": "success",
			"message": ""
		}
	return JsonResponse(result)


@csrf_exempt
def add_tag(request):
	result = {
		"type": "failed",
		"message": ""
	}
	if request.method == "POST":
		tag_name = request.POST['tagName']
		tag_object = Tag(name=tag_name).save()
		result = {
			"type": "success",
			"message": ""
		}
	return JsonResponse(result)


@csrf_exempt
def change_redaction_tag(request):
	result = {
		"type": "failed",
		"message": ""
	}
	if request.method == "POST":
		tag_name_new = request.POST['tagNameNew']
		redaction_id = request.POST['redactionId']

		tag_set = Tag.objects.filter(name=tag_name_new)
		for t in tag_set:
			tag_new = t
			break
		Redaction.objects.filter(id=redaction_id).update(tag=tag_new)
		result = {
			"type": "success",
			"message": ""
		}
	return JsonResponse(result)


@csrf_exempt
def change_redaction_str(request):
	result = {
		"type": "failed",
		"message": ""
	}
	if request.method == "POST":
		str = request.POST['str']
		id = request.POST['id']
		Redaction.objects.filter(id=id).update(str=str)
		result = {
			"type": "success",
			"message": ""
		}
	return JsonResponse(result)


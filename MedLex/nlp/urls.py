from django.urls import path
from . import views


urlpatterns = [
	path('', views.home, name='home'),
	path('settings/', views.medlex_settings, name='settings'),
	path('redaction/', views.medlex_redaction, name='redaction'),
	path('savePdfList', views.save_pdf_list, name=''),
	path('settings/saveTagList', views.save_tag_list, name=''),
	path('settings/saveYearLimit', views.save_year_limit, name=''),
	path('redaction/getSentenceList', views.get_sentence_list, name=''),
	path('redaction/getRedactionInfo', views.get_redaction_list_page, name=''),
	path('redaction/getRedactionInfoForReport', views.get_redaction_list_report, name=''),
	path('redaction/acceptRedactionById', views.accept_redaction, name=''),
	path('redaction/acceptAllRedaction', views.accept_all_redaction, name=''),
	path('redaction/removeAllRedaction', views.remove_all_redaction, name=''),
	path('redaction/removeRedactionById', views.remove_redaction, name=''),
	path('redaction/addRedaction', views.add_redaction, name=''),
	path('redaction/addTag', views.add_tag, name=''),
	path('redaction/changeRedactionTag', views.change_redaction_tag, name=''),
	path('redaction/changeRedactionStr', views.change_redaction_str, name=''),

]
# -*- coding: utf-8 -*-
import urllib.request, re, os, csv, shutil
from urllib.request import urlopen
import requests  
import lxml
from lxml import html, etree
import lxml.etree as ET
import xml.etree.ElementTree as ETO
from lxml.html import fromstring, parse
from w3lib.html import remove_tags
from datetime import datetime, date, time
import urllib.parse 
import urllib, webbrowser
import csv, imp
import logging, sys
import pymystem3
from pymystem3 import Mystem
import textwrap, time, glob

'''

Author: Hazova N. 
[Gusina Text Analyser]

'''

'''
Для создания нового CSV файла, содержащего все ссылки, необходимо
Запустить PySpider, создать задание с именем test
'''

'''
url = 'http://0.0.0.0:5000/'
webbrowser.open(url)


destination = 'test.csv'
url = 'http://0.0.0.0:5000/results/dump/test.csv'
urllib.request.urlretrieve(url, destination)
'''




'''
Можно было использовать xpath, но мы не ищем легких путей
Посему в дальнейшем достаточное количество не самых логичных и очевидных, но работающих методов
'''


'''
Глобальный путь; является рабочей директорией скрипта
'''



def create_folder(path, year="", month="", typeof="html"):
	'''
	Создание директории при отсутствии заданной
	(string) path -- рабочая директория
	(int)	year -- год статьи
	(string) month -- месяц статьи
	(string) typeof -- тип файла статьи
						html
						xmlFile
						plain
	'''
	os.chdir(path)
	if os.path.exists(path+typeof) == False:
		os.makedirs(typeof)
	if os.path.exists(path+typeof+"/"+year+"/") == False:
		os.chdir(path+typeof)
		os.makedirs(str(year))
	if os.path.exists(path+typeof+"/"+year+"/"+month) == False:
		os.chdir(path+'/'+typeof+"/"+year)
		os.makedirs(str(month))


def monthdic(month):
	'''
	Заменяет во входных данных строку месяца на числовой эквивалент
	(string) month -- входной месяц
	'''
	month_dictionary = {
		"январь": "01",
		"февраль": "02",
		"март": "03",
		"апрель": "04",
		"май": "05",
		"июнь": "06",
		"июль": "07",
		"август": "08",
		"сентябрь": "09",
		"октябрь": "10",
		"ноябрь": "11",
		"декабрь": "12",
	}
	for i, j in month_dictionary.items():
		month = month.replace(i, j)
	return month

def transpose_month(month, type="base"):
	'''
	Перевод месяца в изначальную форму слова
	При необходимости можно вызывать для превращения месяца в числовой эквивалент
	(string) month -- месяц на входе
	(string) type -- входящая переменная для определения необходимости перевода в числовой эквивалент
				ext -- если нужно перевести
				base -- только изменить форму
	'''
	month = re.sub("(сентябр|октябр|ноябр|декабр|январ|феврал|апрел|июн|июл)(я)", r"\1ь", month)
	month = re.sub("(март|август)(а)", r"\1", month)
	month = re.sub("(ма)(я)", r"\1й", month)
	if type == "ext":
		month = monthdic(month)
	return month


def provide_clean_file(input_file, output_file, info=[], type="mystem"):
	'''
	Производит окончательную очистку и создает ИНФО
	(string) input_file -- путь входного файла для очистки
	(string) output_file -- путь выходного файла
	(list)	info -- список ИНФО
	(string) type -- тип очистки
					extra - очичает и добавляет ИНФО в начало файла
					mystem - очищает до состояния ЧИСТОЙ статьи
	'''
	with open(input_file) as file:
		text = file.read()
		text = extra_cleaning(text)
		if type =="extra":
			info[3] = find_topic(text)
			#print(info[3])
			info = write_info(info)
       # print(extra_cleaning(text))
		with open(output_file, 'w') as file:
			if type == "extra":
				file.write('\n'.join(info))
			file.write(text)


def find_topic(text):
	'''
	Поиск топика статьи по заданному regex в тексте
	(string) text - входной текст
	'''
	topic = re.search("(?:\n)([А-Я]{3,20}\s{1})(?=[А-Я]{1})", text)
	if topic != None:
		#print(topic.group(0))
		return topic.group(1)
	else:
		return "None"

def extra_cleaning(text):
	'''
	Очистка от мусора по заданным regex
	(string) text - входной текст
	'''
	pattern = re.compile("(ПОПУЛЯРНЫЕ МАТЕРИАЛЫ).+", re.DOTALL)
	pattern_new = re.compile("(ПОЛИТИКА).+(О газете)", re.DOTALL)
	#pattern_desa = re.compile("\.(БРЯНСК.RU).+\xBB\s\n{1}", re.DOTALL)
	#pattern_totheend = re.compile("\n([А-Я :]+)\n[а-я]{1}(.+)", re.DOTALL)
	pattern_iknowaboutxpath = re.compile("\.(БРЯНСК.RU)(.+)", re.DOTALL)
	text = re.sub("Ещё →", " ", text)
	text = re.sub(r"\|", "", text)
	text = re.sub("Комментарии:\s\d", " ", text)
	text = re.sub("Версия для печати Подписаться на новости На главную", "", text)
	text = re.sub("(|)?\s?(Версия для печати)\s?", "", text)
	text = re.sub("\D{1}(?=(\d{1,2}-\d{1,2}-\d{4}),(\s\d{2}:\d{2}))", "\n  ", text)
	text = re.sub(".{1}(?=(сегодня|вчера), \d{2}:\d{2})", "\n", text)
	text = re.sub(".{1}(?=В РОССИИ И МИРЕ: ПОСЛЕДНИЕ НОВОСТИ)", "\n\n", text)
	text = re.sub("([а-я]{1})(?=\d{1,2}\s)", r"\1 ", text)
	text = re.sub("([а-я]|\d){1}(?=[А-Я])", r"\1. ", text)
	text = re.sub("([А-Я]){1}(?=[А-Я]{1}\s?[а-я]{1,}\s)", r"\1 ", text)
	text = re.sub("Р\sФ", "РФ", text)
	text = re.sub("ЦФ\sО", "ЦФО", text)	
	text = re.sub("СШ\sА", "США", text)
	text = re.sub("МИ\sД", "МИД", text)
	text = re.sub(pattern, " ", text)
	text = re.sub(pattern_new, " ", text)
	text = re.sub(pattern_iknowaboutxpath, '', text)
	#text = re.sub(pattern_desa, ".", text)
	#text = re.sub(pattern_totheend, "", text)
	return text

def gusina():
	print(textwrap.dedent(
		"""
	                                                                                        
	                                                                                        
	                                                                                        
	                                              '                                         
	                                               #                                        
	                                         `+:,` ,+                                       
	                                            `:.:`;                                      
	                                         :+''#``,:`                                     
	                                       .;'.:``.``.``#.                                  
	                                      #  #```````.'.``#                                 
	                                       .,`````````.````+.                               
	                                      ,.```````````;`````;                              
	                                      :```````````````````:                             
	                                     @`````````````.+;;````.                            
	                                    ``````````````@   `````,                            
	                                    #````````````,`   ;`````+                           
	                                    :```````````,@      ```+:' `                        
	                                    ``````````` :+`    ;``;,,.:                         
	                                   :````````    .@#:   ,``#:',;'       ``               
	                                   #```````     ##@;. ````';;:.`;;   ,:`:`              
	                                   #``````     `+'#@..+```:;;;;..`'@,`.,,;              
	                                   '``````          .:`  ;;;;;;;+,...,:::`              
	                                  +:``````            `  #;;;;;;;;::::::'`              
	                                `+@,`````             .``;;;;'';;:;::::+                
	                                  ..;.```             : ';;;;;;:;;;;:':                 
	                                `.+;``,``             .+;;;;;;;;::'#'                   
	                                 #`+`:,.``             .:;'#+'+,`                       
	                                   ;+@`;```           .`+;;;:#:: `                      
	                                   ; ; ```            . ::;;:::+:                       
	                                   :  :```               @'+++;:;'                      
	                                   `  ##,`         ` `:+.       ;+#                     
	                                       .`.;`      . #`             #                    
	                                       `'````     :@`                                   
	                                        .````     `'                                    
	                                         ;````     @                                    
	                                         :`````    +    


	                                 <<< Гусина отправляется в долгий путь >>>                                

	"""
	))



def make_it_clean(line):
	'''
	Очистка текста от тегов html, css стилей, js
	(string) line - входной текст
	'''
	cleari = remove_tags(line)
	soline = re.compile("(\<.+\n)", re.DOTALL)
	boline = re.compile("(.+\>)", re.DOTALL)
	alline = re.compile("\<.+\>", re.DOTALL)
	cleari = re.sub(soline, '', cleari)
	cleari = re.sub(boline, '', cleari)
	cssline = re.compile(r"\{.+\}{1}", re.DOTALL)
	cleari = re.sub(cssline, ' ', cleari)
	cleari = re.sub("async=\"async\"\n", '', cleari)
	cleari = re.sub("src=.+\"", '', cleari)
	cleari = re.sub("var\s_.+\)", '', cleari)
	cleari = re.sub("function.+\"\)", '', cleari)
	cleari = re.sub("document.+\);", " ", cleari)
	cleari = re.sub("function.+\)", " ", cleari)
	cleari = re.sub("&laquo;", " «", cleari)
	cleari = re.sub("&raquo;", "» ", cleari)
	cleari = re.sub("&rarr;", "→", cleari)
	cleari = re.sub(r'&nbsp;', ' ', cleari)
	cleari = re.sub(r'(&mdash;)|(&ndash;)', '-', cleari)
	cleari = re.sub(r'\t{2,}', ' ', cleari)
	cleari = re.sub(r'\s{2,}', ' ', cleari)
	cleari = re.sub(r'\n{2,}', '\n', cleari)
	cleari = re.sub(r"(\<\!\-\-.*\-\-\>)", '', cleari)

	return cleari


def amixml(file):
	'''
	Генерация данных для XML
	(file) file - источник для генерации
	'''
	array = []
	body_re = re.compile(r"<div class=\"sgray\"></div></div>(.+)\.<p align", re.DOTALL)
	header_re = re.compile(r"<h1>(.+)</h1>", re.DOTALL)	
	date_re = re.compile(r"<div class=\"sgray\">(.+)&ndash; БРЯНСК\.RU &nbsp; \| &nbsp;", re.DOTALL)


	array.append(searchnclean(body_re, file))
	array.append(searchnclean(header_re, file))
	array.append(searchnclean(date_re, file))

	return array

def write_info(info=[]):
	'''
	Создание массива ИНФО
	(list) info - входной лист для преобразования
	'''
	result = ["@au " + str(info[0]), "@ti "+ str(info[1]), "@da " + str(info[2]), "@topic " + str(info[3]), "@url " + str(info[4]) + "\n\n"]
	return result



def searchnclean(thing, file):
	'''
	Подготовка для массива XML
	(string(regex)) thing -- входной regex
	(file) file - входной файл для поиска
	'''
	things = re.findall(thing, file)
	things = ''.join(things)
	things = make_it_clean(things)
	return things

def toddmmyyy(date):
	'''
	Перевод строки с датой в формат DD.MM.YYY
	(string) date -- строка с датой входящая
	'''
	date = re.sub("(\d{,2})(\s)(.+)(\s)(\d{4})", r"\1.\3.\5", date)
	date = transpose_month(date,"ext")
	return date


def poehali(csv_input):
	'''
	Основная функция
	csv_input -- файл с таблицей ссылок
	На выходе
	|-xmlFile/
	|---------year/
	|--------------month/
	=========
	|-plain/
	|-------year/
	|------------month/
	=========
	|-html/
	|------year/
	|-----------month/
	|csv_file.csv

	'''
	data = []
	i = 0
	m = Mystem()
	gusina()
	col = ["path", "author", "sex", "birthday", "header", "created", "sphere", "genre_fi", "type", "topic", "chronotop", "style", "audience_age", "audience_level", "audience_size", "source", "publication", "publisher", "publ_year", "medium", "country", "region", "language"]
	time.sleep(3)

	path = os.getcwd()
	path = path + "/"
	csv_file = open(path + "csv_file.csv", "w")
	writer = csv.writer(csv_file,delimiter = ",")
	writer.writerow(col)


	dosugvbryanske = re.compile("^(http://www.briansk.ru/)(.+)")

	with open(csv_input) as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if re.search(dosugvbryanske, row['url']):
				print('passing on ' + str(i))

				test = urllib.request.urlopen(row['url']).read().decode('cp1251')
				file_html = path+"/"+str(i)+".html"
				file_html1 = path+"/"+str(i-1)+".html"
				dest_html = str(i)+".html"
				plain = str(i)+".txt"
				plain_new = str(i)+"_plained.txt"
				plain_stem = str(i)+"_mystem.txt"
				output_plain_stem = str(i)+"_out_mystem.txt"
				xmlFile = str(i) + ".xml"
				#dir_for_stem = "XML_STEM"

				page1_html = open(file_html, 'w')
				page1_html.write(str(test))
				page1_html.close()
				print("FILE EX: "+ str(os.path.exists(file_html)))
				pageMoving = open(file_html, 'r')
				#print(file_html + " PATH " + dest_html+"\n")
				if os.path.exists(file_html1):
					os.remove(file_html1)
					print("FILE "+str(i-1)+" HB REMOVED")
				else:
					print("FILE "+str(i-1)+" HB ALREADY MOVED")
				for line in pageMoving:
					data = re.search(r"\">[0-9]{1,2}\s{1}((янв|февр|март|апре|май|июнь|июль|авг|сентя|октяб|нояб|декаб)[а-я]{1,}\s[0-9]{4})|\">[0-9]{1,2}\s{1}(ма(а|я)\s[0-9]{4})", line)
					if data:

						'''
						Определение датирования статьи
						'''
						dates = data.group()
						dates2 = dates.split()
						year = dates2[2]
						month = dates2[1]

						create_folder(path, year, transpose_month(month), "html")
						shutil.move(file_html, path+"html/"+year+"/"+transpose_month(month)+"/"+dest_html)
						print("FILE "+str(i)+" HB MOVED")


						'''
						Созидание директории для XML
						'''
						create_folder(path, year, transpose_month(month), "xmlFile")

						forxml = path+"xmlFile/"+year+"/"+transpose_month(month)+"/"+dest_html
						forxml_dir = path+"xmlFile/"+year+"/"+transpose_month(month)+"/"
						xml_stem = forxml_dir + str(i) + "_mystem.xml"
						rofxml = path+"xmlFile/"+year+"/"+transpose_month(month)+"/"+xmlFile

						'''
						Копирование html -> xmldir для дальнейшей обработки
						'''

						shutil.copy(path+"html/"+year+"/"+transpose_month(month)+"/"+dest_html, forxml)
						print("FILE "+str(i)+" HB COPIED TO XML")
						openindosug_xml = open(forxml, "r")
						read_and_clean_xml = openindosug_xml.read()
						xml_data = amixml(read_and_clean_xml)
						#print(xml_data[2])
						openindosug_xml.close()
						'''
						Созидание директории для plain текста
						'''
						
						create_folder(path, year, transpose_month(month), "plain")
						forplain = path+"plain/"+year+"/"+transpose_month(month)+"/"+dest_html
						forplain_dir = path+"plain/"+year+"/"+transpose_month(month)+"/"
						shutil.copy(path+"html/"+year+"/"+transpose_month(month)+"/"+dest_html, forplain)
						print("FILE "+str(i)+" HB COPIED TO PLAIN")
						openindosug = open(forplain, "r")

						dates = re.sub("\">", "", dates)


						'''
						wri = лист для генерации ИНФО о статьи
						'''

						wri = ["briansk.ru", str(xml_data[1]), toddmmyyy(dates), "", row['url']]


						page2_txt = open(str(forplain_dir)+str(plain), 'w')
						for datline in openindosug:
							page2_txt.write(str(make_it_clean(datline)))
						
						page2_txt.close()
						print("PLAIN FOR "+str(i)+" HB CREATED")

						'''
						Окончательная очистка plain файла; оставляем только текст статьи или текст + ИНФО
						'''
						provide_clean_file(forplain_dir+str(plain),forplain_dir+str(plain_new), wri, "extra")
						provide_clean_file(forplain_dir+str(plain),forplain_dir+str(plain_stem), wri, "mystem")
						os.remove(forplain_dir+str(plain))
						os.remove(forplain)
						openindosug.close()

						'''
						xml_data[0] -- content
						xml_data[1] -- headerTag
						xml_data[2] -- content date
						'''

						'''
						Генерация XML
						'''
						pageEtree = etree.Element('html')
						doc = etree.ElementTree(pageEtree)
						infoTag = etree.SubElement(pageEtree, "body")
						dateTag = etree.SubElement(infoTag, "h1")
						dateTag.text = str(xml_data[2])
						headerTag = etree.SubElement(infoTag, "h2")
						headerTag.text = str(xml_data[1])
						mainTag = etree.SubElement(infoTag, "h3")
						contentTag = etree.SubElement(infoTag, "h4")
						contentTag.text = str(xml_data[0])
						outFile = open(str(forxml_dir)+str(i)+".xml", 'wb')
						doc.write(outFile, xml_declaration=True, encoding='utf-16') 
						outFile.close()
						print("FILE "+str(i)+" HB CODED TO XML")

						writer.writerow([str(path+"html/"+year+"/"+transpose_month(month)+"/"+dest_html) , "briansk.ru" , "" , "" , str(xml_data[1]) , toddmmyyy(dates), 'публицистика' , "" , "" , "категория" , "" , "нейтральный" , "н-возраст" , "н-уровень" , "городская" , str(row['url']) , "брянск.ru" , "" , str(year) , "газета" , "Россия" , "БРЯНСК" , "ru"])
						os.remove(forxml)


						input_plain = forplain_dir + plain_stem
						output_plain = forplain_dir + output_plain_stem


						'''
						pystem
						mystem 

						'''
						
						with open(input_plain) as file:
						    text = file.read()
						

						lemmas = m.lemmatize(text)
						with open(input_plain, 'w') as file:
							file.write(''.join(lemmas))

						os.system(r'/home/haniani/Загрузки/mystem -icd '+ input_plain + ' ' + output_plain)
						os.system(r'/home/haniani/Загрузки/mystem -icd --format xml '+ input_plain +' '+ xml_stem)
						

						print("MYSTEM'ed "+str(i))
						break

				i += 1
				print("PASSED ; NEXT: "+str(i)+"\n")
	csv_file.close()
	        
	for file in glob.glob(path+"*.html"):
		os.remove(file)








'''
Запуск
'''



poehali('test.csv')






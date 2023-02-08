import io
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
#Docx resume
import docx2txt

import re
import operator

import os
from pdfminer.high_level import extract_text

import datetime
from typing import Final

###
# input resume folder Path
input_file_path = "C:\\projects\\python\\resume_data"
#output file path and name
output_file_path_name = "C:\\temp\\output_parsed_applicants.csv"

#define keywords
job_skill_single_keywords: Final = ["Java*10", "Node.js*6", "AngularJS*4","JavaScript*4", "Maven*3", "web*2", "Agile*5"]

#may can add a relative weight on each keyword. such as scale 1 to 10

job_skill_phrase_keywords = ["REST service*4", "REST services*5", "Web Service*9", "Web Services*9", "project manager*3", "team work*5"
                             ,"computer science*8"]
#store strings which need to be removed
remove_string = [",", "\n", ".", "•"]

degree = ["bachelor", "master", "doctor"]
max_year_work_experience = 30

#parse to find years from resume, to determine how many years work experience.
# error 4 -8 years, because year of high school, college is possiblly included in a resume

#*****functions************
def get_current_year():
    today = datetime.date.today()
    current_year = today.year
    return current_year


def get_year_of_experience(text):
    text1 = "project: big data (feb 2016 – now)   environment and tools 2000 2022"
    year_match = re.findall(r"[0-9]{4}(?![0-9])", text)
    year_list = []
    year_of_work_experience = 0;
    for year in year_match:
        year = year.strip()
        #print(year)
        if int(year) > (get_current_year() - max_year_work_experience ) and int(year) <= get_current_year():
            year_list.append(year)

    if len(year_list) > 0:
        year_list.sort()
        year_of_work_experience = int(get_current_year()) - int(year_list[0])

    return year_of_work_experience

#file_name:string,year_of_experience:int,total_keyword_score:int, keyword_scores:dictionary
#file_name,year_of_experience,total_keyword_score,keywords
#Test-resume-john-smith.docx.docx,23,54,{'java': 17, 'javascript': 1, 'maven': 5, 'web': 10, 'agile': 3, 'web service': 7, 'web services': 6, 'project manager': 4, 'computer science': 1}
#may add degrees


# Read text File
def read_text_file(file_path):
    with open(file_path, 'r') as f:
        print(f.read())

def read_pdf_file(file):
    #print("\n****" + file)
    text = extract_text(file)
    #remove unwanted characters
    text = clean_resume(text)

    text = text.lower();

    return text

    # resume_pool_dictionary['total_keyword_score']
    total_keyword_score = 0;
    #    print("content: " + text)



# Create your dictionary class
class my_dictionary(dict):

    # __init__ function
    #def __init__(self):
    #    self = dict()

    # Function to add key:value
    def add(self, key, value):
        self[key] = value

    def get_key_value(self, key):
        return self[key]

    def haskey(self, key):
        if self.get(key) == None:
            return False
        else:
            return True

#remove unwanted strings
def clean_resume(text):
    for character in remove_string:
        text = text.replace(character, " ")

    return text


def get_total_keyword_score(job_keywords_dict_obj):
    total_keyword_score = 0;
    #for each_score in job_keywords_dict_obj.values():
    for each_score in job_keywords_dict_obj:
        #each_keyword
        #print("**"+each_score +" " + str(job_keywords_dict_obj[each_score]))
        total_keyword_score = total_keyword_score + \
                              job_keywords_dict_obj[each_score] * get_weight_from_keyword(each_score)
    return total_keyword_score

def get_weight_from_keyword(search_keyword):
    keyword_weight = 0
    for keyword in job_skill_single_keywords:
        #if match
        keyword_content = keyword[0: keyword.index("*")].strip().lower()
        if keyword_content == search_keyword:
            keyword_weight = int(keyword[keyword.index("*") + 1: len(keyword)].strip())
            #print ( search_keyword + " weight:"+ str(keyword[keyword.index("*") + 1: len(keyword)]))
            break

    #check phrash keyword if no keyword find in single keyword
    if keyword_weight == 0:
        for keyword in job_skill_phrase_keywords:
            #if match
            keyword_content = keyword[0: keyword.index("*")].strip().lower()
            if keyword_content == search_keyword:
                keyword_weight = int(keyword[keyword.index("*") + 1: len(keyword)].strip())
                #print ( "**phrase keyword " +search_keyword + " weight:"+ str(keyword[keyword.index("*") + 1: len(keyword)]))
                break
    return keyword_weight


def read_file_computing(text):
    words = text.split(" ")
    #dictionaries (hasmap)
    job_keywords_dict_obj = my_dictionary()
    count = 0
    for keyword in job_skill_single_keywords:
        #if match
        for resume_word in words:
            keyword_content = keyword[0: keyword.index("*")].strip().lower()
            keyword_weight = int(keyword[keyword.index("*")+1: len(keyword)].strip())
            if keyword_content == resume_word.strip():
                if job_keywords_dict_obj.haskey(keyword_content):
                    count = job_keywords_dict_obj[keyword_content]
                    job_keywords_dict_obj.add(keyword_content, count+1)
                else:
                    job_keywords_dict_obj.add(keyword_content, 1)


    computing_phrase_keywords(text, job_keywords_dict_obj)

    total_keyword_score = get_total_keyword_score(job_keywords_dict_obj)

    resume_pool_dictionary = my_dictionary()
    resume_pool_dictionary.add("file_name", file)
    resume_pool_dictionary.add("year_of_experience", get_year_of_experience(text))

    resume_pool_dictionary.add("total_keyword_score", int(total_keyword_score))

    resume_pool_dictionary.add("keywords", job_keywords_dict_obj)

    return resume_pool_dictionary

def computing_phrase_keywords(resume_text, keyword_dictionary):

    for keyword in job_skill_phrase_keywords:
        keyword_content = keyword[0: keyword.index("*")].strip().lower()

        phrase_count = len(list(re.finditer(keyword_content.lower(), resume_text)))
        #if find any, add to dictionary
        if phrase_count > 0:
            keyword_dictionary.add(keyword_content, phrase_count)

#read doc resume, convert to text
def read_word_resume(word_doc):
    resume = docx2txt.process(word_doc)
    resume = str(resume)

    text = ''.join(resume)
    #text = text.replace("\n", "")
    text = clean_resume(text)
    text = text.lower();
    if text:
        return text


def sort_by_keyword_total_score(resume_pool_dictionary):
    return resume_pool_dictionary["total_keyword_score"]

delimiter_keywords = " | "
delimiter_title_column_name = ","

def print_header_rows(resume_pool_dictionary):
    buffer_str = ""
    header_label = ""
    #header
    for record in resume_pool_dictionary:
        column_count = 0
        for key in record:
            if column_count > 0:
                buffer_str = buffer_str + delimiter_title_column_name

            column_count = column_count + 1
            buffer_str = buffer_str + key
        break
    buffer_str = buffer_str + "\n"

#get columns data
    for record in resume_pool_dictionary:
        # buffer_str = "\n" + buffer_str
        column_count = 0
        for key in record:
            if column_count > 0:
                buffer_str = buffer_str + delimiter_title_column_name
            column_count = column_count + 1
            buffer_str = buffer_str + str(record.get(key))

        buffer_str = buffer_str + "\n"

    return buffer_str


def write_to_file (resume_pool_dictionary):
    #decending sort by keyword total score
    resume_pool_dictionary.sort(reverse=True, key=sort_by_keyword_total_score)

    try:

        output_file = open(output_file_path_name, "w")
        output_file.write(print_header_rows(resume_pool_dictionary))

    except Exception as e:
        print("open file error " + str(e))

    finally:
        output_file.close()


#*****MAIN************

#define
resume_pool_dictionary = []


# Change the directory
os.chdir(input_file_path)


# iterate through all file
for file in os.listdir():
    #print("************file name:" + file)
    # Check whether file is in text format or not
    if file.endswith(".pdf"):
        file_path = f"{input_file_path}\{file}"

        # call read text file function
        #read_text_file(file_path)
        text = read_pdf_file(file)
        if len(text) >0:
            resume_pool_dictionary.append(read_file_computing(text))

    if file.endswith(".docx"):
        file_path = f"{input_file_path}\{file}"

        # call read text file function
        # read_text_file(file_path)
        text = read_word_resume(file)

        if len(text) > 0:
            resume_pool_dictionary.append(read_file_computing(text))

write_to_file(resume_pool_dictionary)

print("The output file is at " + output_file_path_name)

#*****end main*****


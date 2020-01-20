import copy
import pandas as pd
import numpy as np
from app.db import download_db
from pandas import DataFrame

from app.Course import Course
# timetablePath='ECE Time Table - Sheet5 (3).csv'
timetablePath='database.csv'
def get_data_from_dynamo(unwanted_courses):
    '''
    This function connects to dynamoDB and get all the course objects from database
    :param unwanted_courses: unwanted course code
    :return: two lists of course objects (fall and winter)
    '''
    list_fall = []
    list_winter = []

    download_data = download_db()

    for item in download_data:
        if item.code not in unwanted_courses:
            if item.semester == "F":
                list_fall.append(item)
            elif item.semester == "S":
                list_winter.append(item)

    return list_fall, list_winter


def get_data(unwanted_courses):
    '''
    This function reads the data from csv file and do permutation for different combination of the course wrt
    lecture/practice/tutorial sessions and create two lists of available choices
    :param unwanted_courses: unwanted courses
    :return: winter list and fall list
    '''

    df = pd.read_csv(filepath_or_buffer=timetablePath)

    list_fall = []
    list_winter = []

    df = df.sort_values(['code','type'])
    df.loc[len(df)]=df.loc[len(df)-1]
    # df.loc[len(df),0] = 'hello'
    # print(df.shape[1])
    unwanted_courses_index=[]
    for i in range(len(df)):
        if str(df.iloc[i]['code']) in unwanted_courses:
            unwanted_courses_index.append(i)

    df = df.drop(df.index[unwanted_courses_index])

    list_of_lec=[]
    list_of_tut=[]
    list_of_pra=[]
    curr_course_code=""
    for ind, row in enumerate(df.iterrows()):
        if row[1]['code']!=str(curr_course_code) or ind==len(df):#move to the next course
            curr_course_code=row[1]['code']
            #save
            if len(list_of_lec) >=1 :
                # print(str(row[1]['code']) + "|||" + str(row[1]['semester']))
                result_fall, result_winter = generate_all_combination(list_of_lec, list_of_tut, list_of_pra)
                list_fall+=result_fall
                list_winter+=result_winter

            #clean
            list_of_lec=[]
            list_of_tut=[]
            list_of_pra=[]
        #normal case
        dict = {}
        dict['code'] = str(row[1]['code'])
        dict['title'] = str(row[1]['title'])
        dict['semester'] = str(row[1]['semester'])
        dict['type'] = str(row[1]['type'])
        dict['session'] = str(row[1]['session'])
        dict['category'] = str(row[1]['category'])

        dict['timeslot'] = []

        #Append time slot1
        duration = int(row[1]['end_time1']) - int(row[1]['start_time1'])
        for k in range(duration):
            dict['timeslot'].append((int(row[1]['date1'])-1)*12 + (int(row[1]['start_time1'] - 9 + k)))

        # Append time slot2
        if (np.isnan(row[1]['date2'])!= True):
            duration = int(row[1]['end_time2']) - int(row[1]['start_time2'])
            for k in range(duration):
                dict['timeslot'].append((int(row[1]['date2']) - 1) * 12 + (int(row[1]['start_time2'] - 9 + k)))

        # Append time slot3
        if (np.isnan(row[1]['date3'])!= True):
            duration = int(row[1]['end_time3']) - int(row[1]['start_time3'])
            for k in range(duration):
                dict['timeslot'].append((int(row[1]['date3']) - 1) * 12 + (int(row[1]['start_time3'] - 9 + k)))


        if dict['type']=="LEC":
            list_of_lec.append(dict)
        elif dict['type']=="TUT":
            list_of_tut.append(dict)
        elif dict['type']=="PRA":
            list_of_pra.append(dict)

    return list_fall, list_winter


def get_pd_data():
    df = pd.read_csv(filepath_or_buffer='/home/yixiao/Desktop/ECE1779A3/ECE Time Table - Sheet5 (3).csv')

    df['timeslot'] = 'default value'

    for i in range(len(df)):

        list = []

        #Append time slot1
        duration = int(df.iloc[i]['end_time1']) - int(df.iloc[i]['start_time1'])
        for k in range(duration):
            list.append((int(df.iloc[i]['date1'])-1)*12 + (int(df.iloc[i]['start_time1'] - 9 + k)))

        # Append time slot2
        if (np.isnan(df.iloc[i]['date2'])!= True):
            duration = int(df.iloc[i]['end_time2']) - int(df.iloc[i]['start_time2'])
            for k in range(duration):
                list.append((int(df.iloc[i]['date2']) - 1) * 12 + (int(df.iloc[i]['start_time2'] - 9 + k)))

        # Append time slot3
        if (np.isnan(df.iloc[i]['date3'])!= True):
            duration = int(df.iloc[i]['end_time3']) - int(df.iloc[i]['start_time3'])
            for k in range(duration):
                list.append((int(df.iloc[i]['date3']) - 1) * 12 + (int(df.iloc[i]['start_time3'] - 9 + k)))

        df.at[i, 'timeslot'] = list

    return df

def generate_all_combination(list_of_lec, list_of_tut, list_of_pra):
    '''
    this function generates all the combination of a course with given lectures,
     tutorials and practices
    :param list_of_lec: list of lecture sessions
    :param list_of_tut: list of tutorial sessions
    :param list_of_pra: list of practice sessions
    :return: the list of all the combinations
    '''
    result_fall = []
    result_winter = []
    dict_sample = list_of_lec[0]

    list_of_fall_lec =[]
    list_of_fall_tut  =[]
    list_of_fall_pra =[]
    list_of_winter_lec =[]
    list_of_winter_tut =[]
    list_of_winter_pra =[]
    #Split
    for lec in list_of_lec:
        if lec['semester']=='F':
            list_of_fall_lec.append(lec)
        elif lec['semester']=='S':
            list_of_winter_lec.append(lec)

    for tut in list_of_tut:
        if tut['semester']=='F':
            list_of_fall_tut.append(tut)
        elif tut['semester']=='S':
            list_of_winter_tut.append(tut)

    for pra in list_of_pra:
        if pra['semester']=='F':
            list_of_fall_pra.append(pra)
        elif pra['semester']=='S':
            list_of_winter_pra.append(pra)
    # print(str(len(list_of_lec))+dict_sample['code'])
    #split into fall and


    #solve fall term combination

    '''
    list_of_fall_lec =[]
      =[]
    list_of_fall_pra =[]
    list_of_winter_lec =[]
    list_of_winter_tut =[]
    list_of_winter_pra =[]
    '''
    if len(list_of_fall_tut)==0:
        dict_sample_tt = copy.deepcopy(dict_sample)
        dict_sample_tt['type'] = "TUT"
        dict_sample_tt['session'] = 0
        dict_sample_tt['timeslot'] = []
        list_of_fall_tut.append(dict_sample_tt)
    if len(list_of_fall_pra)==0:
        dict_sample_pt = copy.deepcopy(dict_sample)
        dict_sample_pt['type'] = "PRA"
        dict_sample_pt['session'] = 0
        dict_sample_pt['timeslot'] = []
        list_of_fall_pra.append(dict_sample_pt)

    for i in range(len(list_of_fall_lec)):
        for j in range(len(list_of_fall_tut)):
            for k in range(len(list_of_fall_pra)):
                _dict_sample = copy.deepcopy(list_of_fall_lec[i])
                _dict_sample['type'] = str(list_of_fall_lec[i]['type']) + "-" + str(list_of_fall_lec[i]['session']) + "_" + str(list_of_fall_tut[j]['type']) + "-" + str(list_of_fall_tut[j]['session']) + "_" + str(list_of_fall_pra[k]['type']) + "-" + str(list_of_fall_pra[k]['session'])
                _dict_sample['timeslot'] = list_of_fall_lec[i]['timeslot']+list_of_fall_tut[j]['timeslot']+list_of_fall_pra[k]['timeslot']
                #eliminate case when time slot has conflict
                if len(set(_dict_sample['timeslot'])) == len(_dict_sample['timeslot']):
                    course = Course(_dict_sample['code'], _dict_sample['title'], _dict_sample['semester'], _dict_sample['type'], _dict_sample['category'], _dict_sample['timeslot'])
                    #print(course.code + course.semester)
                    if course.semester=="F":
                       # print(course)
                       result_fall.append(course)
                    else:
                        result_winter.append(course)


    #solve winter term combination

    '''
    list_of_fall_lec =[]
      =[]
    list_of_fall_pra =[]
    list_of_winter_lec =[]
    list_of_winter_tut =[]
    list_of_winter_pra =[]
    '''
    if len(list_of_winter_tut) == 0:
        dict_sample_tt = copy.deepcopy(dict_sample)
        dict_sample_tt['type'] = "TUT"
        dict_sample_tt['session'] = 0
        dict_sample_tt['timeslot'] = []
        list_of_winter_tut.append(dict_sample_tt)
    if len(list_of_winter_pra) == 0:
        dict_sample_pt = copy.deepcopy(dict_sample)
        dict_sample_pt['type'] = "PRA"
        dict_sample_pt['session'] = 0
        dict_sample_pt['timeslot'] = []
        list_of_winter_pra.append(dict_sample_pt)

    for i in range(len(list_of_winter_lec)):
        for j in range(len(list_of_winter_tut)):
            for k in range(len(list_of_winter_pra)):
                _dict_sample = copy.deepcopy(list_of_winter_lec[i])
                _dict_sample['type'] = str(list_of_winter_lec[i]['type']) + "-" + str(
                    list_of_winter_lec[i]['session']) + "_" + str(list_of_winter_tut[j]['type']) + "-" + str(
                    list_of_winter_tut[j]['session']) + "_" + str(list_of_winter_pra[k]['type']) + "-" + str(
                    list_of_winter_pra[k]['session'])
                _dict_sample['timeslot'] = list_of_winter_lec[i]['timeslot'] + list_of_winter_tut[j]['timeslot'] + \
                                           list_of_winter_pra[k]['timeslot']
                # eliminate case when time slot has conflict
                if len(set(_dict_sample['timeslot'])) == len(_dict_sample['timeslot']):
                    course = Course(_dict_sample['code'], _dict_sample['title'], _dict_sample['semester'],
                                    _dict_sample['type'], _dict_sample['category'], _dict_sample['timeslot'])
                    # print(course.code + course.semester)
                    if course.semester == "F":
                        # print(course)
                        result_fall.append(course)
                    else:
                        result_winter.append(course)

    return result_fall, result_winter





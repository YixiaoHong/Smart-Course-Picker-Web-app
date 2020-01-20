import time
import uuid

from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from app.DataReadHelper import *
import boto3
from app.Course import Course
from app.DetailCourse import DetailCourse
# timetablePath='ECE Time Table - Sheet5 (3).csv'
timetablePath='database.csv'

hot_course_table_name="hot_course"

expire_time_in_second=24*60*60


def update_hot_search_key_table(courses):
    '''
    This function calls whenever a user submit search,
    it will put the searched keywards to database
    :param courses: keywords courses
    :return:
    '''
    upload_hot_search_key_to_db(courses)
    expireds = check_hot_course_insertion_time()
    for i in range(len(expireds)):
        expired_course = expireds[i]
        id = expired_course['hcid']
        delete_data_by_key(id)

def upload_hot_search_key_to_db(courses):
    '''
    upload the info about the search course to the db hot_course
    :param courses: the list of the course object
    '''
    dyndb = boto3.client('dynamodb', region_name='us-east-1')


    for i in range(len(courses)):
        course = courses[i]
        print("inserting#", i)
        response = dyndb.put_item(
            TableName=hot_course_table_name,
            Item={
                'code': {'S': course.code},
                'title': {'S': course.title},
                'semester': {'S': course.semester},
                'type': {'S': course.type},
                'category': {'S': course.category},
                'hcid': {'S': str(uuid.uuid4())},  # Not really unique. But is real enough in this program. Replace it only if you have a way to get the next PK from the Bendan DynamoDb
                'insertion_time': {'N': str(int(round(time.time() * 1000)))},
            }
        )

def check_hot_course_insertion_time():
    '''
    This function downloads all the hot keys from the
    dynamoDB with insert time less than 48 hours
    :return: all the hot keys from the
    dynamoDB with insert time less than 48 hours
    '''
    dyndb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dyndb.Table(hot_course_table_name)
    response = table.scan(
        FilterExpression=Attr('insertion_time').lt(str(int(round(time.time() * 1000))-expire_time_in_second * 1000))
    )
    return response['Items']

def delete_data_by_key(key):
    '''
    This function delete data in dynamoDB by specific id
    :param key: hcid
    :return:
    '''
    dyndb = boto3.client('dynamodb', region_name='us-east-1')

    # table = dyndb.Table(hot_course_table_name)
    try:
        response = dyndb.delete_item(
            TableName=hot_course_table_name,
            Key={
                'hcid': str(key),
            },
            # ConditionExpression="info.rating <= :val",
            # ExpressionAttributeValues={
            #     ":val": decimal.Decimal(5)
            # }
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            print(e.response['Error']['Message'])
        else:
            raise
    else:
        print("DeleteItem succeeded!")

def upload_to_db():
    '''
    this function upload courses to database
    :return:
    '''

    dislike = []
    filtered_data_fall, filtered_data_winter = get_data(dislike)
    alldata = filtered_data_fall + filtered_data_winter

    for c in alldata:
        c.display()

    dyndb = boto3.client('dynamodb', region_name='us-east-1')

    for i in range(len(alldata)):
        course = alldata[i]
        pid = i
        print("inserting#",i)
        response = dyndb.put_item(
            TableName='timetable_db',
            Item={
                'code': {'S':course.code},
                'title':{'S':course.title},
                'semester': {'S':course.semester},
                'type':{'S':course.type},
                'category':{'S':course.category},
                'time_slot':{'S':str(course.time_slot)},
                'pid':{'N': str(pid)},
            }
        )
        print("response#", response)

def download_db():
    '''
    This function downloads all the courses from database
    :return:
    '''

    dynamodb_client = boto3.resource('dynamodb', region_name='us-east-1')

    my_table = dynamodb_client.Table('timetable_db')

    result_item = []

    result_data = my_table.scan()

    result_item.extend(result_data['Items'])

    #rebuild the result to list of oject(course)

    result_list = []

    for item in result_item:
        code = item["code"]
        title = item["title"]
        semester = item["semester"]
        course_type = item["type"]
        category = item["category"]
        timeslot_str = item["time_slot"]
        timeslot_str = timeslot_str[1:-1]
        mylist = timeslot_str.split(', ')
        final_list_int = []
        for slot in mylist:
            final_list_int.append(int(slot))

        course = Course(code,title,semester,course_type,category,final_list_int)
        result_list.append(course)

    return result_list

def upload_original_table():
    '''
    this function upload original table to database
    :return:
    '''
    df = pd.read_csv(filepath_or_buffer=timetablePath)
    dyndb = boto3.client('dynamodb', region_name='us-east-1')

    for i in range(len(df)):
        print("inserting#",i)
        response = dyndb.put_item(
            TableName='original_data',
            Item={
                'pid': {'N': str(i)},
                'code': {'S':str(df.iloc[i]['code'])},
                'title': {'S':str(df.iloc[i]['title'])},
                'semester': {'S':str(df.iloc[i]['semester'])},
                'type': {'S':str(df.iloc[i]['type'])},
                'session': {'S':str(df.iloc[i]['session'])},
                'category': {'S':str(df.iloc[i]['category'])},
                'date1': {'S':str(df.iloc[i]['date1'])},
                'start_time1': {'S':str(df.iloc[i]['start_time1'])},
                'end_time1': {'S':str(df.iloc[i]['end_time1'])},
                'date2': {'S':str(df.iloc[i]['date2'])},
                'start_time2': {'S':str(df.iloc[i]['start_time2'])},
                'end_time2': {'S':str(df.iloc[i]['end_time2'])},
                'date3': {'S':str(df.iloc[i]['date3'])},
                'start_time3': {'S':str(df.iloc[i]['start_time3'])},
                'end_time3': {'S':str(df.iloc[i]['end_time3'])}
            }
        )
        print("response#", response)
    return

def download_original_table():
    '''
    This function downloads the original database from database
    :return: result list
    '''

    dynamodb_client = boto3.resource('dynamodb', region_name='us-east-1')

    my_table = dynamodb_client.Table('original_data')

    result_item = []

    result_data = my_table.scan()

    result_item.extend(result_data['Items'])

    #rebuild the result to list of oject(course)

    result_list = []

    for item in result_item:


        #all in string format
        code = item['code']
        title=item['title']
        semester=item['semester']
        type1=str(item['type']) + '-' +str(item['session'])
        category=item['category']

        time_slot = []
        date1 = int(float(item['date1']))
        start_time1 = int(float(item['start_time1']))
        end_time1 = int(float(item['end_time1']))

        # Append time slot1
        time_slot.append([date1,str(start_time1)+':00',str(end_time1)+':00'])

        # Append time slot2
        if (item['date2'] != 'nan'):
            date2 = int(float(item['date2']))
            start_time2 = int(float(item['start_time2']))
            end_time2 = int(float(item['end_time2']))
            time_slot.append([date2, str(start_time2) + ':00', str(end_time2) + ':00'])

        # Append time slot3
        if (item['date3'] != 'nan'):
            date3 = int(float(item['date3']))
            start_time3 = int(float(item['start_time3']))
            end_time3 = int(float(item['end_time3']))
            time_slot.append([date3, str(start_time3) + ':00', str(end_time3) + ':00'])

        detailed_course = Course(code, title, semester, type1, category, time_slot)
        result_list.append(detailed_course)

    return result_list

# df = pd.read_csv(filepath_or_buffer=timetablePath)
# for i in range (df.shape[1]):
#     print ((df.iloc[2,i]),type(df.iloc[2,i]))
#     print("convert to str:")
#     print(str(df.iloc[2,i]))

# result = download_original_table()
#
# for c in result:
#     print("===========")
#     c.display()

def get_course_by_code(list_of_code,semester):
    full_list = download_db()
    my_list = []
    for i in full_list:
        for j in list_of_code:
            if j == i.code and semester == i.semester:
                my_list.append(i)
    return my_list
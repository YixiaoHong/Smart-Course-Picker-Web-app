import flask
from flask import render_template, request, redirect, url_for, session
from app import webapp, Scheduler
from app.CourseFilter import filter_course_by_course_code
from app.DataReadHelper import *
from app.PopularityStatistic.S3Helper import create_presigned_url_expanded
from app.ScheduleEvent import ScheduleEvent
from app.Scheduler import find_course_by_code, remove_must_course_from_all_course
from app.db import download_original_table, get_course_by_code, update_hot_search_key_table

# must = []

# courses dont want to take
dislike = []

# max number of course for F
# maxF = 5
#
# # max number of course for S
# maxS = 5

# Degree requirment

# minimumECE = 5

# data = []

# optional = []

# curr_semester = "fall"

# limit = 5

@webapp.route("/", methods=['GET'])
def main_page():
    '''
    This function returns the mainpage
    :return: rendered "index.html"
    '''
    # return redirect(url_for("select_semester"))
    return render_template("index.html")
    # return render_template("m_test.html")

@webapp.route("/select-semester", methods=['GET'])
def select_semester():
    '''
    This function returns page for user to selecting the semesters
    :return: rendered "select_semester.html"
    '''
    error_msg = ''
    if 'error_msg' in session:
        error_msg = session['error_msg']
        session.pop('error_msg')
    img = create_presigned_url_expanded("pop_course.png")
    return render_template("select_semester.html",error_msg=error_msg, img = img, return_addr=url_for("course_select_must_have"), tag="select_semester")

@webapp.route("/select-must-have-course", methods=['POST'])
def course_select_must_have():
    '''
    This function takes the user input of which semester to schedule and display the available courses in the
    corresponding semester, and allow the user the pick the courses the user must take
    :return: randered page "course_selection.html"
    '''
    # global data#, curr_semester, limit
    #get data from AWS:
    type="Must have course"
    filtered_data_fall, filtered_data_winter = get_data_from_dynamo(dislike)
    # data = []
    limit = flask.request.form.get('limit', "5")
    semester = flask.request.form.get('semester', "fall")
    session['limit'] = limit
    session['semester'] = semester
    #make the data only for curr semester
    # if semester =="fall":
    #     data = filtered_data_fall
    # elif semester == "winter":
    #     data = filtered_data_winter
    # else:
    #     return "WRONG SEMESTER SELECTED!!!"
    data = get_unique_course_data(semester)
    # curr_semester = semester
    # result = Scheduler.schedule(filtered_data_fall, must, 2, 12)
    categories = get_all_categories(data)
    return render_template("course_selection.html", courses=data, curr_semester=semester, categories=categories, return_addr=url_for("submit_must_have_courses"), type=type, selected_courses_ctr=0, tag="select_must_course")


@webapp.route("/submit-must-have-courses", methods=['POST'])
def submit_must_have_courses():
    '''
    This function takes the user input of the courses the user must take and filter out the avaliable course list for
    the user to select the optional courses for the next step
    :return: redirect(url_for("course_select_optional")
    '''
    # global data
    form = request.form
    # limit = form['__PHX_ECE1779__limit']
    must=[]
    must_str=[]
    data = get_unique_course_data(session['semester'])

    #optional courses in form
    for c in form:
        found_course = find_course_by_code(c, data)
        if found_course is not None:
            must.append(found_course)
    for c in must:
        print(c.code)
        must_str.append(c.code)

    #determ if the selected must course exceed limit
    selected_must_number = len(must_str)
    limit = session['limit']

    if selected_must_number>int(limit):
        error_msg = "Error: The selected number of must taken courses exceed the course limit:" + str(limit)
        session['error_msg'] = error_msg
        return redirect(url_for("select_semester"))

    session['must']=must_str
    return redirect(url_for("course_select_optional"), code=307)


@webapp.route("/select-optional-course", methods=['POST'])
def course_select_optional():
    '''
    This function takes the user input of the courses the user must take and filter out the avaliable course list for
    the user to select the optional courses for the next step
    :return: render_template("course_selection.html")
    '''
    # global data
    type="Optional Course"
    semester=session['semester']
    data = get_unique_course_data(semester)
    # get data from AWS:
    # filtered_data_fall, filtered_data_winter = get_data_from_dynamo(dislike)
    must = session['must']

    must_courses = []
    if semester == "fall":
         must_courses = get_course_by_code(must,"F")
    elif semester == "winter":
        must_courses = get_course_by_code(must, "S")

    data = remove_must_course_from_all_course(must_courses, data)
    # result = Scheduler.schedule(filtered_data_fall, must, 2, 12)
    categories = get_all_categories(data)
    return render_template("course_selection.html", courses=data, categories=categories, return_addr=url_for("submit_optional_courses"), curr_semester=semester, type=type,selected_courses_ctr=len(must), tag="select_optional_course")


@webapp.route("/submit-optional-courses", methods=['POST'])
def submit_optional_courses():
    '''
    This function takes the user input of selected optional course and run the dfs search algorithm to check if the
    submitted must take courses has solution with no conflict, if so, it will return with an error. If not, it will
    continue using dfs search to fill the rest of the avaliable slots with the user selected optional courses. Finally,
    it will display to user with solutions and render a timetable.
    :return: render_template("schedule.html")
    '''

    semester=session['semester']

    must = session['must']

    must_courses = []
    if semester == "fall":
         must_courses = get_course_by_code(must,"F")
    elif semester == "winter":
        must_courses = get_course_by_code(must, "S")

    optional=[]
    form = request.form
    limit = session['limit']
    # print(form)
    data = get_data(semester)
    for c in form:
        found_course = find_course_by_code(c, data)
        if found_course is not None:
            optional.append(found_course)


    #Update the hot course table
    must_hot = []
    for mc in must_courses:
        new = True
        for mhc in must_hot:
            if mc.code == mhc.code:
                new = False
        if new:
            must_hot.append(mc)
    update_hot_search_key_table(must_hot)
    opt_hot = []
    for oc in optional:
        new = True
        for ohc in opt_hot:
            if oc.code == ohc.code:
                new = False
        if new:
            opt_hot.append(oc)
    update_hot_search_key_table(opt_hot)

    print("====================")
    for c in must_courses:
        c.display()
    print("-----------------------")
    #retrive all optional courses by code
    optional_courses = []
    optional_string_list = []
    for course_obj in optional:
        optional_string_list.append(course_obj.code)

    if semester == "fall":
         optional_courses = get_course_by_code(optional_string_list,"F")
    elif semester == "winter":
        optional_courses = get_course_by_code(optional_string_list, "S")

    for c in optional_courses:
        c.display()

    result = Scheduler.schedule(optional_courses, must_courses, limit, 12)

    info_msg = ''

    if result == 'no must solution':
        info_msg = 'The must-take courses you selected have conflict! :('
        return render_template("schedule.html", pageTitle=str(semester) + 'Schedule - Result',
                               detailed_solution_dict=[], info_msg=info_msg)

    # print("OPTIONAL:")
    # for i in optional:
    #     print(i)
    # print("MUST:")
    # for i in must:
    #     print(i)
    # print("*******************************")
    # res = "MUST: "
    # for c in must:
    #     res += c.code + " "
    # res += "\nOptional: "
    # for c in optional:
    #     res += c.code + " "
    if result == 'no must solution':
        return 'No valid combination for the must take courses, try to reduce the number of them or put them in optional'
    res=""
    for r in result:
        res+="=====================\n"
        # print("================")
        for rl in r:
            res+=rl.code+"|"+rl.semester+"|"+rl.type+ "|"+str(rl.time_slot)+"<br/>"
            # rl.display()


    ############################################################
    ###############     prepare schedule display  ##############
    ############################################################

    for each_result in result:
        print("solution==>")
        for c in each_result:
            c.display()

    colortype_list = ["event-1", "event-2", "event-3", "event-4"]

    detailed_solution_dict = dict()
    #dictionary(different solution)-dictionary(different day)-list(different event object)-detailedCourseObject

    maxRange = min(8,len(result))

    for index in range(maxRange):
        single_result = result[index]
        mondayEvents = []
        tuesdayEvents = []
        wednesdayEvents = []
        thursdayEvents = []
        fridayEvents = []

        for course in single_result:

            """
            solution course
            Code=> ECE1501H   //Title: Error Control Codes             //Semester: F  //Type: LEC-1_TUT-0_PRA-0     //Category: Communications   //Timeslot: [18, 19, 49, 50]
            Code=> ECE1774H   //Title: Sensory Cybernetics             //Semester: F  //Type: LEC-1_TUT-0_PRA-0     //Category: Biomedical Engi  //Timeslot: [1, 2]
    
            data base detail
            Code=> ECE537H1   //Title: Random Processes                //Semester: F  //Type: PRA-1                 //Category: Communications   //Timeslot: [[1, '10:00', '12:00']]
            """

            all_courses = []

            semester_abbr = 'F'
            if semester == "winter":
                semester_abbr = 'S'

            database = download_original_table()
            count = 0
            for course in single_result:
                count += 1
                for eachdata in database:
                    if eachdata.code == course.code and eachdata.type in course.type and eachdata.semester == semester_abbr:
                        all_courses.append([eachdata, count])

            # Code=> ECE1501H   //Title: Error Control Codes             //Semester: F  //Type: LEC-1                 //Category: Communications   //Timeslot: [[2, '15:00', '17:00'], [5, '10:00', '12:00']]

            for picked_course_list in all_courses:
                picked_course = picked_course_list[0]
                colortype_index = (picked_course_list[1] - 1) % 4
                code = picked_course.code
                title = str(picked_course.code) + str(picked_course.semester) + " " + str(picked_course.title) + " " + str(
                    picked_course.type)
                for slot in picked_course.time_slot:
                    day = slot[0]
                    # print(type(day))
                    starttime = slot[1]
                    endtime = slot[2]
                    scheduleEvent = ScheduleEvent(starttime, endtime, colortype_list[colortype_index], title)
                    if day == 1:
                        mondayEvents.append(scheduleEvent)
                    elif day == 2:
                        tuesdayEvents.append(scheduleEvent)
                    elif day == 3:
                        wednesdayEvents.append(scheduleEvent)
                    elif day == 4:
                        thursdayEvents.append(scheduleEvent)
                    elif day == 5:
                        fridayEvents.append(scheduleEvent)
            # scheduleEvent = ScheduleEvent('19:00', '21:00', 'event-4', 'test course')
            # fridayEvents.append(scheduleEvent)
        disp_index = index + 1
        detailed_solution_dict["solution_"+str(disp_index)] = dict()

        detailed_solution_dict["solution_" + str(disp_index)]['mondayEvents'] = mondayEvents
        detailed_solution_dict["solution_" + str(disp_index)]['tuesdayEvents'] = tuesdayEvents
        detailed_solution_dict["solution_" + str(disp_index)]['wednesdayEvents'] = wednesdayEvents
        detailed_solution_dict["solution_" + str(disp_index)]['thursdayEvents'] = thursdayEvents
        detailed_solution_dict["solution_" + str(disp_index)]['fridayEvents'] = fridayEvents
        detailed_solution_dict["solution_" + str(disp_index)]["solutionNumber"] = "solution_" + str(disp_index)

    if len(detailed_solution_dict) == 0:
        info_msg = 'Sorry, there is no solution for the given conditions :('

    if semester == "fall":
        semester = "Fall"
    if semester == "winter":
        semester = "Winter"
    return render_template("schedule.html", pageTitle= str(semester) + ' Schedule Result', detailed_solution_dict=detailed_solution_dict, info_msg=info_msg)

@webapp.route("/display_img", methods=['GET'])
def display_img_helper():
    '''
    A simple test routing for displaying an image
    :return: render_template("img_display.html"
    '''
    img = create_presigned_url_expanded("pop_course.png")
    return render_template("img_display.html", img = img)




def get_data(semester):
    '''
    this function helps get a list of Course object from databse with given semester
    :param semester: F/S
    :return: list of Course objects
    '''
    filtered_data_fall, filtered_data_winter = get_data_from_dynamo(dislike)
    data = []
    if semester == "fall":
        data = filtered_data_fall
    elif semester == "winter":
        data = filtered_data_winter
    else:
        return "WRONG SEMESTER SELECTED!!!"
    return data

def get_unique_course_data(semester):
    '''
    This function retures a list of course objects with unique course code
    :param semester: F/S
    :return: list of Course objects
    '''
    filtered_data_fall, filtered_data_winter = get_data_from_dynamo(dislike)
    data = []

    if semester == "fall":
        data = filtered_data_fall
    elif semester == "winter":
        data = filtered_data_winter
    else:
        return "WRONG SEMESTER SELECTED!!!"

    list_of_selected_course_codes = []
    return_unique_data = []
    for each_course in data:
        if each_course.code not in list_of_selected_course_codes:
            list_of_selected_course_codes.append(each_course.code)
            return_unique_data.append(each_course)

    return return_unique_data


def get_all_categories(course_list):
    '''
    This function returns a list of string which includes all the course categories from a given course list
    :param course_list: given courses
    :return: list of string
    '''
    categories=[]
    for course in course_list:
        if course.category not in categories:
            categories.append(course.category)
    return categories

# def pop_data():

# def test():
#     must=[]
#     # optional=[]
#     optional, winter = get_data_from_dynamo([])
#     result = Scheduler.schedule(optional, must, 2, 12)
#     print("test print")
#     for r in result:
#         print("================")
#         for rl in r:
#             rl.display()
#
# test()
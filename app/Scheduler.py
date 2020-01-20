import itertools
import numpy as np
# get courses must take
from app.DataReadHelper import *

def __dfs(available_slots, available_courses, course_limit, already_selected, solution):
    '''
    This function implement a DFS algorithm to search different permutation of the given available course options and
    recursively call it self until all the solution are found, each solution will be attached into the solution list
    and be returned (this algorithm make sure all the given course code has to be selected)
    :param available_slots: the current available slotes
    :param available_courses: the current available course options
    :param course_limit: the remaining available course can be selected
    :param already_selected: the courses already selected
    :param solution: the so far searched solution set
    :return: solution list
    '''
    if course_limit <= 0:
        solution.append(already_selected)
        return
    for course in available_courses:
        curr_step_already_selected = copy.deepcopy(already_selected)
        curr_step_available_slots = copy.deepcopy(available_slots)
        curr_step_available_courses = copy.deepcopy(available_courses)
        # curr_step_time_slot = time_slot
        curr_step_limit = course_limit
        fit = True
        for course_slot_index in course.time_slot:
            if curr_step_available_slots[course_slot_index] == 1:
                fit = False
                break
        if fit:
            curr_step_already_selected.append(course)

            for course_slot_index in course.time_slot:
                curr_step_available_slots[course_slot_index] = 1
            #now remove all the course in the abaliable courses which has the same code as the selected course
            current_course_code = course.code
            to_delete_index = []
            for index in range(len(curr_step_available_courses)):
                if curr_step_available_courses[index].code == current_course_code:
                    to_delete_index.append(index)
            to_delete_index.sort(reverse=True)
            for i in to_delete_index:
                curr_step_available_courses.pop(i)
            curr_step_limit-=1

            # for avail_time_slot_index in range(curr_step_time_slot + 1, len(curr_step_available_slots)):
            #     if curr_step_available_slots[avail_time_slot_index]==0:
            #         curr_step_time_slot = avail_time_slot_index
            #         break
            __dfs(curr_step_available_slots, curr_step_available_courses, curr_step_limit, curr_step_already_selected, solution)

def __dfs_optional(available_slots, available_courses, course_limit, already_selected, solution):
    '''
    This function implement a DFS algorithm to search different permutation of the given available course options and
    recursively call it self until all the solution are found, each solution will be attached into the solution list
    and be returned (this algorithm does not require all the given course code has to be selected)
    :param available_slots: the current available slotes
    :param available_courses: the current available course options
    :param course_limit: the remaining available course can be selected
    :param already_selected: the courses already selected
    :param solution: the so far searched solution set
    :return: solution list
    '''
    if course_limit <= 0:
        solution.append(already_selected)
        return
    for course in available_courses:
        curr_step_already_selected = copy.deepcopy(already_selected)
        curr_step_available_slots = copy.deepcopy(available_slots)
        curr_step_available_courses = copy.deepcopy(available_courses)
        # curr_step_time_slot = time_slot
        curr_step_limit = course_limit
        fit = True
        for course_slot_index in course.time_slot:
            if curr_step_available_slots[course_slot_index] == 1:
                fit = False
                break
        if fit:
            curr_step_already_selected.append(course)

            for course_slot_index in course.time_slot:
                curr_step_available_slots[course_slot_index] = 1
            #now remove all the course in the abaliable courses which has the same code as the selected course
            current_course_code = course.code
            to_delete_index = []
            for index in range(len(curr_step_available_courses)):
                if curr_step_available_courses[index].code == current_course_code:
                    to_delete_index.append(index)
            to_delete_index.sort(reverse=True)
            for i in to_delete_index:
                curr_step_available_courses.pop(i)
            curr_step_limit-=1

            # for avail_time_slot_index in range(curr_step_time_slot + 1, len(curr_step_available_slots)):
            #     if curr_step_available_slots[avail_time_slot_index]==0:
            #         curr_step_time_slot = avail_time_slot_index
            #         break
            __dfs(curr_step_available_slots, curr_step_available_courses, curr_step_limit, curr_step_already_selected, solution)

def schedule(course_list, must_have_course_list, max_course_load, max_time_slot_per_day):
    '''
    This function schedule the timetable with two steps, the first step it try to fill the must take courses and see if
    there is any solution, if not it will return info saying there is no solution for must take courses. In the next step, it passes
    the current filled solutions (must courses) with optional courses and run dfs a second time and try to fill the rest course limit with
    optional courses and attach all the solutions to a list and return
    :param course_list:  all the avaliable courses
    :param must_have_course_list: the user given must taken courses
    :param max_course_load: the mat course load
    :param max_time_slot_per_day: the max time slots for a day
    :return: list of all solutions
    '''
    # for must_course in must_have_course_list:
    #     found = False
    #     for course in course_list:
    #         if course.code==must_course.code:
    #             found=True
    #             break
    #     if not found:
    #         raise Exception("Must have course list contains course: " + str(must_course) + " that is not in the course list!")
    avaliableSlots = [0] * max_time_slot_per_day * 5
    solution = []
    must_courses = []

    filtered_data_cp = copy.deepcopy(course_list)
    # # must_courses = remove_must_course_from_all_course(must_have_course_list, course_list)
    # for must_course_code in must_have_course_list:
    #     found_course = find_course_by_code(must_course_code, filtered_data_cp)
    #     if found_course!=None:
    #         filtered_data_cp.remove(found_course)
    #         must_courses.append(found_course)


    # for course in course_list:
    #     for must_course_code in must_have_course_list:
    #         if course.code == must_course_code:
    #             find_course_by_code(must_course_code, course_list)
    #             filtered_data_cp.remove(course)
    #             must_courses.append(course)

    #find solutions for all must courses

    #count unique selected courses

    list_of_selected_course_codes = []
    for each_course in must_have_course_list:
        if each_course.code not in list_of_selected_course_codes:
            list_of_selected_course_codes.append(each_course.code)


    __dfs(avaliableSlots, copy.deepcopy(must_have_course_list), len(list_of_selected_course_codes), [], solution)
    must_solution = copy.deepcopy(solution)
    must_solution = remove_must_courses_duplicate(must_solution)
    if len(must_solution) == 0:
        return 'no must solution'
    # print("****************************************"+str(len(must_solution)))
    # for i in must_solution:
    #     print(i)
    #     for c in i:
    #         c.display()
    print("Start solving:")
    final_solution=[]
    for must_sol in must_solution:
        solution = []
        curr_available_slot = [0] * 60
        #occupy must slots:
        for each_must_course in must_sol:
            for slot in each_must_course.time_slot:
                curr_available_slot[slot] = 1
        optional_course_num=int(max_course_load)-len(list_of_selected_course_codes)
        __dfs_optional(curr_available_slot, course_list, optional_course_num, [], solution)
        for optionsolu in solution:
            final_solution.append(must_sol+optionsolu)




    #here we get all the solutions
    print("=====Solutions=====")
    for eachsolu in final_solution:
        print("===ONE SOLUTION===")
        for c in eachsolu:
            c.display()
    print("=====Solutions  print end=====")


    # for ml in must_solution:
    #     temp_l = []
    #     for l in ml:
    #         temp_l.append(l)
    #     for j in range(len(solution)):
    #         solution[j] = solution[j] + temp_l
    result=remove_must_courses_duplicate(final_solution)

    if (len(result) == 0):
        print("Scheduled: no solution")
    else:
        print("Scheduled: solution found")
    return result

def remove_must_course_from_all_course(must_have_course_list, course_list):
    '''
    This function removes the must taken course from the total course list
    :param must_have_course_list: must taken course list
    :param course_list: all courses
    :return: filtered list
    '''
    filtered_data_fall_cp = copy.deepcopy(course_list)
    for must_course in must_have_course_list:
        found_course = find_course_by_code(must_course.code, filtered_data_fall_cp)
        if found_course is not None:
            filtered_data_fall_cp.remove(found_course)
    return filtered_data_fall_cp

def find_course_by_code(code, course_list):
    '''
    This function returns all the course in the list with given code
    :param code: wanted code
    :param course_list: all courses list
    :return: filtered list
    '''
    for course in course_list:
        # print(course.code + "|||" + code)
        if course.code == code:
            return course
    return None


def remove_must_courses_duplicate(list):
    '''
    This function removes duplicate courses (code) from the course list and only remains a unique course list
    :param list: course list
    :return: unique course list
    '''
    already_selected_solution_set = set()
    return_unique_data = []


    for sol in list:
        sol_set_id_string = ""
        set_len_before = len(already_selected_solution_set)
        sol_sorted = sorted(sol)
        for course in sol_sorted:
            sol_set_id_string += str(course.code) + str(course.type)
        already_selected_solution_set.add(sol_set_id_string)
        if len(already_selected_solution_set) != set_len_before:
            return_unique_data.append(sol_sorted)

    return return_unique_data

def show_detail(each_solution):
    '''
    displys the detail of a solution
    :param each_solution: #each_solution is a list of course object
    :return: list of detailcourse object
    '''
    output =[]
    for course in each_solution:
        code = course.code
        title = course.title
        semester = course.semester
        category = course.category

        #LEC-1_TUT-0_PRA-0
        concatedtype = course.type

        sessions = concatedtype.split()


        lec_session = lec_session
        tut_session = tut_session
        pra_session = pra_session
        lec_time_slot = lec_time_slot
        tut_time_slot = tut_time_slot
        pra_time_slot = pra_time_slot








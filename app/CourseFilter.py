def filter_course_by_course_code(course_list, course_code):
    '''
    pick course objects with specific course code from all course lists
    :param course_list:  course list
    :param course_title:  the given course code
    :return: list of filtered course objects
    '''
    result = __get_courses_by_attr_contains(course_list, course_code, "code")
    return result

def filter_course_by_course_category(course_list, course_category):
    '''
    pick course objects with specific course category from all course lists
    :param course_list:  course list
    :param course_title:  the given course category
    :return: list of filtered course objects
    '''
    result = __get_courses_by_attr_exact(course_list, course_category, "category")
    return result

def filter_course_by_course_title(course_list, course_title):
    '''
    pick course objects with specific course title from all course lists
    :param course_list:  course list
    :param course_title:  the given course title
    :return: list of filtered course objects
    '''
    result = __get_courses_by_attr_contains(course_list, course_title, "code")
    return result

def __get_courses_by_attr_exact(course_list, keyword, attr):
    '''
    pick course objects with specific key words in an attribute from all the course object list
    :param course_list: course list
    :param keyword: the keyword
    :param attr: the attribute
    :return: list of filtered course objects
    '''
    result = []
    for course in course_list:
        if course.__getattribute__(attr)==keyword:
            result.append(course)
    return result

def __get_courses_by_attr_contains(course_list, keyword, attr):
    '''
    pick course objects contains specific keywords in an attribute from all the course object list
    :param course_list: course list
    :param keyword: the keyword
    :param attr: the attribute
    :return: list of filtered course objects
    '''
    result = []
    for course in course_list:
        print(course.__getattribute__(attr))
        if keyword in course.__getattribute__(attr):
            result.append(course)
    return result
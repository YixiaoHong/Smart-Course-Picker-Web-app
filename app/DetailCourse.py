class DetailCourse:
    def __init__(self, code, title, semester, category, lec_session, slot):
        '''
        This class define a detailed course object and stores the necessary
        information for a course session which is ready to be displayed on
        a time table. It has attributes to record timeslots for lectures,
        practices and tuturials seperately.
        :param code: course code
        :param title: course title
        :param semester: course semester "S/F"
        :param category: course category
        :param lec_session: course lecture session
        :param slot: course occupied slots
        '''
        # code
        # title
        # semester
        # type
        # session
        # category
        # date1
        # start_time1
        # end_time1
        # date2
        # start_time2
        # end_time2
        # date3
        # start_time3
        # end_time3


        self.code = code
        self.title = title
        self.semester = semester
        self.category = category
        self.lec_session = lec_session
        self.tut_session = tut_session
        self.pra_session = pra_session
        self.lec_time_slot = lec_time_slot
        self.tut_time_slot = tut_time_slot
        self.pra_time_slot = pra_time_slot
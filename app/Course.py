class Course:
    '''
    This class define a course object and stores the necessary information for a course session
    '''

    def __init__(self, code, title, semester, type, category, time_slot):
        '''
        This is the init function for the class object, takes the following parameters
        :param code: the course code
        :param title: the course title
        :param semester: the course semester "F/S
        :param type: the session type "LEC/TUT/PRA"
        :param category: the course category
        :param time_slot: the session occupied time slots
        '''
        self.code = code
        self.title = title
        self.semester = semester
        self.type = type
        self.category = category
        self.time_slot = time_slot

    def display(self):
        '''
        display the current object
        :return:
        '''
        print("Code=>",'{:9s}'.format(self.code[0:9])," //Title:",'{:30s}'.format(self.title[0:30])," //Semester:",self.semester," //Type:",'{:20s}'.format(self.type[0:20])," //Category:",'{:15s}'.format(self.category[0:15])," //Timeslot:",self.time_slot)

    def __str__(self) -> str:
        '''
        get the string format of the object
        :return: string
        '''
        return "Course code: " + str(self.code) + " Title: " + str(self.title) + " Semester: " + str(self.semester) + " Type: " + str(self.type) + " Category: " + str(self.category) + "Time_Slot: " + str(self.time_slot)

    def __eq__(self, o) -> bool:
        '''
        get the The a == b expression invokes
        :param o: other object
        :return: self.code == o.code and self.semester == o.semester and self.time_slot == o.time_slot and self.category == o.category
        '''
        return self.code == o.code and \
               self.semester == o.semester and \
               self.time_slot == o.time_slot and \
               self.category == o.category

    def __hash__(self) -> int:
        '''
        return the hash result for the object
        :return: hash((self.code, self.semester, str(self.time_slot), self.category))
        '''
        # return super().__hash__()
        return hash((self.code, self.semester, str(self.time_slot), self.category))

    def __lt__(self, other):
        '''
        invoke the comparision process
        :param other: other object
        :return: hash(self.code)<hash(other.code)
        '''
        return hash(self.code)<hash(other.code)

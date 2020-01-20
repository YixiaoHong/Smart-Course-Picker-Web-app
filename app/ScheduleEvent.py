class ScheduleEvent:
    '''
    <This class define an event which can be displayed in a timetable>
    '''
    def __init__(self, starttime, endtime, colortype, title):
        '''
        The init function for the class, stores the information needed for an event
        :param starttime: event start time
        :param endtime: event end time
        :param colortype: event color
        :param title: event title
        '''
        self.starttime = starttime
        self.endtime = endtime
        self.colortype = colortype
        self.title = title
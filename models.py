"""Models used for playing with Habits"""
import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from base import Base


class HabitCategory(Base):
    """ Class for habit category, e.g. sports, inherits super constructor"""
    __tablename__ = 'HabitCategory'

    # an unique id and a name for the category of a habit
    cat_id = Column('cat_id', Integer, primary_key=True, autoincrement=True)
    cat_name = Column('cat_name', String, unique=True, nullable=False)

    def set_name(self, name):
        """" Sets the name of a category """
        self.cat_name = name

    def __str__(self):
        """ Returns the habit category name in a string context """
        return f"Name: {self.cat_name}"


class Habit(Base):
    """ Class for general habit """
    __tablename__ = 'Habit'

    # id member
    habit_id = Column('habit_id', Integer,
                      primary_key=True,
                      autoincrement=True)

    # define a relationship to the event table
    habit_events = relationship("HabitEvent", backref="Habit",
                                lazy='dynamic')
    # define a relationship to the category table
    cat_id = Column(Integer, ForeignKey('HabitCategory.cat_id'), default=0)

    # a user-definable name for a habit
    name = Column('name', String, nullable=False)

    # checked true/false, if this habit is enabled
    enabled = Column('enabled', Boolean, default=True)

    # when habit was created
    created = Column('created', String)
    # when habit was updated
    updated = Column('updated', String)

    # a condition function, that needs to be matched
    # eq => exactly match
    # lt => less than or equal
    # gt => greater than equal
    condition = Column('condition', String, default="")

    # the quota, if any condition function is given
    quota = Column('quota', Integer, default=0)

    # the  defined unit, like kilometres, number of jumps, ...
    unit = Column('unit', String, default="")

    # the weekdays, if any, where the habit needs to be done
    # encoded in a bitset, starting with monday, giving
    # 2^7 states
    # (bit 0 => monday, 1 => tuesday, 2 => wednesday,
    # 3 => thursday, 4 => friday, 5 => saturday,
    # 6 => sunday, 7 => weekly habit)
    # Example
    # weekday = 10 (int) = 00001010 (bits)
    # tasks need to be done on Tuesdays and Wednesday
    weekday = Column('weekday', Integer, default=0)

    # latest_streak for easier sorting
    latest_streak = Column('latest_streak', Integer, default=0)

    def __str__(self):
        return f"Name: {self.name}\n" \
               f"Condition: {self.condition} Quota / Units:" \
               f"{self.quota} {self.unit}"

    def set_created(self):
        """ Set date, when habit was created and tracking begins """
        self.created = datetime.date.today()
        self.set_updated(self.created)

    def set_updated(self, latest):
        """ Set update date, important, when
        habit was last tracked as completed and all missing
         events and tracking data was completed """
        self.updated = latest

    def add_day(self, day):
        """ Adds a day to the scheduler """
        if self.weekday is None:
            self.weekday = int(0)

        # Several cases here to solve
        if isinstance(day, str):
            if day.isnumeric() and 0 <= int(day) <= 6:
                self.add_day_by_number(int(day))
            else:
                self.add_day_by_name(day.lower())
        elif isinstance(day, int):
            self.add_day_by_number(int(day))

    def add_day_by_name(self, name):
        """ Adds a day to the weekday scheduler by name """
        days = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                "friday": 4, "saturday": 5, "sunday": 6}
        if name in days:
            self.add_day_by_number(days[name])

    def add_day_by_number(self, day):
        """ Adds a day to the weekday scheduler by integer """
        self.weekday = (1 << day) | self.weekday

    def due_today(self):
        """ Checks if habit is due today """

        # If the habit is weekly, it will be due at least at one day per week
        # so always return true
        if self.is_weekly():
            return True

        # Get today's weekday and return
        today_weekday = int(datetime.datetime.today().weekday())
        return self.due_weekday(today_weekday)

    def due_weekday(self, weekday):
        """ Checks if habit is due at some specific weekday """

        # If the habit is weekly, it will be due at least at one day per week
        # so always return true
        if self.is_weekly():
            return True

        # If habit is day by day, check if bit is not set for this weekday
        if (self.weekday & (1 << weekday)) == 0:
            return False

        # by default, a habit is due
        return True

    def is_weekly(self):
        """ Returns if habit is weekly """
        if self.weekday == 128:
            return True
        return False

    def disable(self):
        """ Disables the habit """
        self.enabled = False

    def enable(self):
        """ Enables the habit """
        self.enabled = True

    def set_name(self, name):
        """ Sets the name of the habit """
        self.name = name

    def reset_weekday(self):
        """ Resets the scheduler """
        self.weekday = int(0)

    def set_weekly(self):
        """ Set scheduler to weekly """
        self.reset_weekday()
        self.weekday = 1 << 7

    def get_satisfaction(self):
        """ Returns satisfaction condition as a string """

        if self.condition == "eq":
            return f"You need exactly {self.quota} " \
                   f"{self.unit} for succeeding {self.name}."
        if self.condition == "lt":
            return f"You need less or equal {self.quota} " \
                   f"{self.unit} for succeeding {self.name}."
        if self.condition == "gt":
            return f"You need greater or equal {self.quota} " \
                   f"{self.unit} for succeeding {self.name}."

        return "Just doing it, is enough for succeeding."

    def needs_satisfaction(self):
        """ Checks if this habit has a condition parameter """
        if self.condition != "":
            return True
        return False

    def satisfied(self, user_quota):
        """ Returns status, if habit condition function
        is satisfied by user quota """
        user_quota = int(user_quota)

        if self.condition == "eq":
            if self.quota == user_quota:
                return 1
        elif self.condition == "lt":
            if user_quota <= self.quota:
                return 1
        elif self.condition == "gt":
            if user_quota >= self.quota:
                return 1

        return 2

    def set_quota(self, quota, unit):
        """ Sets the quota and unit name for this habit """
        self.quota = quota
        self.unit = unit

    def set_condition(self, condition):
        """ Sets the condition function for this habit """
        if condition in ("eq", "lt", "gt"):
            self.condition = condition
            return True
        return False

    def update_streak(self, streak):
        """ updates number of latest streaks """
        self.latest_streak = streak


class HabitEvent(Base):
    """ Class for tracking single events """
    __tablename__ = 'HabitEvent'

    # the event_id for easier identification
    event_id = Column('event_id', Integer,
                      primary_key=True,
                      autoincrement=True)
    # foreign "key" to match habit to its events
    habit_id = Column(Integer, ForeignKey('Habit.habit_id'))

    # when was date/time to be scheduled, when was ist solved (t.b.a.)
    datetime = Column('datetime', String)
    datetime_solved = Column('datetime_solved', String, default="")

    # day of month and day of month the event as was done
    weekday = Column('weekday', Integer, default=0)

    # status
    # 0 = pending, 1 = done, 2 = not done
    status = Column('status', Integer, default=0)

    # variable for number of quota that was solved in that single event
    quota = Column('quota', Integer, default=0)

    def set_status(self, status):
        """set_status"""
        self.status = status

    def set_status_success(self):
        """set_status"""
        self.set_status(1)

    def set_status_fail(self):
        """set_status to fail event """
        self.set_status(2)

    def set_quota(self, user_quota):
        """ set the quota for this event """
        self.quota = user_quota

    def set_weekday(self, weekday):
        """" Sets the weekday, this event was done """
        self.weekday = weekday

    def set_created(self):
        """" Sets the the creation date of a single event """
        self.datetime = datetime.date.today()

    def set_solved(self, date):
        """" Sets the the actual solved date of a single event """
        self.datetime_solved = date

    def set_habit(self, habit_id):
        """" Sets the the habit id, to which the event belongs  """
        self.habit_id = habit_id

    def get_status(self):
        """" Gets current status as a str """
        if self.status == 1:
            return "Done"
        if self.status == 2:
            return "Failed"
        # Default pending == 0
        return "Pending"

    def get_status_num(self):
        """" Gets current status as a int """
        return self.status

    def __str__(self):
        """ prints Habits event id """
        return f"<HabitEvent {self.event_id}>"

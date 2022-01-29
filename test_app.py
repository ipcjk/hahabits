""" Test cases """
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import analytics
import app
import base
import models

# Create SQLite inside memory
# Create connection to sqlite database
# engine = create_engine('sqlite:///habit.sqlite3', echo=False)
engine = create_engine('sqlite:///', echo=False)
Session = sessionmaker(bind=engine)
base.Base.metadata.create_all(engine)
session = Session()

HABS = []
CATS = []
EVENTS = []


def test_generation_of_objects():
    """ Populate test database inside memory """
    # Generate 5 categories
    global CATS
    CATS = [models.HabitCategory(cat_name="Sport"),
            models.HabitCategory(cat_name="Leisure"),
            models.HabitCategory(cat_name="Uni"),
            models.HabitCategory(cat_name="Friends"),
            models.HabitCategory(cat_name="Family"),
            models.HabitCategory(cat_name="Social work")]

    for xcats in CATS:
        session.add(xcats)
        session.commit()
        # Categories will now have a cat_id
        assert str(xcats.cat_id).isnumeric()

    # Generate list of 6 habits
    global HABS
    HABS = [
        models.Habit(cat_id=1, name="Running", enabled=True, created="2022-01-01"),
        models.Habit(cat_id=2, name="Walking around", enabled=True, created="2022-01-01"),
        models.Habit(cat_id=3, name="Study Math", enabled=True, created="2022-01-01"),
        models.Habit(cat_id=4, name="Playing pool", enabled=True, created="2022-01-01"),
        models.Habit(cat_id=5, name="Reading to kids", enabled=True, created="2022-01-01"),
        models.Habit(cat_id=6, name="Doing something else", enabled=False, created="2022-01-01")
    ]

    # Running on Wednesday and Saturday
    HABS[0].add_day(5)
    HABS[0].add_day(2)
    #  Walking around on every day
    HABS[1].add_day(0)
    HABS[1].add_day(1)
    HABS[1].add_day(2)
    HABS[1].add_day(3)
    HABS[1].add_day(4)
    HABS[1].add_day(5)
    HABS[1].add_day(6)
    # Study math Sunday and Thursday
    HABS[2].add_day("Sunday")
    HABS[2].add_day("Thursday")
    # Play pool on Sunday
    HABS[3].add_day("Sunday")
    # Read kids "weekly"
    HABS[4].set_weekly()

    # Set updated for later event checking
    HABS[0].set_updated("2022-01-31")
    HABS[1].set_updated("2022-01-31")
    HABS[2].set_updated("2022-01-31")
    HABS[3].set_updated("2022-01-31")
    HABS[4].set_updated("2022-01-31")

    # Add condition functions to reading kids and playing pool
    HABS[4].set_condition("gt")
    HABS[4].set_quota("3", "books")
    HABS[3].set_condition("eq")
    HABS[3].set_quota("5", "rounds")

    # Add to virtual session
    session.add(HABS[0])
    session.add(HABS[1])
    session.add(HABS[2])
    session.add(HABS[3])
    session.add(HABS[4])
    session.commit()


def test_habit_satisfactions():
    """ Check satisfaction for all habits """
    assert HABS[0].satisfied(0)
    assert HABS[1].satisfied(0)
    assert HABS[2].satisfied(0)
    assert not HABS[0].needs_satisfaction()
    assert not HABS[1].needs_satisfaction()
    assert not HABS[2].needs_satisfaction()
    assert HABS[3].needs_satisfaction()
    assert HABS[4].needs_satisfaction()
    assert HABS[3].satisfied(2) == 2
    assert HABS[3].satisfied(3) == 2
    assert HABS[3].satisfied(5)
    assert HABS[3].satisfied(6) == 2
    assert HABS[4].satisfied(0) == 2
    assert HABS[4].satisfied(3)
    assert HABS[4].satisfied(-1) == 2

    # Check due days (for hab first at least=
    assert HABS[0].due_weekday(5)
    assert HABS[0].due_weekday(2)
    assert not HABS[0].due_weekday(0)
    assert not HABS[0].due_weekday(1)
    assert not HABS[0].due_weekday(4)
    assert not HABS[0].due_weekday(6)


def test_habitevent():
    """ Test habitevent class """
    habitevent = models.HabitEvent()

    # Default is pending
    assert habitevent.get_status() == "Pending"

    habitevent.set_status_success()
    assert habitevent.get_status() == "Done"

    habitevent.set_status_fail()
    assert habitevent.get_status() == "Failed"

    habitevent.set_weekday(6)
    assert habitevent.weekday == 6
    assert habitevent.weekday != 7

    habitevent.set_quota(90)
    assert habitevent.quota == 90
    assert habitevent.quota != 10

    habitevent.set_habit(45)
    assert habitevent.habit_id == 45


def test_habit_category():
    """ Test the category class """
    cat = models.HabitCategory()

    # Set and check name
    cat.set_name("Foo bar")
    assert cat.cat_name == "Foo bar"


def test_habit_defaults():
    """ Test habit class """
    habit = models.Habit()

    habit.set_name("Karate")
    assert habit.name == "Karate"

    habit.enable()
    assert habit.enabled

    # Weekdays
    habit.set_weekly()
    assert habit.is_weekly()
    assert habit.weekday == 128
    habit.reset_weekday()
    assert habit.weekday == 0
    assert not habit.is_weekly()

    # Weekday scheduling
    habit.add_day("Wednesday")
    assert habit.due_weekday(2)
    assert not habit.due_weekday(4)
    assert not habit.due_weekday(5)
    assert not habit.due_weekday(6)
    assert not habit.due_weekday(0)
    assert not habit.due_weekday(1)
    assert not habit.due_weekday(3)
    assert not habit.due_weekday(71)
    assert not habit.is_weekly()
    habit.add_day_by_number(4)
    assert habit.due_weekday(4)

    # condition checker
    habit.set_condition("eq")
    habit.set_quota(90, "km")
    assert habit.needs_satisfaction()
    assert habit.satisfied(90) == 1
    assert habit.satisfied(50) == 2
    assert habit.satisfied(100) == 2


def test_event_system_for_checkoff():
    """ Tests for the habitevent system"""
    global HABS
    global CATS

    # Add test events
    events1_dates = ["2022-01-01", "2022-01-05", "2022-01-08", "2022-01-12",
                     "2022-01-15", "2022-01-19", "2022-01-22", "2022-01-26",
                     "2022-01-29"]
    events1_weekdays = [5, 2, 5, 2, 5, 2, 5, 2, 5]
    events1_status = [0, 1, 1, 1, 2, 0, 1, 2, 0]

    def helper(eve, solve, weekday, ste):
        eve.set_solved(solve)
        eve.set_weekday(weekday)
        eve.set_status(ste)
        session.commit()

    # Generate events
    streaks = ""
    for i in range(0, 9):
        eve = models.HabitEvent(habit_id=1)
        session.add(eve)
        session.commit()
        helper(eve, events1_dates[i], events1_weekdays[i], events1_status[i])
        streaks = streaks + str(eve.get_status_num())

    # Longest streak shall be 3 by now (consecutive 3x1)
    assert analytics.get_lstreaks_single(streaks) == 3

    # Add test events for habit 2
    # Add test events
    events2_dates = []
    for i in range(1, 32):
        events2_dates.append("2022-01-" + str(i))
    events2_weekdays = [5, 6, 0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 5, 6, 0,
                        1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 5, 6, 0, 1]
    events2_status = [0, 1, 1, 1, 2, 0, 1, 2, 0, 1, 1, 1, 1, 1, 1, 1, 1,
                      1, 1, 1, 0, 2, 0, 0, 0, 0, 1, 2, 2, 1, 0, 1]
    # Generate events
    streaks = ""

    # Demo, run all days in  01/2022
    for i in range(0, 31):
        eve = models.HabitEvent(habit_id=2)
        session.add(eve)
        session.commit()
        helper(eve, events2_dates[i], events2_weekdays[i], events2_status[i])
        streaks = streaks + str(eve.get_status_num())

    # Longest streak shall be 11 for event2 by now (consecutive 11x1)
    assert analytics.get_lstreaks_single(streaks) == 11

    # Add test events for habit 3
    events3_dates = ["2022-01-02", "2022-01-06", "2022-01-09", "2022-01-13",
                     "2022-01-16",
                     "2022-01-20", "2022-01-23", "2022-01-27", "2022-01-30"]
    events3_weekdays = [6, 3, 6, 3, 6, 3, 6, 3, 6]
    events3_status = [0, 0, 1, 0, 0, 0, 1, 1, 0]
    # Generate events
    streaks = ""

    for i in range(0, 9):
        eve = models.HabitEvent(habit_id=3)
        session.add(eve)
        session.commit()
        helper(eve, events3_dates[i], events3_weekdays[i], events3_status[i])
        streaks = streaks + str(eve.get_status_num())

    # Longest streak shall be 2 for event3 by now (consecutive 11x1)
    assert analytics.get_lstreaks_single(streaks) == 2


def test_event_system_for_condition():
    """ Tests the event system with condition style habits """

    def helper(eve, solve, weekday, ste):
        eve.set_solved(solve)
        eve.set_weekday(weekday)
        eve.set_status(ste)
        session.commit()

    # Add test events for habit 4
    events4_dates = ["2022-01-02", "2022-01-09", "2022-01-16",
                     "2022-01-23", "2022-01-30"]
    events4_weekdays = [6, 6, 6, 6, 6]
    events4_quota = [1, 5, 5, 5, 5]
    # Generate events
    streaks = ""

    for i in range(0, 5):
        eve = models.HabitEvent(habit_id=4)
        session.add(eve)
        session.commit()
        eve.set_quota(events4_quota[i])
        status = HABS[3].satisfied(events4_quota[i])
        helper(eve, events4_dates[i], events4_weekdays[i], status)
        streaks = streaks + str(eve.get_status_num())

    # Longest streak shall be 4 for event4 by now
    assert analytics.get_lstreaks_single(streaks) == 4

    # Add test events for habit 5
    events5_dates = ["2022-01-06", "2022-01-13", "2022-01-19",
                     "2022-01-24", "2022-01-31"]
    events5_weekdays = [3, 3, 2, 0, 0]
    events5_quota = [1, 2, 3, 1, 4]
    # Generate events
    streaks = ""

    for i in range(0, 5):
        eve = models.HabitEvent(habit_id=5)
        session.add(eve)
        session.commit()
        assert str(eve.event_id).isnumeric()
        eve.set_solved(events5_dates[i])
        eve.set_weekday(events5_weekdays[i])
        # Status calculated by satisfaction
        status = HABS[4].satisfied(events5_quota[i])
        eve.set_quota(events5_quota[i])
        helper(eve, events5_dates[i], events5_weekdays[i], status)
        session.add(eve)
        streaks = streaks + str(eve.get_status_num())

    # Longest streak shall be 1 for event5 by now
    assert analytics.get_lstreaks_single(streaks) == 1
    session.commit()


def test_analytics_habits_streaks():
    """ Test habit all streaks """
    # Call the analytics
    habits = session.query(models.Habit).filter(models.Habit.enabled).all()
    habit_events = session.query(models.HabitEvent).filter().all()

    habits_with_streaks = analytics.get_lstreaks_all(habits, habit_events)

    for item in habits_with_streaks:
        if item.habit_id == 1:
            assert habits_with_streaks[item] == 3
            assert item.name == "Running"
        if item.habit_id == 2:
            assert habits_with_streaks[item] == 11
        if item.habit_id == 3:
            assert habits_with_streaks[item] == 2
        if item.habit_id == 4:
            assert habits_with_streaks[item] == 4
        if item.habit_id == 5:
            assert habits_with_streaks[item] == 1
            assert item.name == "Reading to kids"


def test_analytics_habits_weekday():
    """ Test habits per weekday """

    habits = session.query(models.Habit).filter(models.Habit.enabled).all()
    habits_within_weekday = analytics.get_habits_weekday(habits, 3)
    assert len(habits_within_weekday) == 3
    habits_within_weekday = analytics.get_habits_weekday(habits, 6)
    assert len(habits_within_weekday) == 4
    habits_within_weekday = analytics.get_habits_weekday(habits, 0)
    assert len(habits_within_weekday) == 2

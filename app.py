#!/usr/bin/env python3

"""
haha-bits, a small habit tracker in Python

// (C) 2022 by Jörg Kost <jk@ip-clear.de>
// MIT License

"""
# Import engine and session creator
import datetime
import calendar
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import analytics

# Import Base for SQL Classes
import base
# Import our menu class
from climenu import CliMenu, ask, ask_many
# Import our model classes
import models

exception_inputs = (KeyboardInterrupt, EOFError)


def habit_delete(habit_id):
    """ Delete habit and events and then commit to SQL """

    habit = session.query(models.Habit).get(habit_id)

    # If the habit is not found, we return
    if habit is None:
        print("This habit does not exist.")
        return

    session.query(models.Habit).filter(
        models.Habit.habit_id == habit_id).delete()
    session.query(models.HabitEvent).filter(
        models.HabitEvent.habit_id == habit_id).delete()
    session.commit()

    print("habit deleted.")


def cat_delete(cat_id):
    """ Delete habit category and commits to SQL """
    cat = session.query(models.HabitCategory).get(cat_id)

    # If the habit is not found, we return
    if cat is None:
        print("This category does not exist.")
        return

    session.query(models.HabitCategory).filter(
        models.HabitCategory.cat_id == cat_id).delete()
    session.commit()
    print("category deleted.")

# Habit List
def habit_list_ay():
    """ Prints out a list of all habits """
    habits = session.query(models.Habit).filter().all()
    print("\tAll habits\n\tID\tName\tEnabled")

    # Call analytics
    for hab in analytics.get_habits(habits):
        print_habit_row_status(hab)


# Reset an event to "OPEN" state
def reset_event():
    """ Resets an event by id, so the user can modify the event with the
     checkoff function again """
    try:
        event_id = ask("Enter the id of the event, to set this event "
                       "to a pending/open state ", r"^\d{1,8}$")
    except exception_inputs:
        return

    event = session.query(models.HabitEvent).get(event_id)
    # If the event is not found, we return
    if event is None:
        print("This event does not exist")
        return

    # Set status of this event to 0 = PENDING with none quota
    event.set_status(0)
    event.set_quota(0)

    # Execute against DB
    session.add(event)
    session.commit()

    print(f"Event reset, please run "
          f"check(o)ff {event.habit_id} to resolve the issue")


def habit_average():
    """ Average of a habits condition with help of functional """
    try:
        habit_id = ask("Enter the id of the habit,"
                       "to check for it's average quota runs", r"^\d{1,8}$")
    except exception_inputs:
        return

    habit = session.query(models.Habit).get(habit_id)
    # If the habit is not found, we return
    if habit is None:
        print("This habit does not exist")
        return

    if habit.condition == "":
        print("This habit has no condition function")
        return

    habit_events = session.query(models.HabitEvent). \
        order_by(models.HabitEvent.datetime_solved).filter(
        models.HabitEvent.habit_id == habit_id).all()

    # Run analytics
    average = analytics.get_calculate_avg(habit_events)
    print(f"In average you did {average} {habit.unit} per practise")


def longest_streak_int():
    """ Longest streak of a habit with help of functional """
    try:
        habit_id = ask("Enter the id of the habit,"
                       "to check for it's longest streak", r"^\d{1,8}$")
    except exception_inputs:
        return

    habit_events = session.query(models.HabitEvent). \
        order_by(models.HabitEvent.datetime_solved).filter(
        models.HabitEvent.habit_id == habit_id).all()

    # prepare data for analytics
    streaks = ""
    for event in habit_events:
        streaks = streaks + str(event.status)

    # Run analytics
    longest_streak = analytics.get_lstreaks_single(streaks)
    print(f"Longest streak {longest_streak}")


def habit_scheduler_list():
    """ Get longest streak for all habits """

    # Get all habits and habit_events
    habits = session.query(models.Habit).filter(models.Habit.enabled).all()
    try:
        week_input = ask("Please input the weekday-number that you "
                         "want to check for habits", "^([0-6])$")
    except exception_inputs:
        return

    # Call the analytics function
    habits_weekday = analytics.get_habits_weekday(habits, int(week_input))
    print("\tScheduled on this day\n\tID\tName\tDays")
    for hab in habits_weekday:
        print_habit_row_weekly(hab)


def longest_streak_all_int():
    """ Get longest streak for all habits """

    # Get all habits and habit_events
    habits = session.query(models.Habit).filter(models.Habit.enabled).all()
    habit_events = session.query(models.HabitEvent).order_by(
        models.HabitEvent.datetime_solved).filter().all()

    # Call the analytics
    habits_with_streaks = analytics.get_lstreaks_all(habits, habit_events)

    print("Longest streaks of all habits")
    print("\tID\tName\tStreak")
    for item in habits_with_streaks:
        print(f"\t{item.habit_id}\t{item.name}\t{habits_with_streaks[item]}")


# Interactive helper
def habit_delete_int():
    """ Interactive delete for habit and it's events """
    try:
        habit_id = ask("Enter the id of the habit,"
                       "that you want to delete", r"^\d{1,8}$")
    except exception_inputs:
        return
    habit_delete(habit_id)


def cat_delete_int():
    """ Interactive delete for habit category"""
    try:
        cat_id = ask("Please input the category id of the object"
                     " you want to delete", r"^\d{1,8}$")
    except exception_inputs:
        return

    cat_delete(cat_id)


def habit_today():
    """" print today's habits """
    habits = session.query(models.Habit, models.HabitCategory).filter(
        models.Habit.weekday != 0,
        models.Habit.enabled).join(
        models.HabitCategory,
        models.Habit.cat_id == models.HabitCategory.cat_id,
        isouter=True)

    now = datetime.date.today()
    print("\tToday's list")
    print("\tID\tHabit name\tStreak\tCategory")
    for row in habits:
        hab = row[0]
        cat = row[1]
        if hab.due_today():
            if hab.is_weekly():
                # for a weekly habit, try to get an event
                # for start and end of the week
                weekday_today = datetime.datetime.today().weekday()
                today = datetime.datetime.today()
                sweek = (today - datetime.timedelta(days=weekday_today % 7)).date()
                eweek = (today - datetime.timedelta(days=weekday_today - 6 % 7)).date()

                habit_events = session.query(models.HabitEvent).filter(
                    models.HabitEvent.habit_id == hab.habit_id,
                    models.HabitEvent.datetime_solved >= str(sweek),
                    models.HabitEvent.datetime_solved <= str(eweek)).all()
            else:
                habit_events = session.query(models.HabitEvent).filter(
                    models.HabitEvent.habit_id == hab.habit_id,
                    models.HabitEvent.datetime_solved == now).all()
            try:
                habit_event = habit_events[0]
                print(habit_event.get_status(), end="")
            except IndexError:
                print("Open", end="")
            print_habit_row_simple(hab, cat)


def print_habit_row_status(hab):
    """" print one habit record with enabled-information ia simplified way"""
    print(f"\t{hab.habit_id}\t{hab.name}\t{hab.enabled}")


def print_habit_row_simple(hab, cat):
    """" print one habit record in a simplified way"""

    # print habits name and identification
    print(f"\t{hab.habit_id}\t{hab.name}\t{hab.latest_streak}", end=" ")

    if cat is not None:
        print(f"\t{cat.cat_name}")
    else:
        print("\t")


def print_habit_row_weekly(hab):
    """" print one habit record with scheduling information """

    print(f"\t{hab.habit_id}\t{hab.name}", end=" ")

    # If weekly. print and return
    if hab.is_weekly():
        print("( Weekly )", end="\n")
        return

    # loop all weekdays, from 0 (Monday) to maximum 6 (Sunday)
    print("( ", end="")
    for i in range(0, 7):
        if hab.weekday & (1 << i):
            # print out the Weekday abbreviation
            print(f"{calendar.day_abbr[i]}", end=" ")
    print(end=")\n")


def print_habit_row(hab):
    """" print one habit record """

    # print habits name and identification
    print(f"\t{hab.habit_id}\t{hab.name}\t{hab.enabled}\t", end=" ")

    if hab.condition != "":
        # print the condition function
        print(f"({hab.condition},{hab.quota} "
              f"{hab.unit})")
    else:
        # print latest streak
        print("Check off only")


def resolve_habit_event(habit, event):
    """ Resolve a habit with an existing event """

    # Does the habit have a condition? Then run the condition dialog
    if habit.needs_satisfaction():
        print(habit.get_satisfaction())
        try:
            user_quota = ask(f"Please input the quota for {habit.unit} on "
                             f"that day, that you have reached, n for "
                             f"abort", r"(\d{1,8}|n)")
        except exception_inputs:
            session.rollback()
            return

        if user_quota == "n":
            session.rollback()
            return

        status = habit.satisfied(int(user_quota))
        event.set_quota(int(user_quota))
        event.set_status(status)
    else:
        try:
            question = ask(f"Did you do {habit.name} on "
                           f"{event.datetime_solved}?", r"(y|n)")
        except exception_inputs:
            session.rollback()
            return
        if question == "y":
            event.set_status_success()
        else:
            event.set_status_fail()
        event.set_quota(0)

    # Check status
    if event.get_status() == "Done":
        print("Oh Great, than we are booking this event as SUCCESS!")
    else:
        print("Oh well, seems you did not reach the target!")

    # Set Quota, will be set to 0 for non condition-tracking habits
    eday = datetime.datetime.strptime(
        event.datetime_solved, "%Y-%m-%d").date()
    event.set_weekday(eday.weekday())

    # Save HabitEvent?
    try:
        save = ask(f"Mark this state - {event.get_status()} - for the "
                   f"{event.datetime_solved} as final?", r"(y|n)")
    except exception_inputs:
        session.rollback()
        return

    if save == "y":
        session.add(event)
        session.commit()
    else:
        session.rollback()


def check_open_events(habit_id):
    """
    Checks a habit for open events (missed trials)
    and give the user a list to work on
    """

    # Pull the habit and pending / open events
    # events with status == 0
    habit = session.query(models.Habit).get(habit_id)
    events = session.query(models.HabitEvent).filter(
        models.HabitEvent.habit_id == habit_id,
        models.HabitEvent.status == 0).all()

    # If we have some open events, print them
    if len(events) > 0:
        print(f"{len(events)} open or unresolved events.")
    else:
        print("No open events anymore, all events are marked as final.")
        return

    # loop open events and give the user a chance to resolve them
    # event by event
    for event in events:
        print(f"Resolving event {event.event_id} on {event.datetime_solved}")
        # Call resolver
        resolve_habit_event(habit, event)


def habit_toggle_status():
    """ Toggles en/disable for a habit  """

    try:
        question = ask("Please input the id for the habit, "
                       "that you want to toggle",
                       r"^\d{1,8}$")
    except exception_inputs:
        return

    # Get that single habit
    habit = session.query(models.Habit).get(question)

    # If the habit is not found, we return
    if habit is None:
        print("This habit does not exist.")
        return

    # Need adjust the update date, so future open event calls from
    # persistence() will work, else persistence() will add events from the past
    habit.set_updated(datetime.date.today())
    if habit.enabled:
        habit.disable()
        print(f"Disabled {habit.name}")
    else:
        habit.enable()
        print(f"Enabled {habit.name}")

    session.add(habit)
    session.commit()


# Check off habit
def habit_info():
    """ Prints all info about a habit  """

    # Get habit id
    try:
        habit_id = ask("Please input the id for the specific habit",
                       r"^\d{1,8}$")
    except exception_inputs:
        return

    # Try to get a habit
    habit = session.query(models.Habit).get(habit_id)
    # No habit, no cry ...
    if habit is None:
        return

    # Print habit infos
    print(f"Name: {habit.name}\tID: {habit.habit_id}"
          f"\tEnabled: {habit.enabled}")
    if habit.condition != "":
        print(f"Condition: {habit.condition}: {habit.quota} {habit.unit}")
    print(f"Created: {habit.created}, Last Updated: {habit.updated}")
    print("Scheduler: ", end="")

    # If weekly. print and return
    if habit.is_weekly():
        print("Weekly")

    # for all weekdays, ... check if it would be due, then get the
    # weekday name
    for i in range(0, 7):
        if habit.weekday & (1 << i):
            # print out the Weekday abbreviation
            print(f"{calendar.day_abbr[i]}", end=" ")
    print(end="\n")

    # Get events with this particular habit id
    events = session.query(models.HabitEvent).filter(
        models.HabitEvent.habit_id == habit_id).all()

    print("\tHabit Events\n\tEvent\tStatus\tQuota\tSolved\tWeekday")
    for event in events:
        print_habitevent_row(event)
        print()


def print_habitevent_row(event):
    """ prints a habitevent row """

    print(f"\t{event.event_id}\t"
          f"{event.get_status()}\t{event.quota}"
          f"\t{event.datetime_solved}"
          f"\t{calendar.day_abbr[event.weekday]}", end="")


# Check off habit
def habit_checkoff():
    """ Checks off a habit interactive """

    # Get calling date
    now = datetime.date.today()

    # Get habit id
    try:
        habit_id = ask("Please input the id for the habit,"
                       "that you want to checkoff", r"^\d{1,8}$")
    except exception_inputs:
        return

    # Try to get the habit from the db layer
    habit = session.query(models.Habit).get(habit_id)

    # No habit, no cry ...
    if habit is None:
        print("This habit does not exist")
        return

    # If the habit is not weekly and not due today
    # at least, check for any open events
    if not habit.is_weekly() and not habit.due_today():
        # Lets check for any other open event
        check_open_events(habit.habit_id)
        # Recalculate streaks if necessary
        recalculate_streak(session, habit.habit_id)
        # exit early, nothing to do
        return

    # At this point, left are weekly habit
    # and daily habits, that are due

    # For a daily habit, that is now due heck if was checked off today
    if not habit.is_weekly():
        habit_events = session.query(models.HabitEvent).filter(
            models.HabitEvent.habit_id == habit_id,
            models.HabitEvent.datetime_solved == now).all()
    # For a weekly habit, we need to generate the current week
    # and then check for an open event in this time period
    elif habit.is_weekly():
        weekday_today = datetime.datetime.today().weekday()
        today = datetime.datetime.today()
        sweek = (today - datetime.timedelta(days=weekday_today % 7)).date()
        eweek = (today - datetime.timedelta(days=weekday_today - 6 % 7)).date()

        # Try to pull the events
        habit_events = session.query(models.HabitEvent).filter(
            models.HabitEvent.habit_id == habit.habit_id,
            models.HabitEvent.datetime_solved >= str(sweek),
            models.HabitEvent.datetime_solved <= str(eweek)).all()

    # Is there already an event stored for this habit for today,
    # that is open and need be resolved?
    if len(habit_events) > 0:
        habit_event = habit_events[0]
        print(f"Changes will update the current event "
              f"{habit_event.event_id}  with status "
              f"{habit_event.get_status()}.")
    else:
        # Ok, then we need to create a new habit event
        habit_event = None

    # Create new base habit event with the current datetime
    # or update current event
    try:
        habitevent_create_mod_base(habit, now, habit_event)
    except exception_inputs:
        return

    # Lets check for any other open event
    check_open_events(habit.habit_id)
    recalculate_streak(session, habit.habit_id)


# Event List
def event_list():
    """" prints all recent events """

    print("\tHabit Events\n\tEvent\tStatus\tQuota\tSolved\tWeekday\tHabit")
    results = session.query(models.Habit, models.HabitEvent). \
        join(models.HabitEvent).filter().all()
    for row in results:
        print_habitevent_row(row.HabitEvent)
        print(f"\t{row.Habit.name}({row.HabitEvent.habit_id})", end="\n")


# Habit List
def habit_list():
    """ Prints out a list of all habits """

    habits = session.query(models.Habit).filter().all()
    print("\tAll habits\n\tID\tName\tEnabled\tCondition")

    for hab in habits:
        print_habit_row(hab)


# Habit streak list
def habit_streak_list():
    """ Prints out a list of all habits """
    habits = session.query(models.Habit).filter().all()
    print("\tStreak list\n\tCurrent\tLongest\tName")
    for hab in habits:
        print(f"\t{hab.latest_streak}"
              f"\t{get_longest_streak_for_habit(hab.habit_id)}"
              f"\t{hab.name}({hab.habit_id})")


# Cat list
def cat_list():
    """ Prints out a list of all categories """
    cats = session.query(models.HabitCategory).filter().all()
    print("\tAll categories\n\tID\t\tName")
    for cat in cats:
        print(f"\t{cat.cat_id}\t\t{cat.cat_name}")


# Modify habit
def habit_modify():
    """ Interactive habit rename """
    try:
        hab_id = ask("Please input the id for the habit,"
                     "that you want to modify", r"^\d{1,8}$")
    except exception_inputs:
        return

    habit = session.query(models.Habit).get(hab_id)
    if habit is None:
        return

    habit_name = ask("Please input a new name", r"^[\w{1,256\s]+$")
    habit.set_name(habit_name)

    try:
        question = ask("Do you want to put this habit into a category?",
                       r"(y|n)")
    except exception_inputs:
        session.rollback()
        return

    if question == "y":
        cat_list()
        try:
            cat_id = ask("Please input the category id", r"^\d{1,8}$")
        except exception_inputs:
            session.rollback()
            return

        cat = session.query(models.HabitCategory).get(cat_id)
        if cat is not None:
            habit.cat_id = question

    print(habit)
    try:
        save = ask('Do you want to save the modifications now?',
                   r"(y|n)")
    except exception_inputs:
        session.rollback()
        return

    if save == "y":
        session.add(habit)
        session.commit()
    else:
        session.rollback()


def cat_modify():
    """" interactively rename a category """

    # Ask friendly for the current id of the category
    try:
        cat_id = ask("Please input the id for the category, "
                     "that you want to rename", r"^\d{1,8}$")
    except exception_inputs:
        return

    cat = session.query(models.HabitCategory).get(cat_id)
    if cat is None:
        return

    # Ask for a new name
    try:
        cat_name = ask("Please input a new name", r"^\w{1,256}")
    except exception_inputs:
        return

    # Set the new name
    cat.set_name(cat_name)

    # And commit the category back to the database
    session.add(cat)
    session.commit()


def cat_create():
    """" interactively create a category """

    # ask for a nice name
    try:
        keyword_arguments = (ask_many("category",
                                      [r'cat_name;string;^[\w{1,256\s]+$']))
    except exception_inputs:
        session.rollback()
        return

    # create a new habit object by using
    # the sqlalchemy constructor with keywords
    cat = models.HabitCategory(**keyword_arguments)

    # Commit / create
    session.add(cat)
    session.commit()


def habitevent_create_mod_base(habit, now, habit_event):
    """ creates or modifies an event for a habit """

    # Create a new instance or use existing habit_event
    if habit_event is None:
        habit_event = models.HabitEvent(habit_id=habit.habit_id,
                                        datetime=str(now))
        habit_event.set_solved(str(now))

    # Call resolver
    resolve_habit_event(habit, habit_event)


def habit_create_base():
    """ Creates a new habit with scheduling information """

    print("Ok, let's create a new habit together!")

    # by default, habit tracking is done with condition and value tracking
    condition_tracking = ask("Would you like to track exact values for the"
                             "new habit\n and make success dependent on "
                             "the values achieved?", r"(y|n)")

    # Default values
    values = [r'name;string;^[\w{1,256\s]+$']

    # if we need to track condition, we need more user inputs
    if condition_tracking == 'y':
        values = [r'name;string;^[\w{1,256\s]+$', r'condition;string;^(eq|lt|gt)$',
                  r'quota;integer;^\d{1,8}$',
                  r'unit;string;^\w{1,256}$']

    keyword_arguments = ask_many("habit", values)

    # create a new habit object by using
    # the sqlalchemy constructor with keywords
    hab = models.Habit(**keyword_arguments)

    print("Now let's find the appropriate days of the week for the habit in "
          "your calendar.")

    # Additional questions for scheduling habits
    question = ask("Do you want to work on this habit\n"
                   "(w)eekly once on any day, or on \n"
                   "(s)pecific days like a single day?", r"(w|s)")

    if question == "s":
        question = ask("Ok, let us find the right days of the week.\n"
                       "Do you wan to to run the habit on a\n"
                       "(s)ubset of week days (like Monday, Wednesday) or on\n"
                       "(e)very day of the week?", r"(s|e)")

        if question == "s":
            week_input = ask("Please input the weekdays that you want to work "
                             "on the habit.\n"
                             "0 (Monday) to 6 (Sunday), you can input several "
                             "weekdays in a comma-separated "
                             "list (0,1,3) or as String "
                             "(Monday,Tuesday,...)\n",
                             r"([0-6]|"
                             r"(Monday|Tuesday|Wednesday|"
                             r"Thursday|Friday|Saturday|Sunday)),?")

            # Get the weekdays and add them to the habit set
            for day in week_input.replace(" ", "").split(","):
                hab.add_day(day)

        elif question == "e":
            # Add a full week set by ranging from 0 to 7
            for i in range(0, 7):
                hab.add_day(i)
    # set weekly
    else:
        hab.set_weekly()

    return hab


def habit_create():
    """" interactively create a habit """

    # Create a base habit with scheduling information
    try:
        hab = habit_create_base()
    except exception_inputs:
        return

    # Find a category (if any)
    try:
        question = ask("Do you want to put this habit into a category?",
                       r"(y|n)")
    except exception_inputs:
        return

    # print out the category list, when answer is y
    if question == "y":
        cat_list()

        # As long as the habit category was not given, ask
        satisfied = False
        while not satisfied:
            try:
                cat_id = ask("Please input the category id", r"^\d{1,8}$")
            except exception_inputs:
                return

            # Try to search for a category
            habit_category = session.query(models.HabitCategory).get(cat_id)
            if habit_category is not None:
                hab.cat_id = cat_id
                satisfied = True
            else:
                print("Category does not exist, try again")

    # print out the habit
    print(hab)
    try:
        save = ask('Do you want to save and track this habit now?',
                   r"(y|n)")
    except exception_inputs:
        session.rollback()
        return

    # Rollback, when save is denied
    if save == "n":
        session.rollback()
        return

    # Commit explicit
    hab.set_created()
    session.add(hab)
    session.commit()


def recalculate_streak(sqlsession, habit_id):
    """ recalculates streak of a habit by evaluating events """
    habit = sqlsession.query(models.Habit).get(habit_id)
    # pull all events
    habit_events = sqlsession.query(models.HabitEvent). \
        order_by(models.HabitEvent.datetime_solved).filter(
        models.HabitEvent.habit_id == habit_id).all()

    streak = 0
    for event in habit_events:
        status = event.get_status()
        if status in ("Failed", "Pending"):
            streak = 0
        else:
            streak += 1

    habit.update_streak(streak)
    sqlsession.commit()


def get_longest_streak_for_habit(habit_id):
    """ get longest streak of a habit by evaluating events """

    # pull all events
    habit_events = session.query(models.HabitEvent). \
        order_by(models.HabitEvent.datetime_solved).filter(
        models.HabitEvent.habit_id == habit_id).all()

    # set starting streaks all to 0
    streak = 0
    longest_streak = 0
    for event in habit_events:
        status = event.get_status()
        if status in ("Failed", "Pending"):
            streak = 0
        else:
            streak += 1
        # only if streak is larger that the longest ever, do a replacement
        if streak > longest_streak:
            longest_streak = streak

    return longest_streak


def persistence():
    """ Starts at every program run to catch missed habit events
        For example, when called on Friday, this code will take care
        that missing events from Monday till at least Thursday are being
        placed in the habit event queue as missing

        Returns a list of events generated, so called
        startup-messages
    """
    startup_messages = []
    today = datetime.datetime.today().date()

    # Get all weekly habits
    habits = session.query(models.Habit).filter(models.Habit.weekday == 128,
                                                models.Habit.enabled).all()

    # Weekly habits calculator
    for hab in habits:
        # Just triple check :-)
        if not hab.is_weekly():
            continue

        need_calc = False
        # Get start date
        start = datetime.datetime.strptime(hab.updated, "%Y-%m-%d").date()
        # calculate s_week (start day of week)
        # and e_week (end day of a week)
        # relative from updated column
        s_week = start - datetime.timedelta(days=start.weekday() % 7)
        e_week = start - datetime.timedelta(days=start.weekday() - 6 % 7)
        hab.set_updated(datetime.datetime.today().date())

        # As long as the s_week is smaller the e_week
        # and also the s_week is smaller than today,
        # continue to look for missed events
        while s_week < e_week and s_week < today:

            # Get all habit events in this particular week
            habit_events = session.query(models.HabitEvent).filter(
                models.HabitEvent.habit_id == hab.habit_id,
                models.HabitEvent.datetime_solved >= str(s_week),
                models.HabitEvent.datetime_solved <= str(e_week)).all()

            # No event? Then add a missing event
            # IF today is not the start of the week
            if len(habit_events) == 0 and s_week != today:
                habit_event = models.HabitEvent(habit_id=hab.habit_id,
                                                datetime=start,
                                                datetime_solved=s_week,
                                                weekday=start.weekday())
                # Add object to session and commit
                session.add(habit_event)
                session.commit()
                # add Message to startup buffer
                startup_messages.append(f"You missed {hab.name} "
                                        f"from {s_week} to {e_week},"
                                        f"please check(o)ff {hab.habit_id}")
                need_calc = True

            # Update habit to reflect new end date
            session.add(hab)
            session.commit()

            # shift start for at least 7 days
            s_week = s_week + datetime.timedelta(days=7)
            # recalculate end_of_the_week for next loop step
            e_week = s_week - datetime.timedelta(days=start.weekday() - 6 % 7)

        # recalculate habit
        if need_calc:
            recalculate_streak(session, hab.habit_id)

    # Daily habits calculator
    # Get all enabled habits
    habits = session.query(models.Habit).filter(models.Habit.weekday != 0,
                                                models.Habit.weekday != 128,
                                                models.Habit.enabled).all()
    for hab in habits:
        # Just double check :-)
        if hab.is_weekly():
            continue

        need_calc = False
        start = datetime.datetime.strptime(hab.updated, "%Y-%m-%d").date()
        end = datetime.datetime.today().date()
        hab.set_updated(end)

        while start < end:
            # if the habit is not to be done on this weekday, ignore that day
            if not hab.due_weekday(start.weekday()):
                start = start + datetime.timedelta(days=1)
                continue

            # Check all habits in an easy loop
            # 1.) check if there is a habit event for that specific day
            # 2.) if not, create it
            # so, pull all events
            habit_events = session.query(models.HabitEvent).filter(
                models.HabitEvent.habit_id == hab.habit_id,
                models.HabitEvent.datetime_solved == start).all()

            # check size of habit events vs today's date
            if len(habit_events) == 0 and start != today:
                habit_event = models.HabitEvent(habit_id=hab.habit_id,
                                                datetime=start,
                                                datetime_solved=start,
                                                weekday=start.weekday())
                # Add object to session and commit
                session.add(habit_event)
                session.commit()
                # add Message to startup buffer
                startup_messages.append(f"You missed {hab.name} "
                                        f"on {start}, please run check(o)ff"
                                        f" {hab.habit_id}")
                need_calc = True

            # Update habit to reflect new end date
            session.add(hab)
            session.commit()

            # continue adding a day to the start
            # to advance loop to the next day
            start = start + datetime.timedelta(days=1)

        # recalculate habit, when changes were detected
        if need_calc:
            recalculate_streak(session, hab.habit_id)

    return startup_messages


# Create engine & session
if __name__ == "__main__":
    # Create connection to sqlite database
    engine = create_engine('sqlite:///habit.sqlite3', echo=False)
    Session = sessionmaker(bind=engine)

    # Create all missing tables if necessary
    base.Base.metadata.create_all(engine)
    session = Session()

    # Check open and missed events
    startup = persistence()

    # init the menu
    clm = CliMenu(
        header="\thaha-Bits 0.1",
        menus={
            # define a main menu with h and g leading to submenus
            # strings => move to submenus
            # function pointers / callbacks => call a function,
            # that can be defined by user
            "main": [
                ["(T)oday's habits", "Check(o)ff",
                 "(C)reate new", "(H)abits menu",
                 "Cate(g)ory menu", "(A)nalytics", "E(x)it"],
                {"t": habit_today, "o": habit_checkoff, "c": habit_create,
                 "h": "habs", "g": "cats", "a": "analytics",
                 "hl": habit_list, "cl": cat_list},
            ],
            "habs": [
                ["(L)ist all", "(I)nfo",
                 "Check(o)ff",
                 "(C)reate new", "(D)elete",
                 "(M)odify", "E(v)ent list",
                 "(T)oggle Enable/Disable",
                 "(R)eset event",
                 "E(x)it To Top"],
                {"l": habit_list, "o": habit_checkoff, "c": habit_create,
                 "d": habit_delete_int, "t": habit_toggle_status,
                 "m": habit_modify, "v": event_list,
                 "r": reset_event, "i": habit_info}
            ],
            "analytics": [
                ["(L)ist all tracked habits",
                 "(R)eturn Habits by the scheduler",
                 "Return longe(s)t streaks",
                 "Longest Streak of a hab(i)t",
                 "(A)verage calculation of quotas",
                 "E(x)it To Top"],
                {"l": habit_list_ay, "s": longest_streak_all_int,
                 "i": longest_streak_int,
                 "r": habit_scheduler_list, "a": habit_average,
                 }
            ],
            "cats": [
                ["(L)ist all categories", "(C)reate new category",
                 "(D)elete category",
                 "(M)odify category name", "E(X)it to Top"],
                {"c": cat_create, "l": cat_list,
                 "d": cat_delete_int,
                 "m": cat_modify},
            ]},
    )

    # Start the menu loop
    clm.run(startup)
    # Add close the stargate
    session.close()

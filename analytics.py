"""" Analytics functions """


def get_habits(habits):
    """ get all enabled habits the functional way """
    return list(filter(lambda x: x.enabled, habits))


def get_habits_weekday(habits, weekday):
    """ get habits the functional way within a certain weekday """
    return list(filter(lambda x: x.enabled and x.due_weekday(weekday), habits))


def get_lstreaks_single(streak):
    """ get longest streak of a habit by evaluating the functional way """

    # Replace pending with failed
    streak_normalized = "".join(
        list(map(lambda x: x if x in ('2', '1') else "2", streak)))

    # Get the maximum number from ...
    return max(
        # mapping the len values
        map(
            # of the len function, from splitting the string
            # by the 0 (11001 => 11,1) => (2,1) => 2
            len, streak_normalized.split("2"))
    )


def get_lstreaks_all(habits, events):
    """ get all longest streaks for all habits """

    # Helping function
    def streakhelper(habit):
        # return a string of all habit events
        # containing 1s (success) or 2s (failed)
        return (
            # Concat all strings together to get the string
            # e.g. "1122221112121"
            "".join(map(str, map(
                # if status is 1 or 2, pass it as it is
                # and if an event is pending, mark it also as 2 (failed)
                lambda x: x.status if x.status in (1, 2) else 2, (
                    filter(
                        # Filter events containing our habit id
                        lambda x: habit.habit_id == x.habit_id, events))))))

    # Then return a dictionary of habit object
    return (
        # Dictionary with object as key
        dict(map(lambda x: (x,
                            # Calculating the max value of mapping
                            max(map(
                                # the single splits from the streak - function
                                len, streakhelper(x).split("2")))), habits)))


def get_calculate_avg(events):
    """ Calculates the average quota of a habit """
    return sum(map(lambda x: x.quota, events)) / len(events)

## haha-bits
haha-bits is a small CLI-based habit tracking application in Python. 

### How to install

#### 1.) Clone the source code 
    git clone https://github.com/ipcjk/hahabits

#### 2.) Install python3-interpreter, pip and venv for your local OS
    
    # For example, Ubuntu and Debian:
    apt-get install python3.8-venv python3.8 python3-pip

#### 3.) Activate a virtual environment
    cd hahabits 
    python3 -m venv env
    . env/bin/activate

#### 4.) Install requirements with pip
    pip install -r requirements.txt

#### 5.) Test the installation
    pytest -v

#### 6.) Remove test - database
The application is packed with a test database containing pre-defined
habits and events. If you want to start your fresh copy, remove the 
SQLite-database file. On startup, the application will create a new, clean database. For example, on *nix OS:

    # On Linux, BSD: 
    rm habit.sqlite3

#### 7.) Run the installation
    ./app.py

or

    python3 app.py

### How to use haha-bits 


Haba-bits is menu-driven, so you can quickly start along. Commands and menu
switches are given by typing and entering keystrokes, which are shown in the braces
of the menu output.

For example, to create  your first habit, fire up the application, then type in the "C"-button and push
"Enter". Haha-bits will ask you a few questions about this habit, like the name and tracking 
this in detail. Afterward, the habit is committed to the database, and the journey begins.

You can then start to fulfill the habit and check it off by entering
the "o"-button and then give the unique habit identification number, that you can see
in the habit-list of today or the general overview.

Haha-Bits is designed with the main menu, including three submenus. Submenus can be called by entering certain 
keystrokes. The keystrokes in action are shown between the round braces.

Submenus exist for more additional functions: Habits, Category, Analytics. All of them are 
explained later in this document.

Menus and the main application can be left by typing the "x"-character. Input can be stopped in almost any dialog 
by hitting the CTRL+C keys together. Entering "?" will print the current menu again.

Below is the explanation of the main menu, the habits menu, and a few short sentences about the others. 

### main menu ###

     --- main ---
        1. (T)oday's habits
        2. Check(o)ff
        3. (C)reate new
        4. (H)abits menu
        5. Cate(g)ory menu
        6. (A)nalytics
        7. E(x)it


##### 1.) Today's habits #####

The "t"-keystroke will present you with a list of weekly and daily habits that need to be done today.  
The habit status will be shown as "Open," "Done" when you successfully did the habit, and "Failed" when you 
did not reach the goal.

    
        >t
       Today's list 
           ID  Habit name         Streak Category 
    Open   5  Reading to kids        0  Family

##### 2.) Checkoff habit ##### 

With the button "o" and the checkoff function, you can run a  dialog, asking you
specific particular question to resolve and check off the open habit.
    
    >o
    Please input the id for the habit, that you want to checkoff>5
    Please input the books, that you have reached>3
    Do you want to check off this habit? (y,n)>y

The application will alert you when you try to check off the same habit again:
    
    >Seems you have checked off this habit for  2022-01-18
    Changes will update the current event

Also, "o" will run a resolver and will let present you with an open list of
passed or missed events for that habit - if any.

##### 3.) Create a new habit #####

The "c"-input will lead you to the creation dialog of a habit. Here you can enter details like the name or the weekdays 
planned for practice.

If you want to track the habit with a conditioning tracker and collect data like 
the amount of something (pushups, reading book, others), you are optional to go. You need to answer
with "y" to the "condition/quantification" - question for tracking. The program then will ask you 
additional details like the function to apply, the amount, and the unit name for pretty displaying. 
Please also note the expected input format inside the questionnaire braces, which gives you a hint about the proper, 
expected input. Proper formats are:

string:^\w{1,256} => A string with at least 1 to 256 characters

integer:^\d{1,8} => An integer with at least 1 to 8 digits

string:^(eq|lt|gt) => One of the condition functions: eq,lt,gt

As an example, if you want to make at least 20 pushups on Wednesday and Friday, the dialog could 
look a bit like this. 

Create a habit with a condition 

    >c
    Track this habit with a condition / quantification (y|n)? >y

Enter a pretty name 

    Enter a value for name (string:^\w{1,256}$)
    habit name>Pushups

Enter the condition, here "gt", greater or equal 

    Enter a value for condition (string:^(eq|lt|gt)$)
    habit condition>gt

The value or quota that would be an acceptable target amount.

    Enter a value for quota (integer:^\d{1,8}$)
    habit quota>50

A unit name
    Enter a value for unit (string:^\w{1,256}$)
    habit unit>number

The scheduling information for this habit as a comma-separated list with weekdays or weekday names:

    Do you want to work on this habit on (w)eekly or on specific days (d)aily?)>d
    Please input the weekdays that you want to work on the habit.
    0 (Monday) to 6 (Sunday), you can input several weekdays in a comma-separated list (0,1,3) or as 
    String (Monday, Tuesday, ...)>Wednesday, Friday
    Do you want to put this habit into a category?>n
    Name: Pushups Weekly: 20
    Condition: gt Quota / Units:50 number

The conditional function - if used -uses three conditions to mark a one time
execution of a habit with conditions as successful.

###### Condition functions ######
eq => Habit was done, and repeated exactly $n-times. As an example, made exactly 50 pushups on Wednesday

lt => Number of practice needs to be under or equal to a given value

gt => Number of practice needs to equal or greater a given value

##### 4.) Habits Sub #####

See Habits Submenu point.

##### 5.) Category Sub #####

See Category Submenu point.

##### 6.) Analytics Sub #####

See Analytics Submenu point.

##### 7.) E(x)it #####
Leading to the program's exit


### habs submenu ###

        --- habs ---
        1. (L)ist all
        2. (I)nfo
        3. Check(o)ff
        4. (C)reate new
        5. (D)elete
        6. (M)odify
        7. E(v)ent list
        8. (T)oggle Enable/Disable
        9. (R)eset event
        10. E(x)it To Top


Inside the habs menu, you have different possibilities to work and
manipulate habits. Let's have a quick introduction for every point:

##### 4.) (L)ist all habits #####

This will list all habits with their current
status and the condition function.

     >L
        All habits
        ID      Name    Enabled Condition

        1       Running True     Check off only
        2       Walking around  False    Check off only
        3       Study Math      True     Check off only
        4       Playing pool    True     (eq,5 rounds)
        5       Reading to kids True     (gt,3 books)
        6       Pushups True     (gt,50 number)

#####   2. (I)nfo about a specific habit ######

This function will show all available information for a particular
habit. It will also list the scheduling information and the
last events of a habit.

    >i
    Please input the id for the specific habit>1
    Name: Running   ID: 1   Enabled: True
    Created: None, Last Updated: 2022-01-31
    Scheduler: Wed Sat 
        Habit Events
        Event   Status  Quota   Solved  Weekday
        1       Failed  0       2022-01-01      Sat
        2       Done    0       2022-01-05      Wed
        3       Done    0       2022-01-08      Sat
        4       Done    0       2022-01-12      Wed


##### 3. Check(o)ff  #####

This will run the checkoff dialog similar to the one from the 
main function point.

##### 4. (C)reate new #####

This will run the creation dialog from the primary function.

##### 5. (D)elete  #####

Under point 5, you can delete an existing habit. It will also delete any
written events.

##### 6. (M)odify #####

The modification function is there to rename a habit.

##### 7. E(v)ent list #####

Menu point 7 will print out the last known events for all habits.

##### 8. (T)oggle Enable/Disable #####

The toggle function enables or disables a habit. It can be useful for a kind of vacation function or if you are unable to make certain habits in a known
time-period.

##### 9. (R)eset event #####

Sometimes you might reset a particular event. The reason could be that
you supplied a wrong quota or wrongfully marked the event as failed when 
you succeeded. With the reset event function, you can reset a
specific event of a habit to the open/pending state.

To identify a specific event, you first call up the info function. Here 
you will find different event numbers for the respective habit. You write 
down or remember the event numbers that you want to customize. Then you 
call "Reset event" and enter the event ID in the dialog. You have 
now reset the event. To process the event again, run checkoff with the 
habit identification umber. The checkoff function will find the open event and go through the completion 
dialog with you. Let's take a look at this example. I want to reset
one event for the habit "Reading to kids" with the id "5":

        >i
        Please input the id for the specific habit ^\d{1,8}$>5
        Name: Reading to kids   ID: 5   Enabled: True
        Condition: gt: 3 books
        Created: None, Last Updated: 2022-01-27
        Scheduler: Weekly

        Habit Events
        Event   Status  Quota   Solved  Weekday
        55      Failed  1       2022-01-06      Thu
        56      Failed  2       2022-01-13      Thu
        57      Done    3       2022-01-19      Wed
        58      Done    444     2022-01-24      Mon
        59      Done    4       2022-01-31      Mon

From this list, I reset the event from 2022-01-06, with the event number 55:

    >r
    Enter the id of the event,to set this event to a pending/open state  ^\d{1,8}$>55
    Event reset, please run check(o)ff 5 to resolve the issue

Now I need to run the checkoff function to resolve that event. It will start the already known dialog:

    >o
    Please input the id for the habit,that you want to checkoff ^\d{1,8}$>5
    1 open or unresolved events
    Resolving event 55 on 2022-01-06
    Please input the quota for books on that day, that you have reached, n for abort (\d{1,8}|n)>


##### 10. E(x)it to Top  #####

Exits to the main menu.


### Categories submenu ###

        --- cats ---
        1. (L)ist all categories
        2. (C)reate new category
        3. (D)elete category
        4. (M)odify category name
        5. E(X)it to Top

The categories submenu is self-explanatory after learning the other menus. There is no new functionality. 
A habit can be tagged with a category. It is a display-only function currently. Deleting a category won't delete
any habit associated with it.

### Analytics ####

        --- analytics ---
        1. (L)ist all tracked habits
        2. (R)eturn Habits by the scheduler
        3. Return longe(s)t streaks of all habits
        4. Longest Streak of a hab(i)t
        5. (A)verage calculation of a habit quota
        6. E(x)it to Top Menu

You can run several statistics on all or single habits from the analytics menu. 

## License
MIT © 2022 Jörg Kost 

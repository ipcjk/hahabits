""" Climenu is a class for running a main menu with submenus, by giving
a structure with text, hotkeys and callable functions as parameter
"""
import re


class CliMenu:
    """ Class for running a menu """

    def __init__(self, header="", menus=None):
        # Startup buffer (messages)
        # and current command tracker
        self.startup_buffer = []
        self.pcc = ""

        # current / starting menu
        # read and set the default menu
        # set header
        self.status = "main"
        self.header = header

        # set all menus
        self.menus = menus
        # contains the menu output itself
        self.displayed_menu = ""

        # set allowed input keys for current menu
        self.cur_valid = []

    def read_line(self):
        """ Reads a line and tries to map to valid input strings """

        # Add valid keys
        valid_commands = {i: True for i in self.cur_valid}

        # Add exit and help printer keys
        valid_commands["x"] = True
        valid_commands["?"] = True

        # parse user input by current status
        # Input shell
        while True:
            # lets read some input from the input
            try:
                input_token = input(">").strip().split()
            except (KeyboardInterrupt, EOFError):
                continue

            # Check length of token array
            if len(input_token) == 0:
                print("?=context menu, ctrl-c=abort inputs, x=exit")
                continue

            # lower makes everything easier in comparing
            input_token[0] = input_token[0].lower()

            # check input_token for valid command in the valid_commands dict
            if input_token[0] in valid_commands:
                # return command to menu caller
                return input_token[0]
                # example version, return other strings after the token
                # return input_token[0], input_token[1:]

            # return an error, but stay inside the input loop
            print("command not found, input ? for current menu level")

    def switch_menu(self):
        """ Runs the current menu and switches to different subs """

        # Checkout, which menu is running, print out and
        # wait for exact commands
        # Parse command depending on menu running
        # e.g. moving between menus or bailing out
        old_menu = self.displayed_menu

        # select displayed menu and validated keys
        self.displayed_menu = self.menus[self.status][0]
        self.cur_valid = self.menus[self.status][1]

        # print selected menu if menu has changed
        if self.displayed_menu != old_menu:
            self.print()

        # wait for input
        self.pcc = self.read_line()

        # check if the user tries to exit or want to jump to a top menu
        if self.pcc == "x":
            # exit, when the menu is in main mode and exit command was given
            if self.status == "main":
                return False

            # else, we are in a submenu and need jump back to status menu
            self.setstatus("main")
            # delete command from buffer
            self.pcc = ""
            return True
        if self.pcc == "?":
            # reprint the whole menu, when inputting the help key
            self.pcc = ""
            self.print()

        return True

    def setstatus(self, new_status):
        """ Sets the new menu or submenu """
        self.status = new_status

    def getstatus(self):
        """ Gets the current menu """
        return self.status

    def print(self):
        """ prints out the current menu """

        # start with printing the header
        self.top_header()

        # give menu components
        i = 1
        print(f"\t--- {self.status} ---")
        for line in self.displayed_menu:
            print(f"\t{i}. {line}")
            i += 1

        # if main menu, also print startup buffers
        if self.status == "main":
            if len(self.startup_buffer) > 0:
                print("\tStartup Alert:")
                for msg in self.startup_buffer:
                    print(msg)

    def run(self, startup):
        """ Run Loop, reads input, switches menus,
        tries to execute functions """
        self.startup_buffer = startup
        while True:
            # print current menu and read next input
            if not self.switch_menu():
                return

            command = self.pcc
            # empty command, for example by changing submenus?
            if command == "":
                continue

            # no status? better continue
            if self.status == "" or self.status not in self.menus:
                print("unknown menu_status")
                continue

            # Catch if the list inside the menu structure was not
            # 100% defined by the user, # e.g. no element at index 1
            try:
                self.menus[self.status][1]
            except IndexError:
                continue

            # Check, if a command or function pointer was not set
            if command not in self.menus[self.status][1]:
                continue

            # else act if we need load submenus, the type of object shall
            # be a string
            if isinstance(self.menus[self.status][1][command], str):
                self.setstatus(self.menus[self.status][1][command])
                continue

            # else act on command (if callable)
            if self.menus[self.status][1][command] is not None \
                    and callable(self.menus[self.status][1][command]):
                # run user-defined function call
                self.menus[self.status][1][command]()
                continue

    def top_header(self):
        """ prints the top header """
        print(self.header)


def ask(text, validation):
    """ Asks for "single" input """

    # Try to compile regular expression
    try:
        match_input = re.compile(validation)
    except re.error:
        print(f"Error in compiling regular expression {validation}")
        raise

    user_input = ""
    while not match_input.match(user_input):
        user_input = input(f"{text} {validation}>")

    return user_input


def ask_many(name, ikeys):
    """" Asks for "many" inputs, useful for init a object from a SQL class """

    members = {}
    for inputting in ikeys:
        inputs = str(inputting).split(";")

        # Try to access the third element
        try:
            inputs[2]
        except IndexError:
            print("Error in input validation strings")

        # Try to compile regular expression
        try:
            match_input = re.compile(inputs[2])
        except re.error:
            print(f"Error in compiling regular expression {inputs[2]}")
            raise

        # As long as the input condition is not satisfied by the regular
        # expression, dont move forward to next input
        satisfied = False
        while not satisfied:
            print(f"Enter a value for {inputs[0]} ({inputs[1]}:{inputs[2]})")

            # Catch the usually input errors and raise them to calling function
            user_input = input(name + " " + inputs[0] + ">")

            # When there is a format error, we can witness an
            # Index error sometimes
            if match_input.match(user_input):
                satisfied = True
                if inputs[1] == "integer":
                    members[inputs[0]] = int(user_input)
                else:
                    members[inputs[0]] = user_input
    return members

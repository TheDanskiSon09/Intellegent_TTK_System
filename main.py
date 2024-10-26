from hammett.core import Application
from hammett.core.constants import DEFAULT_STATE
from screens import *


def main():
    """Runs the bot."""

    name = 'TTK Assistant'
    app = Application(
        name,
        entry_point=MainMenu,
        states={
            DEFAULT_STATE: [MainMenu, SignUp, Login, BadRequest, Authorisation],
        },
    )
    app.run()


if __name__ == '__main__':
    main()

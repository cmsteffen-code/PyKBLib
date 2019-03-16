"""A Python library for interacting with the Keybase CLI tools."""


import subprocess


class Keybase:
    """Interfaces with the Keybase application.

    Atrributes
    ----------
    username : str
        The name of the user logged into Keybase.

    """

    def __init__(self):
        """Initialize the Keybase class."""
        self.username = get_username()


def get_username() -> str:
    """Get the name of the user currently logged in.

    Returns
    -------
    username : str
        The username of the currently active Keybase user.

    """
    # Run the command and retrieve the result.
    result = run_command("keybase status")
    # Extract the username from the result.
    username = result.split("\n")[0].split(":")[-1].strip()
    # Return the username.
    return username


def run_command(command_string: str):
    """Execute a console command and retrieve the result.

    This function will make three attempts to run the specified command. Each
    time it fails, it will attempt to restart the keybase daemon before making
    another attempt.

    Parameters
    ----------
    command_string : str
        The command to be executed.

    """
    attempts = 0
    while True:
        try:
            # Attempt to execute the specified command and retrieve the result.
            return subprocess.check_output(
                command_string,
                stderr=subprocess.STDOUT,
                shell=True,
                timeout=10,  # Raise an exception if this takes > 10 seconds.
            ).decode()
        except subprocess.TimeoutExpired:
            # When the call times out, check how many times it has failed.
            if attempts > 3:
                # If it's failed more than three times, raise the exception.
                raise
            # If it hasn't failed three times yet, restart they keybase daemon.
            subprocess.check_output("keybase ctl restart", shell=True)
            # Increment the number of attempts.
            attempts += 1

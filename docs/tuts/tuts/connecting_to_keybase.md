Connecting to Keybase
=====================
Creating an interface to your Keybase installation is simple. First, ensure that you've got the PyKBLib module installed using pip:

```
pip install pykblib
```

Next, in your source, import the `Keybase` class from the `pykblib` module, then create an instance of the `Keybase` class, like so:

```
from pykblib import Keybase

KB = Keybase()
```

It can take a short while for `Keybase` to be instantiated, as it's gathering information from the Keybase command-line interface. Once it's finished, you can use the `KB` variable to interact with Keybase.

The remaining tutorials will assume that you've already taken this step, and will refer to the `KB` variable with the assumption that it's been initialized as a `Keybase` object.

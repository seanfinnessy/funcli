from importlib.metadata import entry_points
from setuptools import setup, find_packages

# where name is the name for the script you want to create,
# the left hand side of : is the module that contains your function
# and the right hand side is the object you want to invoke (e.g. a function).
# name=module:entrypoint
setup(
    name='valcli',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'click',
        'requests',
        'pyautogui'
    ],
    entry_points='''
    [console_scripts]
    val=valcommands:valcommands
    '''
)

import sys
import pyshorteners

def shorten_url(url):
    s = pyshorteners.Shortener()
    short_url = s.tinyurl.short(url)
    return short_url

def get_code(authorize_url):
    sys.stderr.write("\x1b[2J\x1b[H")
    short_url = shorten_url(authorize_url)
    """Show authorization URL and return the code the user wrote."""
    message = "Check this link in your browser: " + short_url 
    sys.stderr.write("\n")
    sys.stderr.write("\n")
    sys.stderr.write("Youtube authentication required!\n")
    sys.stderr.write(message + "\n")
    try: input = raw_input #For Python2 compatability
    except NameError: 
        #For Python3 on Windows compatability
        try: from builtins import input as input 
        except ImportError: pass
    return input("Enter verification code: ")

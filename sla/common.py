#!/usr/bin/python

import os, re
import time

__debug = 1 and True or False;

def is_debug():
    return __debug;

def set_debug(flag):
    __debug = flag;

def printd(text, btime = True):
    if not is_debug():
        return;
    if (btime):
        print time.strftime("%H:%M:%S", time.localtime()) + ' | ' + str(text),;
    else:
        print text,;

if __name__ == '__main__':
    print("is_debug: %d"%is_debug());
    printd("Hello debug trace.\n", False);
    printd("Hello debug trace with timestamp.\n");

from postroj.util import cmd


def info():
    print(cmd("/usr/bin/hostnamectl"))

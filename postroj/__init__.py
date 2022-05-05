from postroj.util import hcmd


def info():
    hcmd("/usr/bin/hostnamectl")

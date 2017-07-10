import termios, fcntl, sys, os
fd = sys.stdin.fileno()

oldterm = termios.tcgetattr(fd)
newattr = termios.tcgetattr(fd)
newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
termios.tcsetattr(fd, termios.TCSANOW, newattr)

oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
truePos = 0
falsePos = 0
falseNeg = 0
noNo = 0
print "1 for if it detected something, 2 if it detected incorrectly, 3 if it didn't detect something that it should've, or 4 for nothing"
try:
    while 1:
        try:
            c = sys.stdin.read(1)
            c = str(repr(c))
            print c
            if c == "'1'":
                truePos += 1
                print "That was a true pos"
            elif c == "'2'":
                falsePos +=1
                print "That was a false pos"

            elif c == "'3'":
                falseNeg += 1
                print "That was a false neg"

            elif c == "'4'":
                noNo += 1
                print "That was a no no"

            elif c == "'q'":
                break
        except IOError: pass
finally:
    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

string = """
   |  Y  |  N  |
Y  |  """ + str(truePos) + """  |  """ + str(falseNeg) + """  |
N  |  """ + str(falsePos) + """  |  """ + str(noNo) + """  |


"""
print string

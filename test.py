import os
hell = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"] 
def check_pid(pid):        
    try:
        print("-------YOU MAY IGNORE THE BELOW ERROR/WARNING GIVEN-------")
        os.kill(pid,0)
    except OSError:
        return True
os.system('cmd /c tasklist /v /fo csv | findstr /i "hellofromwin64py" > pidchecker.txt')
file = open("pidchecker.txt")
pidfile = file.read()
 
pid = int(pidfile[14] + pidfile[15] + pidfile[16])
check_pid(pid)


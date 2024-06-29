from datetime import datetime
unix = (date := datetime.now()).timestamp()

hms = str(date).replace("."+str(date.microsecond), "")

log_dat = open("logs/log"+str(unix),"x")

last_string = ""

def log(string):
    date = datetime.now()
    log_dat.write("At "+str(date) + ": " + str(string)+ "\n")
def write(string, amt = 1):
    for i in range(amt):
        log_dat.write(str(string) + "\n")

from multiprocessing import Process
from multiprocessing import Queue
import time
from check import *
import datetime
from utils import *

def ExecuteCheckInParallel(queue):
    ## Read from the queue
    current_database = None
    dbOutput = None

    # connect to the log database
    db_Input = connectToDataBase(logDatabaseIPAddress, logDatabaseUsername, logDatabaseName, logDatabasePort)

    # open output file in locking mode to the use copy command
    copyFile, file_name = openFile()

    while True:
        entry = queue.get()         # Read from the queue and do nothing
        # we received the terminated signal there are no more stuff to consume
        if (entry == None):
            break

        # taking current database parameters (username, database and statement)
        user_name = entry[0]
        statement = entry[2]
        event_detail = entry[3]

        if(current_database == None):
            current_database = entry[1]
            dbOutput = connectToDataBase(outputDatabaseIPAddress, outputDatabaseUsername, current_database, outputDatabasePort)

        statement = checkParticularConditions(statement, event_detail)
        timestamp_start = datetime.datetime.now().strftime("%Y%m%d %I:%M:%S")
        Success, current_database, dbOutput, error = CheckQuery(entry, statement, current_database, dbOutput)
        timestamp_end = datetime.datetime.now().strftime("%Y%m%d %I:%M:%S")

        #copy to file
        statement = checkAndRemovingComment(statement)
        copyStatement(copyFile, user_name, current_database, statement, Success, error, timestamp_start, timestamp_end)

    copyFile.close()
    batchCopy(db_Input, file_name)

    # we are terminating close all
    dbOutput.close()
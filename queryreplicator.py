# -*- coding: utf-8 -*-
from database import *
from options import *
from multiprocessing import Process
from process import ExecuteCheckInParallel
from multiprocessing import Queue

def main(argv):

    # parsing command lines (-o, -i, -s, -h, -a)
    commandLineArguementParsing(argv)

    print("QueryReplicator: Running replication, just SUCCESSES AND ERRORS WILL BE PRINTED ON SCREEN")

    # connect to the log database
    db_Input = connectToDataBase(logDatabaseIPAddress, logDatabaseUsername, logDatabaseName, logDatabasePort)

    # main query to get all queries from log
    query_results = executeQueryOnLog(db_Input)

    # create a pool of processes synchronized by queues
    processes = []
    queues = []

    for i in range(0, int(N_PROC)):
        queue = Queue()
        queues.append(queue)
        proc = Process(target=ExecuteCheckInParallel, args=((queue),))
        proc.start()
        processes.append(proc)

    if(query_results):
        # sends every query to the queue of a specific thread
        for entry in query_results:
            queues[entry[5]].put(entry, False)

        #sends a None to all thread queues to terminate and close the queues
        for queue in queues:
            queue.put(None, False)
            queue.close()

        #join all processe before terminating
        for proc in processes:
            proc.join()

    db_Input.close()

# start main function
if __name__ == "__main__":
    main(sys.argv)

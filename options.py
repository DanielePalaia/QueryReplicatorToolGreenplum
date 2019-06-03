# This file manage the options

from database import *
from check import *
import datetime
import sys, getopt

def CreateResetOutputTable():
    print 'queryreplicator.py -o'
    print("resetting output table")
    resetOutputTable(logDatabaseIPAddress, logDatabaseUsername, logDatabaseName, logDatabasePort)
    print('output table created')


def LoadInputTableFromLog():
    print 'queryreplicator.py -l'
    print("creating and loading input table from logs")
    dbInput =  connectToDataBase(logDatabaseIPAddress, logDatabaseUsername, logDatabaseName, logDatabasePort)
    createInputTableFromLog(dbInput)
    print('input table created')
    dbInput.close()

def CreateExcludedQueriesTable():
    print 'queryreplicator.py -e'
    print("creating or resetting excluded table queries if not exists and fill entries like for ./scripts/GPDB_t_list_excluded_query.sql")
    createExcludedTable()
    print('input table created')

def AlterDatabase(alter_dbname):
    print 'queryreplicator.py -a ' + alter_dbname
    print("Alter Database Settings for ./scripts/GPDB_Alter_Database.sql")
    alterDatabaseSettings(alter_dbname)
    print('Database altered')

def commandLineArguementParsing(argv):
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'o r s l h e i a:')
    except getopt.GetoptError:
        sys.exit(2)

    for opt, arg in opts:

        # Output: reset the output result table of the Query replicator tool
        if opt == '-o':
            CreateResetOutputTable()
            sys.exit(0)

        # Load: load the input table from the log files
        if opt == '-l':
            LoadInputTableFromLog()
            sys.exit(0)

        # Excluded: Create or reset excluded table
        if opt == '-e':
            CreateExcludedQueriesTable()
            sys.exit(0)

        # AlterDB: Alter DB settings
        if opt == '-a':
            alter_dbname=arg
            AlterDatabase(alter_dbname)
            sys.exit(0)

        # Initialize: Create/Reset Output table, create excluded queries table and initialize input table from logs
        if opt == '-i':
            print 'queryreplicator.py -i'
            print("Initialize: Create/Reset Output table, create excluded queries table and initialize input table from logs at the same time")
            LoadInputTableFromLog()
            CreateResetOutputTable()
            CreateExcludedQueriesTable()
            sys.exit(0)

        # Reload: retry the queries that are currently in failed state in the output table
        if opt == '-r':
            print 'queryreplicator.py -r: Reinjecting query in failed state in ouput table'
            copyFile = openFile()
            query_results, db_Input=queryOutputTable(logDatabaseIPAddress, logDatabaseUsername, logDatabaseName, logDatabasePort)
            if (query_results):
                for entry in query_results:
                    user = entry[0]
                    current_database= entry[1]
                    statement= entry[2]
                    dbOutput =  connectToDataBase(outputDatabaseIPAddress, outputDatabaseUsername, current_database, outputDatabasePort)
                    timestamp_start = datetime.datetime.now().strftime("%Y%m%d %I:%M:%S")
                    # execute the query and return result
                    Success, current_database, current_database, error = CheckQuery(entry, statement, current_database, dbOutput)
                    timestamp_end = datetime.datetime.now().strftime("%Y%m%d %I:%M:%S")
                    #insertOutput(statement, error, db_Input, str(user), str(entry[1]), timestamp, Success)
                    #batch inserction
                    copyStatement(copyFile, str(user), str(entry[1]), statement, Success, error, timestamp_start, timestamp_end)

                copyFile.close()
                batchCopy(db_Input)

                sys.exit(0)

        # Statistics: Print statistics of what is currently stored in the output table
        if opt == '-s':
            print 'queryreplicator.py -s'
            try:
                dbInput =  connectToDataBase(logDatabaseIPAddress, logDatabaseUsername, logDatabaseName, logDatabasePort)
                total_query = countOutputTable(dbInput)
                success_query = countOutputTableSuccess(dbInput)
            except Exception as e:
                print("Sql error" + str(e))
                sys.exit(-1)

            print ("")
            print ("STATISTICS BASED ON OUTPUT TABLE: " + outputTableName)
            print ("")
            print ("TOTAL QUERY EXECUTED:          " + str(total_query))
            print ("SUCCESSED QUERIES:             " + str(success_query))
            print ("UNSUCCESSED QUERIES            " + str(total_query - success_query))
            print("")
            sys.exit(0)

        # Help prints the options help
        if opt == '-h':
            print 'queryreplicator.py -h: Usage'

            print ("")
            print ("Usage of the Query Replicator Tool")
            print ("")
            print ("Main usage: python queryreplicator.py: Start the computation")
            print ("python queryreplicator.py -l: load the input table from log files")
            print ("python queryreplicator.py -o: Create or reset the output table where results will be stored")
            print ("python queryreplicator.py -e: Create excluded queries table")
            print ("python queryreplicator.py -i: Load input table from log files, create or reset the output table and create excluded query table at the same time")
            print ("python queryreplicator.py -s: Print statistics on what stored in output table")
            print ("python queryreplicator.py -r: Reinject what is in failing state in output table specified")
            print ("python queryreplicator.py -a: Alter database settings like optimizer and statement_timeout")

            print("")
            sys.exit(0)
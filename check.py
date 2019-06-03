from database import *
import pygresql
from pygresql import pg


def CheckQuery(input, statement, current_database, dbOutput):
    user_name = input[0]
    database_name= input[1]
    error = 'No error'

    if(database_name != current_database):
        current_database = database_name
        dbOutput.close()
        dbOutput = connectToDataBase(outputDatabaseIPAddress, outputDatabaseUsername, current_database, outputDatabasePort)

    Success = True
    # check the query result
    try:
        #print(statement)
        query_result = executeQueryOutput(dbOutput, statement)
    # error the idea here is to insert the failure in a separate table
    except (pg.ProgrammingError, ValueError) as exception:
        print('FAILURE')
        Success = False
        error = str(exception)
        print (error)
    except pg.InternalError as exception:
        print('FAILURE')
        Success = False
        error = str(exception)
        print(error)
    # success or other exceptions
    else:
        print('SUCCESS')
        Success = True

    return Success, current_database, dbOutput, error

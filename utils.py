import sys
import os
import re
import subprocess
import commands
from properties import *


def replaceChars(statement):
    statement = statement.replace("\"","\"\"")
    return statement

def openFile():
    #open a temporary file to write the results for then use the copy command and copy in batch
    current_path=os.path.dirname(os.path.abspath(__file__))
    file_name= current_path + '/copy/copy' + str(os.getpid()) +'.txt'
    print current_path
    # open with in locking mode
    f = open(file_name, 'w+')
    return f, file_name

def copyStatement(copyFile, user_name, current_database, statement, Success, error, timestamp_start, timestamp_end):
    #error = replaceSpace(error)
    #statement = replaceSpace(statement)
    error = replaceChars(error)
    statement = replaceChars(statement)
    line = '"' +user_name + '"~"' + current_database + '"~"' + statement + '"~"' + str(Success) + '"~"' + error + '"~' + timestamp_start + '~' + timestamp_end +'\n'
    copyFile.write(line)

# reduce verbosity of error message
def replaceSpace(error):
    error = error.replace("\n"," ")
    return error

def checkAndRemovingComment(query):
    startComment = '/*'
    endComment = '*/'
    start = query.find(startComment)
    end = query.find(endComment)
    if (start == -1) or (end == -1):
        return query
    newquery = query[:start-1]
    newquery = newquery + query[end+1:]

    return newquery

def checkEventDetails(event_detail):

    parameters = None
    if(event_detail != None):
        parameters = re.findall(r'= \'(.*?)\'', event_detail)

    return parameters

def replacePrepareStatement(query, list_params):

    i = 1
    for param in list_params:

        tmpstring = "$" + str(i)

        query = query.replace(tmpstring, '\'' +param+ '\'')
        i = i+1

    return query



def checkParticularConditions(query, event_detail):

    list_params = checkEventDetails(event_detail)
    if(event_detail != None):
        query = replacePrepareStatement(query, list_params)

    return query

# This function creates the input table from the log file (please specify its name in property.py)
def createInputTableFromLog(dbInput):

    if (flag_Compress == False):
        str_Ext_Table_Command='\'cat ' + str_Input_File + ' 2> /dev/null || true\''
    else:
        str_Ext_Table_Command='\'zcat ' + str_Input_File + ' 2> /dev/null || true\''

    command = 'psql -U ' + logDatabaseUsername + ' -d ' +  logDatabaseName + ' -v v_ext_table_name=' + logDatabaseTable + ' -v v_read_file=\"' + str_Ext_Table_Command + '\" -f ./scripts/GPDB_read_master_log_template.sql'

    print(command)
    os.system(command)

def createExcludedTable():
    command = 'psql -U ' + logDatabaseUsername + ' -d ' +  logDatabaseName
    command = command + ' -v v_excludedQueryTable=' + excludedQueryTable
    command = command + ' -v v_excludedQueryFile=\"\'' + excludedQueryFile + '\'\"'
    command = command + ' -f ./scripts/GPDB_t_list_excluded_query.sql'
    print(command)
    os.system(command)


def alterDatabaseSettings(alter_dbname):
    command = 'psql -U ' + logDatabaseUsername + ' -d ' +  logDatabaseName
    command = command + ' -v v_db=' + alter_dbname
    command = command + ' -v v_statement_timeout=\"\'' + DatabaseStatementTimeout + '\'\"'
    command = command + ' -v v_optimizer=' + DatabaseOptimizer
    command = command + ' -f ./scripts/GPDB_Alter_Database.sql'
    print(command)
    os.system(command)

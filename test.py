# note to run unit test you need to have access to outputDatabaseIPAddress, outputDatabaseUsername, current_database, outputDatabasePort in database.py
# run with python -m unittest test

import unittest
from check import *


class TestQueryReplicator(unittest.TestCase):

    # this one is a simple query and should return True
    def testValid(self):
        input = []
        input.append('daniele')
        input.append('demo')
        input.append('select * from results;')
        current_database = 'demo'
        dbOutput = connectToDataBase(outputDatabaseIPAddress, outputDatabaseUsername, current_database, outputDatabasePort)
        check, current_database, dbOutput, error = CheckQuery(input, current_database, dbOutput)
        self.assertEqual(check, True)

    # this one is clearly invalid and should return False
    def testInvalid(self):
        input = []
        input.append('daniele')
        input.append('demo')
        input.append('Error lkajdfkjalsdf * fromasdfwer results;')
        current_database = 'demo'
        dbOutput = connectToDataBase(outputDatabaseIPAddress, outputDatabaseUsername, current_database, outputDatabasePort)
        check, current_database, dbOutput, error = CheckQuery(input, current_database, dbOutput)
        self.assertEqual(check, False)

    # the table is not present but the query is corrent should return True
    def testValidNonExisting(self):
        input = []
        input.append('daniele')
        input.append('demo')
        input.append('select * from results WHERE user=\'not found\';')
        current_database = 'demo'
        dbOutput = connectToDataBase(outputDatabaseIPAddress, outputDatabaseUsername, current_database, outputDatabasePort)
        check, current_database, dbOutput, error = CheckQuery(input, current_database, dbOutput)
        self.assertEqual(check, True)

    # the table is not present but the query is corrent should return True
    def testComplexScenario(self):
        input = []
        input.append('daniele')
        input.append('demo')
        input.append('SELECT p.oid::pg_catalog.regprocedure AS signature, ( SELECT rolname FROM pg_catalog.pg_roles WHERE oid = proowner ) AS owner FROM pg_pltemplate t, pg_proc p WHERE p.oid = 10885 AND proname = tmplvalidator AND pronamespace = ( SELECT oid FROM pg_namespace WHERE nspname = \'pg_catalog\' )')
        current_database = 'demo'
        dbOutput = connectToDataBase(outputDatabaseIPAddress, outputDatabaseUsername, current_database, outputDatabasePort)
        check, current_database, dbOutput, error = CheckQuery(input, current_database, dbOutput)
        self.assertEqual(check, True)

        # the table is not present but the query is corrent should return True
    def testComplexScenarioFailing(self):
        input = []
        input.append('daniele')
        input.append('demo')
        input.append('SELECT pg_get_partition_def(\'340734\'::pg_catalog.oid, true, true)')
        current_database = 'demo'
        dbOutput = connectToDataBase(outputDatabaseIPAddress, outputDatabaseUsername, current_database, outputDatabasePort)
        check, current_database, dbOutput, error = CheckQuery(input, current_database, dbOutput)
        self.assertEqual(check, False)

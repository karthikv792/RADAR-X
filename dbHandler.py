import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
import os
from flask import jsonify

class dbHandler:

    def __init__(self):
        self.db = MySQLdb.connect('localhost', 'root', 'yochan', 'radar')
        self.db.autocommit(True)
        self.tableKeys = {'fire_stations_actual': 'fire_station', 'hospitals': 'hospital',
                          'police_stations': 'police_station'}

    def initializeDatabase(self):
        try:
            cmd = 'mysql -u root -pyochan radar < radar.sql'
            os.system(cmd)
        except:
            print("[ERROR] Initializing RADAR Database")

    def getObjects(self):
        cursor = self.db.cursor()
        cursor.execute('select * from object_type')
        a = cursor.fetchall()
        cursor.close()
        return a

    def getTasks(self):
        cursor = self.db.cursor()
        cursor.execute('select * from tasks')
        a = cursor.fetchall()
        cursor.close()
        return a

    def getFireStationsData(self):
        cursor = self.db.cursor()
        cursor.execute('select * from fire_stations_actual')
        s = cursor.fetchall()
        cursor.close()
        return s

    def getFireStationPredicates(self):
        cursor = self.db.cursor()
        cursor.execute('select * from predicates_for_fireStation')
        s = cursor.fetchall()
        cursor.close()
        return s

    def getHospitalData(self):
        cursor = self.db.cursor()
        cursor.execute('select * from hospitals')
        a = cursor.fetchall()
        cursor.close()
        return a

    def getHospitalPredicates(self):
        cursor = self.db.cursor()
        cursor.execute('select * from predicates_for_hospital')
        a = cursor.fetchall()
        cursor.close()
        return a

    def getPoliceStationData(self):
        cursor = self.db.cursor()
        cursor.execute('select * from police_stations')
        a = cursor.fetchall()
        cursor.close()
        return a

    def getPoliceStationPredicates(self):
        cursor = self.db.cursor()
        cursor.execute('select * from predicates_for_policeStation')
        a = cursor.fetchall()
        cursor.close()
        return a

    def getActionDurations(self):
        cursor = self.db.cursor()
        cursor.execute('select * from durations')
        a = cursor.fetchall()
        cursor.close()
        return a

    def getSubGoalPredicates(self):
        cursor = self.db.cursor()
        cursor.execute('select * from subgoals')
        a = cursor.fetchall()
        cursor.close()
        return a

    def getCustomCursor(self, rowsToGet, tableName, conditions='1=1'):
        cursor = self.db.cursor()
        cursor.execute('select {0} from {1} where {2}'.format(rowsToGet, tableName, conditions))
        a = cursor.fetchall()
        cursor.close()
        return a
    def getUIReadyData(self, data, tableName):
        cursor = self.db.cursor()
        cursor.execute('describe {0}'.format(tableName))
        tableDesc = cursor.fetchall()
        mutable_data = [ [] for i in range( len(data) ) ]
        for i in range(len(data)):
            mutable_data[i].append( data[i][0] )
            for j in range(1, len(data[i] )):
                s = '<div class="{0}" style="color:{1};cursor:pointer" onclick="updateResource(\'{2}\', \'{3}\', \'{4}\', {5})"></div>'
                if data[i][j] == 1:
                    mutable_data[i].append( s.format(
                        'fas fa-check', '#00C851', tableName, data[i][0], tableDesc[j][0], 1) )
                else:
                    mutable_data[i].append( s.format(
                        'fas fa-times', '#ff4444', tableName, data[i][0], tableDesc[j][0], 0) )
        cursor.close()
        return mutable_data

    def updateResourcesInTable(self, resourceName, tableName, rowId, presentState):
        cursor = self.db.cursor()
        updatedState = 1
        if presentState == '1':
            updatedState = 0
        sql_cmd = 'update {0} set {1} = {2} where {3} like "{4}"'.format(tableName, resourceName, updatedState, self.tableKeys[ tableName ], rowId)
        print(sql_cmd)
        cursor.execute(sql_cmd)
        cursor.close()
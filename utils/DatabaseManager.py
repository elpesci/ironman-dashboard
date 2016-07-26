import pymysql as MySQLdb
import pymysql.cursors
import psycopg2

class SQLDatabaseManager:

    def __init__(self, host, user, passwd, db):
        self.__err = ""
        self.isConnectionAlive = False
        self.db = None
        self.__query = ""
        self.db_args = {"host":host, "user":user, "passwd":passwd, "db":db}

    def getConnection(self):
        try:
            if not self.isConnectionAlive:
                self.db = MySQLdb.connect(host=self.db_args['host'],
                            user=self.db_args['user'],
                        passwd=self.db_args['passwd'],
                        db=self.db_args['db'],
                        cursorclass=MySQLdb.cursors.DictCursor)
                self.isConnectionAlive = True
            return self.db
        except Exception, e:
            self.__err = e.message
            return None

    def getError(self):
        return self.__err

    def queryCursor(self, query):
        # print("QUERY: %s" % query)
        self.__query = query
        cursor = self.getConnection().cursor()
        cursor.execute(query)
        return cursor

    def runQuery_fetchOne(self, query):
        return self.queryCursor(query).fetchone()

    def runQuery_fetchAll(self, query):
        try:
            return self.queryCursor(query).fetchall()
        except:
            return None

    def runQuery(self, query):
        return runQuery_fetchAll()

    def runCommit(self, query):
        try:
            self.__query = query
            cursor = self.getConnection().cursor()
            cursor.execute(query)
            self.db.commit()
            return True
        except Exception, e:
            # print "Query: " + self.__query
            # print "ERR: " + e.message
            self.__err = e.message
            self.db.rollback()
            return False

    def __del__(self):
        if self.db:
            self.db.close()
        self.isConnectionAlive = None


class PGDatabaseManager():
    def __init__(self, host=None, dbname='postgres', user='smcp', password='smcp1234'):
        self.host = host
        if not host:
            self.host = 'postgres.cvbe158gtbog.us-west-2.rds.amazonaws.com'
        self.dbname = dbname
        self.user = user
        self.password = password
        self.conn = None
        self.conn = self.get_conn()

    def get_conn(self):
        if self.conn and not self.conn.closed:
            return self.conn
        else:
            self.conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'"%\
                            (self.dbname,self.user,self.host,self.password))
            return self.conn
    
    def get_rows(self,query):
        cursor = self.get_conn().cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        del cursor
        return rows

    def get_rows_with_date_range(self, query, start_date, end_date):
        """ 
        start_date, end_date must be in the format:
        yyyy-mm-dd
        """
        query+=" where date_created >= '%s 00:00:00'"%start_date
        query+=" and date_created < '%s 00:00:00'"%end_date 
        
        cursor = self.get_conn().cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        del cursor
        return rows

    '''
     Get Public Score rows filtering by State Name and between a date range
    '''
    def get_rows_public_score_by_state(self, query, stateName, start_date, end_date):
        # building query predicate
        query += " where estado ='" + stateName + "'"
        query += " and date_created >= '%s 00:00:00'" % start_date
        query += " and date_created <= '%s 00:00:00'" % end_date

        cursor = self.get_conn().cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        del cursor

        return rows

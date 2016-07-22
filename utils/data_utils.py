from DatabaseManager import *
import datetime, time
from collections import defaultdict
import random
from twitter import *
import math
from tweepy import TweepError
import operator

def string_to_date(st):
    datepars = [int(v) for v in st.split("-")]
    return datetime.datetime(datepars[0], datepars[1], datepars[2])

def date_to_unixtime(dt):
    return int(time.mktime(dt.timetuple()))

def datetime_to_str(dt):
    return dt.strftime("%Y-%m-%d")

def datetime_to_slash_string(dt):
    return dt.strftime("%m/%d")+'/'+dt.strftime("%Y")[-2:]

def get_week_ago(ctime=datetime.datetime.now()):
    return ctime-datetime.timedelta(7)

def get_days_ago(days,ctime=datetime.datetime.now()):
    return ctime-datetime.timedelta(days)

def bool_or_int(d):
    if not d: return 0
    else: return int(d)

def get_rows_tb3_date_range(sdate=get_week_ago(),edate=datetime.datetime.now()):
    sdate = datetime_to_str(sdate)
    edate = datetime_to_str(edate)
    pg = PGDatabaseManager()
    query = "select * from public.tb3"
    rows = pg.get_rows_with_date_range(query,sdate,edate)
    raw_data = defaultdict(dict)
    for row in rows:
        if raw_data[datetime_to_str(row[0])].has_key(row[7]):
            pass
        else:
            raw_data[datetime_to_str(row[0])][row[7]]=[]
        raw_data[datetime_to_str(row[0])][row[7]].append({row[1]:row[2:5]})
    states = defaultdict(dict)
    for day in raw_data:
        daystates = raw_data[day]
        for state in daystates:
            if state not in states:
                states[state]=[]
            states[state].extend(daystates[state])
    aggregation = defaultdict(dict)
    for state in states:
        for item in states[state]:
            if not aggregation[state].has_key(item.keys()[0]):
                aggregation[state][item.keys()[0]]= defaultdict(int)
            item[item.keys()[0]] = [bool_or_int(v) for v in item[item.keys()[0]]]
            aggregation[state][item.keys()[0]]["pos"]+=item[item.keys()[0]][0]
            aggregation[state][item.keys()[0]]["neu"]+=item[item.keys()[0]][1]
            aggregation[state][item.keys()[0]]["neg"]+=item[item.keys()[0]][2]

    return aggregation

def get_rows_tb4_date_range(sdate=get_days_ago(7),edate=datetime.datetime.now()):
    sdate = datetime_to_str(sdate)
    edate = datetime_to_str(edate)
    pg = PGDatabaseManager()
    query = "select * from public.tbl4"
    rows = pg.get_rows_with_date_range(query,sdate,edate)
    data_index = defaultdict(str)
    scores = {}
    ranks = {}
    for row in rows:
            try:
                row_2 = float(row[2])
            except:
                row_2 = 0
            scores[row[1]]={
                "general":row_2,
                "salud":int(row[4]),
                "economia":int(row[6]),
                "seguridad":int(row[8]),
                "servicios":int(row[10])
            }
            ranks[row[1]]={
                "general":float(row[3]),
                "salud":int(row[5]),
                "economia":int(row[7]),
                "seguridad":int(row[9]),
                "servicios":int(row[11])
            }
    return scores, ranks


def get_state_timeline(estado, tema):
    query = "select * from public.tb4 where date_created == 'None'" # dummy case
    if tema == "general":
        query = """select date_created, score
from public.tb4
where estado = '{0}'""".format(estado)
    else:
        query = """select date_created, score_{1}
from public.tb4
where estado = '{0}'""".format(estado, tema)

    pg = PGDatabaseManager()
    return [(date_to_unixtime(row[0])*1000,row[1]) for row in pg.get_rows(query)]

def get_timeline_date_range(sdate=get_days_ago(7),edate=datetime.datetime.now()):
    sdate = datetime_to_str(sdate)
    edate = datetime_to_str(edate)
    pg = PGDatabaseManager()
    query = "select * from public.tb4"
    rows = pg.get_rows_with_date_range(query,sdate,edate)
    print rows

import random

def get_news_data(tema=None, estado=None):
    """
    Data structure:
    (date_created, heading, newspaper, description, origin, categoria, estado1, estado2, estado3)
    """
    pg = PGDatabaseManager()
    if not estado or estado.lower()=="general":
        query = "select * from public.tb_news order by date_created desc limit 100"
        cursor = pg.conn.cursor()
        cursor.execute(query)
        res = cursor.fetchall()
        #return [random.choice(res) for i in range(10)]
        return []
    else:
        query = """
select * from public.tb_news
where categoria='%s'
and "estado.1" like '%s'
order by date_created desc
limit 10"""%(tema, estado)
        cursor = pg.conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()

def get_ranked_news():
    pg = PGDatabaseManager()
    query = """select *
    from public.tbl_rank_news
    order by ano desc, semana desc
    limit 32"""
    rows = pg.get_rows(query)
    data_index = defaultdict(str)
    scores = {}
    ranks = {}
    for row in rows:
            scores[row[4]]={
                "general":float(row[5]),
                "salud":int(row[7]),
                "economia":int(row[9]),
                "seguridad":int(row[11]),
                "servicios":int(row[13])
            }
            ranks[row[4]]={
                "general":float(row[6]),
                "salud":int(row[8]),
                "economia":int(row[10]),
                "seguridad":int(row[12]),
                "servicios":int(row[14])
            }
    return scores, ranks

def get_ranked_news_last():
    pg = PGDatabaseManager()
    query = """select *
    from public.tbl_rank_news
    order by ano desc, semana desc
    limit 64"""
    rows = pg.get_rows(query)
    data_index = defaultdict(str)
    scores = {}
    ranks = {}
    counter = 0
    for row in rows:
            if counter < 32:counter+=1;continue
            scores[row[4]]={
                "general":float(row[5]),
                "salud":int(row[7]),
                "economia":int(row[9]),
                "seguridad":int(row[11]),
                "servicios":int(row[13])
            }
            ranks[row[4]]={
                "general":float(row[6]),
                "salud":int(row[8]),
                "economia":int(row[10]),
                "seguridad":int(row[12]),
                "servicios":int(row[14])
            }
    return scores, ranks


def get_last_scores():
    sdate=get_week_ago()
    edate=datetime.datetime.now()
    sdate = datetime_to_str(sdate)
    edate = datetime_to_str(edate)
    pg = PGDatabaseManager()
    query = "select * from public.tb4"
    rows = pg.get_rows_with_date_range(query,sdate,edate)
    date_index = defaultdict(str)
    scores = {}
    for row in rows:
        if date_index[row[1]] < datetime_to_str(row[0]) or not date_index[row[1]]:
            date_index[row[1]] = datetime_to_str(row[0])
            scores[row[1]] = (row[2],row[3])
        else:
            pass
    return scores

def get_last_scores_state(statename):
    sdate=get_week_ago()
    edate=datetime.datetime.now()
    sdate = datetime_to_str(sdate)
    edate = datetime_to_str(edate)
    pg = PGDatabaseManager()
    query = "select date_created, estado, score from public.tb4"
    rows = pg.get_rows_with_date_range(query,sdate,edate)
    timeline = [] 
    for row in rows:
        if row[1]!=statename:continue
        timeline.append((datetime_to_str(row[0]),float(row[2])))
    return timeline

def get_last_positions_state_category(statename,category,dfrom=None,dto=None):
    if not dfrom or not dto:
        sdate=get_days_ago(30)
        edate=datetime.datetime.now()
    else:
        sdate = datetime.datetime(int(dfrom[4:]),int(dfrom[:2]),int(dfrom[2:4]))
        edate = datetime.datetime(int(dto[4:]),int(dto[:2]),int(dto[2:4]))
    sdate = datetime_to_str(sdate)
    edate = datetime_to_str(edate)
    pg = PGDatabaseManager()
    if category:
    	query = "select date_created, estado, rank_%s from public.tb4"%category
    else:
        query = "select date_created, estado, rank from public.tb4"
    rows = pg.get_rows_with_date_range(query,sdate,edate)
    timeline = [] 
    counter = 0
    for row in rows:
        if row[1]!=statename:continue
        timeline.append((counter,float(row[2]),datetime_to_str(row[0])))
        counter += 1
    return timeline


def get_last_scores_state_category(statename,category,dfrom=None,dto=None):
    if not dfrom or not dto:
        sdate=get_days_ago(30)
        edate=datetime.datetime.now()
    else:
        sdate = datetime.datetime(int(dfrom[4:]),int(dfrom[:2]),int(dfrom[2:4]))
        edate = datetime.datetime(int(dto[4:]),int(dto[:2]),int(dto[2:4]))
    sdate = datetime_to_str(sdate)
    edate = datetime_to_str(edate)
    pg = PGDatabaseManager()
    if category:
    	query = "select date_created, estado, score_%s from public.tb4"%category
    else:
        query = "select date_created, estado, score from public.tb4"
    rows = pg.get_rows_with_date_range(query,sdate,edate)
    timeline = []
    mean_timeline = []
    accum_mean_timeline = defaultdict(float)
    counter = 0
    accum = defaultdict(int)
    for row in rows:
        if row[1]!=statename:
            accum[datetime_to_str(row[0])]+=1
            accum_mean_timeline[datetime_to_str(row[0])]+=float(row[2])
            continue
        timeline.append((counter,float(row[2]),datetime_to_str(row[0])))
        counter += 1
    counter = 0
    for item in accum_mean_timeline.keys():
        mean_timeline.append((counter, float(accum_mean_timeline[item])/accum[item],item))
        counter+=1
    print timeline, mean_timeline
    return timeline, mean_timeline

def get_general_sr(category=None):
    if category:
        query = """select estado, score_%s, rank_%s from public.tbl_rank_general
order by id desc, estado asc
limit 32;"""%(category, category)
    else:
        query = """select estado, score_general, rank_general from public.tbl_rank_general
order by id desc, estado asc
limit 32;"""
    pg = PGDatabaseManager()
    rows =  pg.get_rows(query)
    data = {}
    for item in rows:
        data[item[0]]={"score":item[1],"rank":item[2]}
    data = sorted(data.iteritems(), key=lambda x: x[1]["rank"])
    return data

def get_general_sr_last(category=None):
    if category:
        query = """select estado, score_%s, rank_%s from public.tbl_rank_general
order by id desc, estado asc
limit 64;"""%(category, category)
    else:
        query = """select estado, score_general, rank_general from public.tbl_rank_general
order by id desc, estado asc
limit 64;"""
    pg = PGDatabaseManager()
    rows =  pg.get_rows(query)
    data = []
    counter = 1
    for item in rows:
        if counter < 32:counter+=1;continue
        data.append((item[0], {"score":item[1],"rank":item[2]}))
    return data


def get_geolocated_tweets_data(stateid, dfrom=None,dto=None):
    if stateid=="GUER":stateid="GUERRERO"
    if stateid=="SIN":stateid="SINALOA"
    if stateid=="JAL":stateid="JAL2"
    if stateid=="DF":stateid="DF2"
    if not dfrom or not dto:
        sdate=get_days_ago(30)
        edate=datetime.datetime.now()
    else:
        sdate = datetime.datetime(int(dfrom[4:]),int(dfrom[:2]),int(dfrom[2:4]))
        edate = datetime.datetime(int(dto[4:]),int(dto[:2]),int(dto[2:4]))
    sdate = datetime_to_str(sdate)
    edate = datetime_to_str(edate)
    pg = PGDatabaseManager()
    query = 'select date_created,lon,lat,polarizacion '
    query += 'from public."tb2_%s"'%stateid
    rows = pg.get_rows_with_date_range(query,sdate,edate)
    left_border = -99.14651
    right_border = -99.14651
    up_border = 19.41125
    down_border = 19.41125
    for row in rows:
        if row[1] > -90: continue
        if row[2] < down_border: down_border=row[1]
        if row[2] > up_border: up_border=row[1]
        if row[1] < left_border: left_border=row[2]
        if row[1] > right_border: right_border=row[2]
    return rows, {"lon":(down_border+up_border)/2.0,"lat":(left_border+right_border)/2.0}

def get_frec_terms(statename, categoria, dfrom=None, dto=None, data_len=10, pol=""):
    if not dfrom or not dto:
        sdate=get_days_ago(30)
        edate=datetime.datetime.now()
    else:
        sdate = datetime.datetime(int(dfrom[4:]),int(dfrom[:2]),int(dfrom[2:4]))
        edate = datetime.datetime(int(dto[4:]),int(dto[:2]),int(dto[2:4]))
    sdate = datetime_to_str(sdate)
    edate = datetime_to_str(edate)
    pg = PGDatabaseManager()
    query = 'select date_created,term,freq,categoria,estado,polarizacion '
    query += 'from public."tbl_topWordsPol" '
    rows = pg.get_rows_with_date_range(query,sdate,edate)
    import operator
    if categoria and categoria!="general": categoria=[categoria]
    else: categoria = ["salud","seguridad","economia","servicios"]
    words = defaultdict(float)
    if not pol: pol = ["positivo", "negativo"]
    else: pol = [pol]
    for row in rows:
        if row[5] not in pol or row[4] != statename \
                or row[3] not in categoria:continue
        words[row[1]]+=row[2]
    words = sorted(words.iteritems() , key=operator.itemgetter(1), reverse=True)
    counter = 0
    output = []
    for word in words:
        output.append((counter,word[0],word[1]))
        counter+=1
    return output[:data_len]

########################################### USERS TAB

def get_top_users(statename, categoria, sdate=None,edate=None):
    if not sdate: sdate = get_days_ago(3)
    if not edate: edate = datetime.datetime.now()
    sdate = datetime_to_str(sdate)
    edate = datetime_to_str(edate)
    pg = PGDatabaseManager()
    query = 'select date_created,from_user_id,freq_users,categoria,estado '
    query += 'from public."tbl_topUsersString"'
    rows = pg.get_rows_with_date_range(query,sdate,edate)
    rows.sort(key=operator.itemgetter(2),reverse=True)
    users = []
    counter = 0
    users_set = set()
    for row in rows:
        if row[4]!=statename or row[3]!=categoria:continue
        if row[1] in users_set: continue
        users.append((counter,row[1],row[2]))
        users_set.add(row[1])
        counter+=1
    data = []
    for item in users:
        if len(data) >= 10: break
        try:
            fulluser = get_user_from_id(item[1])
        except TweepError:
            continue
        impacto = int(math.log(item[2]*fulluser["followers_count"])*100)/100.0
        data.append((item[0],fulluser,item[2],impacto))
    data.sort(key=operator.itemgetter(3),reverse=True)
    return data

def get_user_from_id(userid):
    return get_or_create_user(userid)


####################################################### Corrs Tab

def get_forecasts(index):
    pg = PGDatabaseManager()
    query = "select * from public.tb_pronosticos_mensual order by fechas asc"
    rows = pg.get_rows(query)
    # return [(date_to_unixtime(row[0])*1000, row[int(index)+1]) for row in rows]
    return [(datetime_to_slash_string(row[0]), row[int(index)+1]) for row in rows]



######################################################## Public Policies

def get_last_scores_state_category_pp(statename,category,dfrom=None,dto=None):
    if not dfrom or not dto:
        sdate=get_days_ago(8)
        edate=get_days_ago(1)
    else:
        dfrom = dfrom.split("-")
        dto = dto.split("-")
        sdate = datetime.datetime(int(dfrom[0]),int(dfrom[1]),int(dfrom[2]))
        edate = datetime.datetime(int(dto[0]),int(dto[1]),int(dto[2]))
    sdate = datetime_to_str(sdate)
    edate = datetime_to_str(edate)
    pg = PGDatabaseManager()
    if category:
    	query = "select date_created, estado, \"score_%s\" from public.tbl4"%category
    else:
        query = "select date_created, estado, score from public.tbl4"
    rows = pg.get_rows_with_date_range(query,sdate,edate)
    timeline = []
    mean_timeline = []
    accum_mean_timeline = defaultdict(float)
    counter = 0
    accum = defaultdict(int)
    for row in rows:
        if row[1]!=statename:
            accum[datetime_to_str(row[0])]+=1
            accum_mean_timeline[datetime_to_str(row[0])]+=float(row[2])
            continue
        timeline.append((counter,float(row[2]),datetime_to_str(row[0])))
        counter += 1
    counter = 0
    for item in accum_mean_timeline.keys():
        mean_timeline.append((counter, float(accum_mean_timeline[item])/accum[item],item))
        counter+=1
    score = 0
    for item in timeline:
        score+=item[1]
    if len(timeline) > 0:
        score/=(len(timeline))
    return score, timeline, mean_timeline

def get_last_ranks_state_category_pp(statename,category,dfrom=None,dto=None):
    if not dfrom or not dto:
        sdate=get_days_ago(7)
        edate=datetime.datetime.now()
        sdate = datetime_to_str(sdate)
        edate = datetime_to_str(edate)
    else:
        sdate = dfrom
        edate = dto
    pg = PGDatabaseManager()
    if category:
    	query = "select date_created, estado, \"rank_%s\" from public.tbl4"%category
    else:
        query = "select date_created, estado, rank from public.tb4"
    rows = pg.get_rows_with_date_range(query,sdate,edate)
    timeline = []
    mean_timeline = []
    accum_mean_timeline = defaultdict(float)
    counter = 0
    accum = defaultdict(int)
    for row in rows:
        if row[1]!=statename:
            accum[datetime_to_str(row[0])]+=1
            accum_mean_timeline[datetime_to_str(row[0])]+=float(row[2])
            continue
        timeline.append((counter,float(row[2]),datetime_to_str(row[0])))
        counter += 1
    counter = 0
    for item in accum_mean_timeline.keys():
        mean_timeline.append((counter, float(accum_mean_timeline[item])/accum[item],item))
        counter+=1
    rank = 0
    for item in timeline:
        rank+=item[1]
    rank = int(rank/(len(timeline)+1))
    return rank, timeline, mean_timeline


def get_public_scores_state(statename,dfrom=None,dto=None):
    if not dfrom or not dto:
        sdate=get_days_ago(8)
        edate=get_days_ago(1)
        sdate = datetime_to_str(sdate)
        edate = datetime_to_str(edate)
    else:
        sdate = dfrom
        edate = dto
    pg = PGDatabaseManager()
    query = "select estado, score_presidente, score_gobernador, score_legislativo, score_gobierno from public.tb4_pp"
    rows = pg.get_rows_with_date_range(query,sdate,edate)
    timeline = [0,0,0,0,0,0,0,0]
    counter = 0
    for row in rows:
        if row[0] != statename: continue
        counter+=1
        for i in xrange(len(row)-1):
            timeline[i]+=row[i+1]
    try:
        for i in xrange(len(row)-1):
            timeline[i] = int((timeline[i]/counter)*100.0)/100.0
    except ZeroDivisionError:
        for i in xrange(len(row)-1):
            timeline[i] = 0.0
    overflow = len(row)-1
    # ---->>> overflow
    query = "select estado, score_seguridad, score_servicios, score_economia, score_salud from public.tb4"
    rows = pg.get_rows_with_date_range(query,sdate,edate)
    counter = 0
    for row in rows:
        if row[0] != statename: continue
        counter+=1
        for i in xrange(len(row)-1):
            timeline[overflow+i]+=row[i+1]
    try:
        for i in xrange(len(row)-1):
            timeline[overflow+i] = int((timeline[overflow+i]/counter)*100.0)/100.0
    except ZeroDivisionError:
        for i in xrange(len(row)-1):
            timeline[overflow+i] = 0.0
    return timeline


def get_ppublic_hashtags(tema,estado,date):
    query = """
select hashtags, count from public."tbl_topHash"
where estado = '{0}'
and categoria = '{1}'
and date_created = '{2}'
""".format(estado,tema,date)
    pg = PGDatabaseManager()
    return pg.get_rows(query)

def get_ppublic_tweets(tema, estado, date):
    query = """select text, score from public."tbl_topTweets"
where estado = '{0}'
and categoria = '{1}'
and date_created = '{2}'
order by score desc, date_created desc""".format(estado,tema,date)
    pg = PGDatabaseManager()
    return pg.get_rows(query)

################################################################## EXPORTS

def export_data_pp(days_ago=30):
    data = []

    sdate=get_days_ago(days_ago)
    edate=datetime.datetime.now()
    sdate = datetime_to_str(sdate)
    edate = datetime_to_str(edate)

    query = """select * from public."tb4_pp" where date_created >= '{0}' and date_created <= '{1}'
""".format(sdate, edate)
    pg = PGDatabaseManager()
    for row in pg.get_rows(query):
        data.append(row)
    return data

def export_data_rankings():
    query = """select * from public.tbl_rank_general
order by id desc
limit 128;"""
    pg = PGDatabaseManager()
    return pg.get_rows(query)

def export_data_scores(days_ago=30):
    sdate=get_days_ago(days_ago)
    edate=datetime.datetime.now()
    sdate = datetime_to_str(sdate)
    edate = datetime_to_str(edate)


    pg = PGDatabaseManager()
    query = "select * from public.tb4"
    return pg.get_rows_with_date_range(query,sdate,edate)

def export_data_noticias():
    pg = PGDatabaseManager()
    query = """select *
from public.tbl_rank_news
order by ano desc, semana desc
limit 128"""
    return pg.get_rows(query)





##########################################################|||||||>

if __name__=="__main__":
    print get_last_scores_state_category_pp("Aguascaliente","presidente")
    print "---"
    print get_public_scores_state("Baja California")




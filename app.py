from flask import Flask, make_response, flash, redirect
from flask import render_template, session, request, url_for
from data_utils import *
from rq_queues import create_general_report
import csv
from random import shuffle
# from future import unicode_literals
import sys
reload(sys)
import json
import os
import datetime
import glob
from dropbox_corr_links import get_corrs_from_api
import StringIO
from collections import defaultdict
import operator

from models import *

sys.setdefaultencoding("utf-8")


app = Flask(__name__)

app.secret_key = 'kuriki.kaka.ki...kuriki.kaka.ka'
db.init_app(app)

not_available_msg = """Los estados seleccionados no estan disponibles en su configuracion de usuario. Por favor \
pongase en contacto con nuestra area comercial."""
invitado_message = """La funcionalidad seleccionada no esta disponible para los usuarios invitados. Por favor \
pongase en contacto con nuestra area comercial."""


def state_available(estado):
    estado = Estado.objects(codigo=estado).first()
    cliente = Cliente.objects(login=session["username"]).first()
    if estado not in cliente.estados:
        return False
    return True

@app.before_request
def before_request():
    if "favicon.ico" in request.url:return
    # if True: pass # para pemitir accesos de usuario
    elif request.endpoint in ["login", "register", "payment", "static"]:pass
    elif not session.get("username",None): return redirect(url_for('login'))
    elif session["username"]=="invitado":
        # print request.endpoint
        if not request.endpoint or \
            request.endpoint.strip('/') in ['index','logout']:
            return
        else:
            flash(invitado_message,"error")
            return redirect(url_for('index'))
    elif request.endpoint == "usuarios":
        params = request.url.strip('/').split('/')[-1]
        if params == "usuarios":
            return
        else:
            cat, state = params.split('-')[0], params.split('-')[1]
            if not state:
                return
            else:
                if not state_available(state):
                    flash(not_available_msg,"error")
                    return redirect(url_for(request.endpoint))
                else:
                    return
    elif request.endpoint == "mapas":
        params = request.url.strip('/').split('/')[-1]
        if params == "mapas":
            return
        elif params.isdigit():
            params = request.url.split('/')[-3]
            cat, state = params.split('-')[0], params.split('-')[1]
            if not state_available(state):flash(not_available_msg,"error"); return redirect(url_for(request.endpoint))
            else: return
        else:
            print params.split("-")
            cat, state = params.split('-')[0], params.split('-')[1]
            if not state:
                return
            else:
                if not state_available(state):
                    flash(not_available_msg,"error")
                    return redirect(url_for(request.endpoint))
                else:
                    return

    else: # other endpoints
        pass


@app.route("/login", methods=["GET","POST"])
@app.route("/login/invitado", methods=["GET"])
def login():
    if request.url.split("/")[-1]=="invitado":
        session["username"] = "invitado"
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        user = get_client_from_username(username)
        if user and password == user.password:
            session["username"] = username
            return redirect(url_for("index"))
        else:
            flash("Nombre de usuario o password incorrecto")
        return render_template("login.html")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username")
    return redirect("/login")

from forms import *

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        print "trying to register with login:", form.login.data
        if Cliente.objects(login=form.login.data).first():
            flash("El login ya existe, elija otro por favor","error")
            return render_template('register.html', form=form)
        client = Cliente(
                nombre=form.nombre.data,
                login=form.login.data,
                password=form.password.data,
                descripcion=form.descripcion.data
                )
        client.save()

        session["username"] = client.login
        flash('Gracias por registrarse en nuestro servicio! A continuacion procederemos con los detalles de su pago.')
        return redirect(url_for('payment'))
    return render_template('register.html', form=form)

@app.route('/payment')
def payment():
    form = PaymentForm(request.form)
    return render_template('payment.html', form=form)

@app.route("/score")
@app.route("/score/<tpars>")
def score(tpars=None):
    if not session.has_key("username"):return redirect("/login")
    if tpars == "favicon.ico":
        return redirect(url_for('static', filename='favicon.ico'))
    reader = csv.reader(open("./utils/formato_estados.csv"))
    _ = reader.next()
    estados = dict([(row[0],row[1]) for row in reader])
    estados = estados.keys()
    estados.sort()
    # print estados
    alltopics = ("economia", "salud", "seguridad", "servicios")
    notopic = False
    if not tpars or tpars=="general":
        notopic = True
        tpars = ["economia", "salud", "seguridad", "servicios"]
    else:
        tpars = [tpars]

    sentiments = get_rows_tb3_date_range()
    data_sentiments = {}
    for state in sentiments:
        if notopic:
            general = {'neg': 0, 'neu': 0, 'pos': 0}
            for key in tpars:
                general['neg'] = general['neg']+sentiments[state][key]['neg']
                general['neu'] = general['neu']+sentiments[state][key]['neu']
                general['pos'] = general['pos']+sentiments[state][key]['pos']
            data_sentiments[state] = dict([("general", general)])
        else:
            data_sentiments[state] = dict([(key, sentiments[state][key]) for key in tpars])
    if notopic:
        rsearch = ["general"]
    else: rsearch = tpars

    scores, ranks = get_rows_tb4_date_range()
    last_scores , last_ranks = get_rows_tb4_date_range(get_days_ago(14),get_days_ago(7))
    data_scores, data_ranks = {}, {}
    last_data_scores, last_data_ranks = {}, {}
    for state in scores:
        data_scores[state] = dict([(key, scores[state][key]) for key in rsearch])
        last_data_scores[state] = dict([(key, last_scores[state][key]) for key in rsearch])
    for state in ranks:
        data_ranks[state] = dict([(key, int(ranks[state][key])) for key in rsearch])
        last_data_ranks[state] = dict([(key, int(last_ranks[state][key])) for key in rsearch])

    ## hand coded stuff
    if notopic:
        data_sentiments = sorted(data_sentiments.items(), \
                key=lambda x: x[1]['general']['neu'], reverse=True)
    else:
        data_sentiments = sorted(data_sentiments.items(), \
                key=lambda x: x[1][tpars[0]]["neu"], reverse=True)
    ndate = datetime.datetime.now()
    d = datetime.timedelta(days=7)
    sdate = ndate-d
    ndate = ndate.strftime("%Y-%m-%d")
    sdate = sdate.strftime("%Y-%m-%d")
    return render_template("index.html", alltopics=alltopics, tpars=tpars, rsearch=rsearch,
                            data=None, estados=estados, int=int,
                            data_sentiments=data_sentiments, data_scores=data_scores,
                            data_ranks=data_ranks, temas=alltopics, sdate=sdate, ndate=ndate,
                            last_data_scores=last_data_scores, last_data_ranks=last_data_ranks)

@app.route("/")
@app.route("/<pars>")
@app.route("/index")
@app.route("/index/")
@app.route("/index/<pars>")
def index(pars=None):
    if not session.get("username",None):return redirect("/login")
    if pars == "favicon.ico":
        return redirect(url_for('static', filename='favicon.ico'))
    reader = csv.reader(open("./utils/formato_estados.csv"))
    _ = reader.next()
    estados = [(row[0],row[1]) for row in reader]
    temas = ["seguridad", "servicios", "salud", "economia"]

    try:
        tema, estado = tuple(pars.split("-"))
    except:
        tema, estado = "general", None
    destados = dict(estados)
    scores = []
    keys = destados.values()
    keys.sort()
    for key in keys:
        temp  = get_public_scores_state(key)
        # promedio por entidad federativa
        temp[-1] = int(sum(temp[:-1])*100/len(temp[:-1]))/100.0
        scores.append((key,temp))
    ndate = datetime.datetime.now()
    sdate = ndate-datetime.timedelta(days=7)
    ndate = ndate-datetime.timedelta(days=1)
    ndate = ndate.strftime("%Y-%m-%d")
    sdate = sdate.strftime("%Y-%m-%d")
    proms = [0,0,0,0,0,0,0,0,0]
    for t in scores:
        for i in xrange(len(t[1])):
            proms[i]+=t[1][i]
    for i in xrange(len(t[1])):
        proms[i]/=len(scores)
        proms[i] = int(proms[i]*100)/100.0

    return render_template("public.html", scores=scores, \
            estados=estados, ndate=ndate, sdate=sdate, destados=destados, \
            proms=proms)


@app.route("/ranking")
@app.route("/ranking/")
@app.route("/ranking/<pars>")
def ranking(pars=None):
    if not session.get("username",None):return redirect("/login")
    if pars == "favicon.ico":
        return redirect(url_for('static', filename='favicon.ico'))
    reader = csv.reader(open("./utils/formato_estados.csv"))
    _ = reader.next()
    estados = [(row[0],row[1]) for row in reader]
    temas = ["seguridad", "servicios", "salud", "economia"]

    try:
        tema, estado = tuple(pars.split("-"))
    except:
        tema, estado = "general", None
    destados = dict(estados)
    if not tema: # or not estado:
        scores = get_general_sr()
        last_scores = get_general_sr_last()
    else: # both are given
        scores = get_general_sr(tema)
        last_scores = get_general_sr_last(tema)
    for i in xrange(len(scores)):
        scores[i][1]["last_score"] = last_scores[i][1]["score"]
        scores[i][1]["last_rank"] = last_scores[i][1]["rank"]

    if not estado:pass
    else: estado=destados[estado]; tema=tema.capitalize()
    """
    scores, ranks = get_ranked_news()
    data_scores, data_ranks = {}, {}
    for state in scores:
        data_scores[state] = scores[state][tema.lower()]
    data_scores = sorted(data_scores.items(), key=operator.itemgetter(1), reverse=True)
    for state in ranks:
        data_ranks[state] = int(ranks[state][tema.lower()])
    data_ranks = sorted(data_ranks.items(), key=operator.itemgetter(1))
    rank_data = []
    for i in range(len(data_ranks)):
        rank_data.append((data_ranks[i][0],data_ranks[i][1],data_scores[i][1]))
    """
    ndate = datetime.datetime.now()
    d = datetime.timedelta(days=7)
    sdate = ndate-d
    ndate = ndate.strftime("%Y-%m-%d")
    sdate = sdate.strftime("%Y-%m-%d")
    return render_template("ranking_combinado.html", scores=scores, \
            tema=tema, estado=estado, topic=tema.lower(), \
            temas=temas, estados=estados, ndate=ndate, sdate=sdate,\
            last_scores=last_scores, int=int)

@app.route("/noticias")
@app.route("/noticias/<pars>")
def noticias(pars=None):
    if not session.has_key("username"):return redirect("/login")
    if pars == "favicon.ico":
        return redirect(url_for('static', filename='favicon.ico'))
    reader = csv.reader(open("./utils/formato_estados.csv"))
    _ = reader.next()
    estados = [(row[0],row[1]) for row in reader]
    temas = ["seguridad", "servicios", "salud", "economia"]

    try:
        tema, estado = tuple(pars.split("-"))
    except:
        tema, estado = "general", None
    destados = dict(estados)
    if not tema or not estado:
        noticias = get_news_data()
    else: # both are given
        noticias = get_news_data(tema, destados[estado])
    if not estado:pass
    else: estado=destados[estado]; tema=tema.capitalize()

    scores, ranks = get_ranked_news()
    last_scores, last_ranks = get_ranked_news_last()
    data_scores, data_ranks = {}, {}
    last_data_scores, last_data_ranks = {}, {}
    for state in scores:
        data_scores[state] = scores[state][tema.lower()]
        last_data_scores[state] = last_scores[state][tema.lower()]
    data_scores = sorted(data_scores.items(), key=operator.itemgetter(1), reverse=True)
    for state in ranks:
        data_ranks[state] = int(ranks[state][tema.lower()])
        last_data_ranks[state] = int(last_ranks[state][tema.lower()])
    data_ranks = sorted(data_ranks.items(), key=operator.itemgetter(1))
    rank_data = []
    last_rank_data = []
    for i in range(len(data_ranks)):
        rank_data.append((data_ranks[i][0],data_ranks[i][1],data_scores[i][1]))
        last_rank_data.append((data_ranks[i][0],\
                last_data_ranks[data_ranks[i][0]],\
                last_data_scores[data_ranks[i][0]]))
    ndate = datetime.datetime.now()
    sdate = ndate-datetime.timedelta(days=7)
    ndate = ndate-datetime.timedelta(days=1)
    ndate = ndate.strftime("%Y-%m-%d")
    sdate = sdate.strftime("%Y-%m-%d")
    return render_template("noticias.html",noticias=noticias, \
            tema=tema, estado=estado, topic=tema.lower(),\
            temas=temas, estados=estados, rank_data=rank_data,\
            sdate=sdate, ndate=ndate, last_rank_data=last_rank_data,\
            xrange=xrange, len=len, int=int)




@app.route("/_indicadores")
@app.route("/_indicadores/<pars>")
@app.route("/_indicadores/<pars>/<dfrom>/<dto>")
def mapas(pars=None,dfrom=None,dto=None):
    if not session.has_key("username"):return redirect("/login")
    if "favicon.ico" in request.url:
        return redirect(url_for('static', filename='favicon.ico'))
    reader = csv.reader(open("./utils/formato_estados.csv"))
    _ = reader.next()
    estados = [(row[0],row[1]) for row in reader]
    temas = ["seguridad", "servicios", "salud", "economia"]

    if pars and len(pars.split("-"))==2:
        tema, estado = tuple(pars.split("-"))
    elif pars and "-" in pars:
        tema, estado = "general", pars.strip("-")
    else: tema, estado = None, None

    destados = dict(estados)
    if not estado:
        geotweet = []
        timeline_scores = []
        mean_timeline_positions = []
        timeline_positions = []
        top_words = []
        geo_center = {"lon":-99.14651,"lat":19.41125}
        sdate=None
        ndate=None
    else: # both are given
        # scores
        # timeline_scores = get_last_scores_state(estado)
        if not dfrom or not dto:
            if tema and tema!="general":
                timeline_scores, mean_timeline_positions = get_last_scores_state_category(destados[estado],tema)
                timeline_positions = get_last_positions_state_category(destados[estado],tema)
		# palabras frecuentes
                top_words = get_frec_terms(destados[estado],tema)
            else:
                timeline_scores, mean_timeline_positions = get_last_scores_state_category(destados[estado],None)
                timeline_positions = get_last_positions_state_category(destados[estado],None)
                # palabras frecuentes
                top_words = get_frec_terms(destados[estado],None)
                tema = "general"
            # tweets
            geotweet,geo_center = get_geolocated_tweets_data(estado)
            ndate = datetime.datetime.now()
            d = datetime.timedelta(days=30)
            sdate = ndate-d
            ndate = ndate.strftime("%Y-%m-%d")
            sdate = sdate.strftime("%Y-%m-%d")
        else:
            if tema and tema!="general":
                 timeline_scores, mean_timeline_positions = get_last_scores_state_category(destados[estado],tema,dfrom,dto)
                 timeline_positions = get_last_positions_state_category(destados[estado],tema,dfrom,dto)
                 # palabras frecuentes
                 top_words = get_frec_terms(destados[estado],tema,dfrom,dto)
            else:
                 timeline_scores, mean_timeline_positions = get_last_scores_state_category(destados[estado],None,dfrom,dto)
                 timeline_positions = get_last_positions_state_category(destados[estado],None,dfrom,dto)
                 # palabras frecuentes
                 top_words = get_frec_terms(destados[estado],None,dfrom,dto)
                 tema="general"
            # tweets
            geotweet,geo_center = get_geolocated_tweets_data(estado,dfrom,dto)
            sdate=dfrom[-4:]+"-"+dfrom[:2]+"-"+dfrom[2:4]
            ndate=dto[-4:]+"-"+dto[:2]+"-"+dto[2:4]
        timeline_scores = [(item[0], item[1], item[2].split("-")[-1]) for item in timeline_scores]
        geo_center = {"lon":-99.14651,"lat":19.41125}
    if not estado:pass
    else: estadoid=estado;estado=destados[estado]; tema=tema.capitalize()
    geotweet = geotweet[:10]
    return render_template("mapas.html",geotweet=geotweet, top_words=top_words, \
            tema=tema, geo_center=geo_center, estado=estado, \
            temas=temas, estados=estados,timeline_scores=timeline_scores, \
            sdate=sdate, ndate=ndate, timeline_positions=timeline_positions,\
            mean_timeline_positions=mean_timeline_positions)

@app.route("/usuarios")
@app.route("/usuarios/<pars>")
def usuarios(pars=None):
    if not session.has_key("username"):return redirect("/login")
    reader = csv.reader(open("./utils/formato_estados.csv"))
    _ = reader.next()
    estados = [(row[0],row[1]) for row in reader]
    temas = ["seguridad", "servicios", "salud", "economia"]

    try:
        tema, estado = tuple(pars.split("-"))
    except:
        tema, estado = None, None
    destados = dict(estados)
    if not tema or not estado:
        top_users = []
    else: # both are given
        # users
        if tema == "general":
            top_users = []
            for t in temas:
                top_users.extend(get_top_users(destados[estado],t))
                top_users = sorted(top_users.__iter__(), \
                        key=lambda x: x[-1], reverse=True)
                added_users = []
                temp = []
                for item in top_users:
                    if not len(added_users) < 10: break
                    if item[1]["screen_name"] in added_users:continue
                    added_users.append(item[1]["screen_name"])
                    temp.append(item)
                top_users=temp
        else:
            top_users = get_top_users(destados[estado],tema)
    if not estado:pass
    else: estadoid=estado;estado=destados[estado]; tema=tema.capitalize()

    return render_template("usuarios.html", top_users=top_users, \
            tema=tema, estado=estado, \
            temas=temas, estados=estados)

@app.route("/reportes")
@app.route("/reportes/<pars>")
def reporte(pars=None):
    if not session.has_key("username"):return redirect("/login")
    if 'favicon.ico' in request.url: return redirect(url_for('static', filename='favicon.ico'))
    reader = csv.reader(open("./utils/formato_estados.csv"))
    _ = reader.next()
    estados = [(row[0],row[1]) for row in reader]
    temas = ["seguridad", "servicios", "salud", "economia"]
    destados = dict(estados)
    tema, estado = None, None
    # -----------------------
    if not pars:
	pass
        #flash("Debe seleccionar un estado.","error")
    elif "-" not in pars.strip("-"):
        estado = pars.strip("-")
        if not state_available(estado): flash(not_available_msg,"error"); return redirect(url_for(request.endpoint))
        create_general_report(estado, destados)
        flash("Reporte general en proceso: %s. Este tardara alrededor de 5 min en realizarse."%destados[estado],"info")
        return redirect(url_for('reporte'))
    else: # '-' in pars
        tema, estado = tuple(pars.split("-"))
        if not state_available(estado): flash(not_available_msg,"error"); return redirect(url_for(request.endpoint))
        # create_report(destados[estado], tema)
        flash("Reporte en proceso para: %s/%s. Este tardara alrededor de 5 min en realizarse."%(destados[estado],tema),"info")
        return redirect(url_for('reporte'))
    # checking reports
    timestamp = str(datetime.datetime.now()).split()[0]
    exists_gral_report = glob.glob('./utils/r/reporte_*_{0}.html'.format(timestamp))
    exists_gral_report = [(destados[item.split("_")[-2]], item.split("/")[-1]) \
				for item in exists_gral_report]
    exists_report = False
    return render_template("reporte.html", exists_grep=exists_gral_report, \
            temas=temas, estados=estados)

@app.route("/corrs")
@app.route("/corrs/<pars>")
def corrs(pars=None):
    if not session.has_key("username"):return redirect("/login")
    if pars and not state_available(pars): flash(not_available_msg,"error"); return redirect(url_for(request.endpoint))
    if 'favicon.ico' in request.url: return redirect(url_for('static', filename='favicon.ico'))
    reader = csv.reader(open("./utils/formato_estados.csv"))
    _ = reader.next()
    estados = [(row[0],row[1]) for row in reader]
    destados = dict(estados)
    # loading static data
    fr = open("data/redes_vs_news.csv","r")
    rnheaders = fr.readline().strip("\n").split(",")
    redes_news = []
    for line in fr:
        redes_news.append(line.strip("\n").split(','))
    # ---
    dateformat = (datetime.datetime.utcnow().replace(day=1) - datetime.timedelta(days=60)).strftime("%m-%Y")
    if pars and pars in destados:
        return render_template("correlaciones.html", estados=estados, indicador="rn",
                estado=pars, rnheaders=rnheaders, redes_news=redes_news, dateformat=dateformat)
    else:
        return render_template("correlaciones.html", estados=estados, indicador="rn", dateformat=dateformat)

@app.route("/corrs-inegi")
@app.route("/corrs-inegi/<pars>")
def corrs_inegi(pars=None):
    if not session.has_key("username"):return redirect("/login")
    if pars and not state_available(pars): flash(not_available_msg,"error"); return redirect(url_for(request.endpoint))
    if 'favicon.ico' in request.url: return redirect(url_for('static', filename='favicon.ico'))
    reader = csv.reader(open("./utils/formato_estados.csv"))
    _ = reader.next()
    estados = [(row[0],row[1]) for row in reader]
    destados = dict(estados)
    # loading static data
    fr = open("data/inegi_redes.csv","r")
    headers = fr.readline().strip("\n").split(",")
    inegi_redes = []
    for line in fr:
        inegi_redes.append(line.strip("\n").split(','))
    # ---
    forecasts_headers = {
            0:"Fechas",
            1:"Actividad industrial nacional",
            2:"Construccion nacional",
            3:"Manufacturas nacional",
            4:"Mineria nacional",
            5:"Generacion luz y agua nacional",
            6:"Media nacional inflacion",
            7:"Indice desempleo nacional",
            8:"Tipo cambio",
            9:"Indice nacional precios consumidor"
            }
    # ---
    dateformat = (datetime.datetime.utcnow().replace(day=1) - datetime.timedelta(days=60)).strftime("%m-%Y")
    if pars and pars in destados:
        return render_template("correlaciones.html", estados=estados, indicador="ir",
                estado=pars, rnheaders=headers, redes_news=inegi_redes,
                forecasts_headers=forecasts_headers, dateformat=dateformat)
    else:
        return render_template("correlaciones.html", estados=estados, indicador="ir",
                forecasts_headers=forecasts_headers, dateformat=dateformat)




@app.route("/org-corrs/<tipo>/")
@app.route("/org-corrs/<tipo>/<pars>")
def corrsexp(tipo=None,pars=None):
    if pars and tipo:
        return render_template("correxplorer.html", estado=pars, tipo=tipo)
    else:
        return ''


@app.route("/ppublicas")
@app.route("/ppublicas/<pars>")
@app.route("/ppublicas/<pars>/<dfrom>/<dto>")
def ppublicas(pars=None,dfrom=None,dto=None):
    if not session.has_key("username"):return redirect("/login")
    if "favicon.ico" in request.url:
        return redirect(url_for('static', filename='favicon.ico'))
    reader = csv.reader(open("./utils/formato_estados.csv"))
    _ = reader.next()
    estados = [(row[0],row[1]) for row in reader]
    destados = dict(estados)
    temas = [ \
            "seguridad","servicios","salud","economia", \
            "presidente", "gobernador", \
            "gobierno", "obra.publica", \
            "pavimentacion", "recoleccion.basura", "servicio.agua", \
            "transporte.publico","legislativo", "judicial"]

    if pars and len(pars.split("-"))==2:
        tema, estado = tuple(pars.split("-"))
    elif pars and "-" in pars:
        tema, estado = "general", pars.strip("-")
    else: tema, estado = None, None

    if not tema or not estado:
        noticias = get_news_data()
    else: # both are given
        noticias = get_news_data(tema, destados[estado])

    destados = dict(estados)
    sdate_anterior = None
    ndate_anterior = None
    if not estado:
        mean_timeline_scores = []
        timeline_scores = []
        mean_timeline_positions = []
        timeline_positions = []
        sdate=None
        ndate=None
        score=0
        rank=0
        score_anterior = 0
        rank_anterior = 0
    else: # both are given
        # scores
        # timeline_scores = get_last_scores_state(estado)
        if not dfrom or not dto:
            sdate_anterior = datetime.datetime.now()-datetime.timedelta(days=14)
            ndate_anterior = datetime.datetime.now()-datetime.timedelta(days=7)
            sdate_anterior = sdate_anterior.strftime("%Y-%m-%d")
            ndate_anterior = ndate_anterior.strftime("%Y-%m-%d")
            if tema and tema!="general":
                score, timeline_scores, mean_timeline_scores = get_last_scores_state_category_pp(destados[estado],tema)
                score_anterior, _, _ = get_last_scores_state_category_pp(destados[estado],tema,sdate_anterior,ndate_anterior)
                rank_anterior, _, _ = get_last_ranks_state_category_pp(destados[estado],tema,sdate_anterior,ndate_anterior)
                rank, timeline_positions, mean_timeline_positions = get_last_ranks_state_category_pp(destados[estado],tema)
            else:
                score, timeline_scores, mean_timeline_scores = get_last_scores_state_category_pp(destados[estado],None)
                score_anterior, _, _ = get_last_scores_state_category_pp(destados[estado],None,sdate_anterior,ndate_anterior)
                rank, timeline_positions, mean_timeline_positions = get_last_ranks_state_category_pp(destados[estado],None)
                rank_anterior, _, _ = get_last_ranks_state_category_pp(destados[estado],None,sdate_anterior,ndate_anterior)
                # palabras frecuentes
                tema = "general"
            ndate = datetime.datetime.now()
            d = datetime.timedelta(days=7)
            sdate = ndate-d
            ndate = ndate-datetime.timedelta(days=1)
            ndate = ndate.strftime("%Y-%m-%d")
            sdate = sdate.strftime("%Y-%m-%d")
        else:
            sdate_anterior = datetime.datetime.now()-datetime.timedelta(days=14)
            ndate_anterior = datetime.datetime.now()-datetime.timedelta(days=7)
            sdate_anterior = sdate_anterior.strftime("%Y-%m-%d")
            ndate_anterior = ndate_anterior.strftime("%Y-%m-%d")
            if tema and tema!="general":
                 score, timeline_scores, mean_timeline_scores = get_last_scores_state_category_pp(destados[estado],tema,dfrom,dto)
                 score_anterior, _, _ = get_last_scores_state_category_pp(destados[estado],tema,sdate_anterior,ndate_anterior)
                 rank, timeline_positions = get_last_ranks_state_category_pp(destados[estado],tema,dfrom,dto)
                 rank_anterior, _, _ = get_last_ranks_state_category_pp(destados[estado],tema,sdate_anterior,ndate_anterior)
            else:
                 score, timeline_scores, mean_timeline_scores = get_last_scores_state_category_pp(destados[estado],None,dfrom,dto)
                 score_anterior, _, _ = get_last_scores_state_category_pp(destados[estado],None,sdate_anterior,ndate_anterior)
                 rank, timeline_positions, mean_timeline_positions = get_last_ranks_state_category_pp(destados[estado],None,dfrom,dto)
                 rank_anterior, _, _ = get_last_ranks_state_category_pp(destados[estado],None,sdate_anterior,ndate_anterior)
                 tema="general"
            sdate=dfrom[-4:]+"-"+dfrom[:2]+"-"+dfrom[2:4]
            ndate=dto[-4:]+"-"+dto[:2]+"-"+dto[2:4]
        timeline_scores = [(item[0], item[1], item[2].split("-")[-1]) for item in timeline_scores]
    if not estado:pass
    else: estadoid=estado;estado=destados[estado]; tema=tema.capitalize()
    return render_template("ppublicas.html", int=int, noticias=noticias, destados=destados, \
            tema=tema, estado=estado, score=score, rank=rank, \
            temas=temas, estados=estados, timeline_scores=timeline_scores, \
            sdate=sdate, ndate=ndate, timeline_positions=timeline_positions,\
            mean_timeline_positions=mean_timeline_positions, \
            mean_timeline_scores=mean_timeline_scores, \
            score_anterior=score_anterior, rank_anterior=rank_anterior)



######################################
################# API ################
######################################

@app.route("/api/getFrecTerms/<state>/<cat>/<pol>")
def get_frec_terms_pol(state=None,cat=None,pol=None):
    pol = pol.lower().strip('s')
    cat = cat.lower()
    if cat=="neutros":cat=="general"
    data = get_frec_terms(state,cat,pol)
    return json.dumps(data)


@app.route("/api/score/states/<estado>/<tema>")
def score_states(estado=None,tema=None):
    if not session.has_key("username"):return "[/* No active session */]"
    reader = csv.reader(open("./utils/formato_estados.csv"))
    _ = reader.next()
    estados = dict([(row[0],row[1]) for row in reader])
    return json.dumps(get_state_timeline(estados[estado], tema))

@app.route("/api/corrs/<tipo>/<escode>")
def coors_redes_news(escode=None, tipo=None):
    if not session.has_key("username"):return "[/* No active session */]"
    if not escode: return ""
    else: escode = escode.split('.')[0]
    # ----
    si = StringIO.StringIO()
    si.write(get_corrs_from_api(escode, tipo))
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=%s-%s.csv"%(tipo,escode)
    output.headers["Content-type"] = "text/csv"
    return output

@app.route("/api/forecasts/<index>")
def forecasts(index):
    forecasts_headers = {
            0:"Fechas",
            1:"Actividad industrial nacional",
            2:"Construccion nacional",
            3:"Manufacturas nacional",
            4:"Mineria nacional",
            5:"Generacion luz y agua nacional",
            6:"Media nacional inflacion",
            7:"Indice desempleo nacional",
            8:"Tipo cambio",
            9:"Indice nacional precios consumidor"
            }
    data = get_forecasts(index)
    return json.dumps(data)


@app.route("/api/ppublicas/<tema>/<estado>/<dia>")
def ppublicas_values(tema=None,estado=None,dia=None):
    ndate = datetime.datetime.now()
    d = datetime.timedelta(days=7-int(dia))
    sdate = ndate-d
    ndate = ndate.strftime("%Y-%m-%d")
    sdate = sdate.strftime("%Y-%m-%d")
    data = {
            "hashtags":[],
            "tweets":[]
            }
    hashtags = get_ppublic_hashtags(tema.lower(),estado,sdate)
    max_size = 0.0
    for item in hashtags:
        if max_size < item[1]:
            max_size = float(item[1])
    for item in hashtags:
        data["hashtags"].append({"text":item[0],"size":int((item[1]/max_size)*70)+1})
    # tweets
    tweets = get_ppublic_tweets(tema.lower(),estado,sdate)
    for tweet in tweets:
        data["tweets"].append({"text":tweet[0],"score":int(tweet[1]*100)/100.0})
    return json.dumps(data)

######## EXPORTS
import StringIO, csv

@app.route("/export/ppublicas")
def export_ppublicas():
    si = StringIO.StringIO()
    cw = csv.writer(si)
    headers = ("Date", "Estado", "Score", "Rank", "Score Gobernador", "Rank Gobernador", \
            "Score Presidente", "Rank Presidente", "Score Gobierno", "Rank Gobierno", \
            "Score Obra Publica", "Rank Obra Publica", "Score Pavimentacion", "Rank Pavimentacion", \
            "Score Recoleccion Basura", "Rank Recoleccion Basura", "Score Servicio Agua", \
            "Rank Servicio Agua", "Score Transporte Publico", "Rank Transporte Publico", \
            "Score Legislativo", "Rank Legislativo", "Score Judicial", "Rank Judicial")
    cw.writerows([headers])
    cw.writerows(export_data_pp())
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=Politicas-Publicas.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route("/export/rcombinado")
def export_rankings():
    si = StringIO.StringIO()
    cw = csv.writer(si)
    headers = ("Id Semana", "Anno", "Semana", "Estado", "Score", "Rank", "Score Salud", "Rank Salud", \
            "Score Economia", "Rank Economia", "Score Seguridad", "Rank Seguridad", \
            "Score Servicios", "Rank Servicios", "Score Gobernador", "Rank Gobernador", \
            "Score Presidente", "Rank Presidente", "Score Gobierno", "Rank Gobierno", \
            "Score Obra Publica", "Rank Obra Publica", "Score Pavimentacion", "Rank Pavimentacion", \
            "Score Recoleccion Basura", "Rank Recoleccion Basura", "Score Servicio Agua", "Rank Servicio Agua", \
            "Score Transporte Publico", "Rank Transporte Publico", \
            "Score Legislativo", "Rank Legislativo", "Score Judicial", "Rank Judicial")
    cw.writerows([headers])
    # construyes los ids de las semanas del mes que quieres
    cw.writerows(export_data_rankings())
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=Ranking-Combinado.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route("/export/scores")
def export_scores():
    si = StringIO.StringIO()
    cw = csv.writer(si)
    headers = ("Date", "Estado", "Score", "Rank", "Score Salud", "Rank Salud", \
            "Score Economia", "Rank Economia", "Score Seguridad", "Rank Seguridad", \
            "Score Servicios", "Rank Servicios")
    cw.writerows([headers])
    cw.writerows(export_data_scores())
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=Ranking-Social.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route("/export/rnoticias")
def export_noticiass():
    si = StringIO.StringIO()
    cw = csv.writer(si)
    headers = ("Anno", "Mes", "Semana", "Id Semana", "Estado", "Score", "Rank", "Score Salud", "Rank Salud", \
            "Score Economia", "Rank Economia", "Score Seguridad", "Rank Seguridad", \
            "Score Servicios", "Rank Servicios", "Score Diputado", "Rank Diputado", \
            "Score Gobernador", "Rank Gobernador", "Score Gobierno", "Rank Gobierno", \
            "Score Juez", "Rank Juez", \
            "Score Obra Publica", "Rank Obra Publica", "Score Pavimentacion", "Rank Pavimentacion", \
            "Score Presidente", "Rank Presidente", \
            "Score Recoleccion Basura", "Rank Recoleccion Basura", "Score Servicio Agua", "Rank Servicio Agua", \
            "Score Transporte Publico", "Rank Transporte Publico")
    cw.writerows([headers])
    cw.writerows(export_data_noticias())
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=Ranking-Noticias.csv"
    output.headers["Content-type"] = "text/csv"
    return output

######## REPORTES

@app.route("/reporte/<filename>")
def ver_reporte(filename=None):
    if not filename: return "nothing to see here... :("
    return open("utils/r/{}".format(filename),"r").read()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0",	port=5000)
#    context = ('host.crt', 'host.key')
#    app.run(host='0.0.0.0', port=80, ssl_context=context, threaded=True, debug=True)





















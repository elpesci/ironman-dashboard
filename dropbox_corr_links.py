import requests
import urllib2
import csv
import dropbox

# values from dropbox
access_token = "yNZCtRWG-wAAAAAAAAAAN5b4rtO6GvqMwCKJCkrjgZpuq_vTlpcjNMnUX2VKb3A3"
dbx = dropbox.Dropbox(access_token)


# format data

reader = csv.reader(open("./utils/formato_estados.csv"))
_ = reader.next()
destados = dict([(row[0],row[1]) for row in reader])

dropbox_corr_links = {
        "AS":"svisl4k1o7u50ec",
        "BCS":"nwzg91v5xtweeaj",
        "BC":"jbokv4530y818t8",
        "CC":"u3kw9ple0h07nq3",
        "CS":"xt38jikags6ykhw",
        "CH":"tp317m2rqgbfnvn",
        "CL":"4r0oaampg6ij14v",
        "CM":"r5ygk43hby37du2",
        "DF":"jb1y0ha9puln4wd",
        "DG":"uzn7khtqobgl7j2",
        "GT":"djmhm50jb10jbju",
        "EM":"bbigmdt2c84lgjt",
        "GUER":"m518k5nn2zj8v2k",
        "HG":"3zg264kvc3bw1g8",
        "JAL":"ba54esbi3iiblmf",
        "MS":"f28ablvygza7df0",
        "MN":"qkdfvnzgh39cs20",
        "NT":"6n9n9j8olwnyjdq",
        "MTY":"47j4ubbdg8ro50m",
        "OC":"99yokqvabbyqwdt",
        "PL":"ma8ojwwugfz1p2v",
        "QR":"ilo38ximvlosc4w",
        "QT":"xexhmgni5322kck",
        "SP":"94lqugylervfo3w",
        "SIN":"wc5esotq0045osl",
        "SN":"o55qp6jy3bvsjgx",
        "TC":"907f468tczgzx44",
        "TS":"r82z73ndfu7o6ae",
        "TL":"14lx24nasjbjesq",
        "VZ":"ynf60ajj43vay32",
        "YN":"2y1r27pzwggnm3v",
        "ZS":"qls0jm6sfn95qlc"
        }

def get_corrs_from_dropbox(state):
    url = "https://www.dropbox.com/s/{1}/correlaciones_mensuales_redes_vs_news_{0}.csv?dl=1".\
                format(destados[state].lower(),dropbox_corr_links[state])

    response = urllib2.urlopen(url)
    cr = csv.reader(response)

    for row in cr:
        print row


def get_corrs_from_api(state,tipo):
    if tipo=="rn":
        filename = "/redes_vs_news/correlaciones_mensuales_redes_vs_news_{0}.csv".\
            format(destados[state].lower().replace(' ','_'))
    else: # =="ir"
        filename = "/inegi/correlaciones_mensuales_inegi_redes_{0}.csv".\
            format(destados[state].lower().replace(' ','_'))
    print "trying to fetch:", filename
    # csvr = csv.reader(dbx.files_download(filename)[1])
    return dbx.files_download(filename)[1].text
    #          :o
    data = data.split('\n')
    for row in data:
        print row.split(',')


if __name__=="__main__":
    # get_corrs_from_state("QT")
    #get_corrs_from_dropbox("QT")
    get_corrs_from_api("QT")




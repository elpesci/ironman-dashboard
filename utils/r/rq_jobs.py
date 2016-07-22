#! /usr/bin/python
import os
import datetime

### Here are the rq jobs (R scripts mainly)


def run_general_report(estado, destados):
    ## R scripts here...
    # R -e "estado='Nuevo Leon'; rmarkdown::render('get_reporteGral.Rmd')"
    os.chdir("/home/ubuntu/dashboard/utils/r/")
    timestamp = str(datetime.datetime.now()).split()[0]
    command = 'cp reporteTotal.Rmd reporte_{0}_{1}.Rmd'.format(\
                    estado, timestamp)
    os.system(command)
    command = "R -e \"estado='{0}';rmarkdown::render('reporte_{1}_{2}.Rmd')\"".format(\
                                destados[estado], estado, timestamp)
    print "### R command:", command
    os.system(command)


def run_report(estado,tema):
    # R scripts here...
    return None


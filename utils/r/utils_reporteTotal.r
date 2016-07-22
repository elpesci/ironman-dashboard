############################### UTILS MOTHAFUCK´N GOOD #######################################

###################################################################################
#       GET RANK
###################################################################################
Rank <- function(estado){
  library(RMySQL)
  library(lubridate)
  library(stringr)
  library(RCurl)
  library(dplyr)
  library(tidyr)
  library(knitr)
  library(Rstem)
  library(irlba)
  library(Matrix)
  library(tm)
  library(ggplot2)
  library(rCharts)
  library(ggmap)
  library(mapproj)
  library(gridExtra)
  library(png)
  library(grid)
  library(rMaps)
  library(tmcn.word2vec)
  library(RTextTools)
  library(topicmodels)
  library(wordcloud)
  library(topicmodels)
  library(ggthemes)
  library(RPostgreSQL)
  library(slam)
  library(reshape2)
  drv <- dbDriver("PostgreSQL")
  con <- dbConnect(drv, host="postgres.cvbe158gtbog.us-west-2.rds.amazonaws.com",
                   port="5432",
                   dbname="postgres",
                   user = 'smcp',
                   password = 'smcp1234')
  
  part_query <- "select * from \"tb4\""
  #query de categoria
  edo_pre <- sprintf("'%s'", estado)
  #query final
  query <- paste(part_query,"where estado =",edo_pre ,";")
  #hacer query con la categoría y estado selecionado
  rs <- dbSendQuery(con, query)
  dframe <- fetch(rs,n=-1)
  dbDisconnect(con) 
  #regresa el rank del día
  edo_rank <- dframe %>% 
    arrange(desc(date_created)) %>%
    head(1) %>% 
    gather(concepto, puntuacion, -date_created, -estado) %>% 
    filter(str_detect(concepto,'rank')) %>% 
    select(concepto, puntuacion) 
  
  edo_rank
  
}

###################################################################################
#     OBTENER EL PERFORMANCE DE TODOS LOS INDICADORES DE UN ESTADO
###################################################################################


Performance <- function(estado){
  library(RMySQL)
  library(lubridate)
  library(stringr)
  library(RCurl)
  library(dplyr)
  library(tidyr)
  library(Rstem)
  library(irlba)
  library(Matrix)
  library(tm)
  library(gridExtra)
  library(grid)
  library(RPostgreSQL)
  drv <- dbDriver("PostgreSQL")
  con <- dbConnect(drv, host="postgres.cvbe158gtbog.us-west-2.rds.amazonaws.com",
                   port="5432",
                   dbname="postgres",
                   user = 'smcp',
                   password = 'smcp1234')
  #####tabla con los nombres de los estados   
  part_query <- "select * from \"tb4\""
  
  #query de categoria
  edo_query <- sprintf("'%s'", estado)
  
  #fecha
  fecha_inicio <- sprintf("'%s'",  as.character(as.Date(format(Sys.time(), "%Y-%m-%d"))-7))
  fecha_final <- sprintf("'%s'", as.character(as.Date(format(Sys.time(), "%Y-%m-%d"))))
  #query final
  #query <- paste(part_query,step_estado,"where categoria =",cat_pre ,";")
  query <- paste(part_query,"where estado =",edo_query,"and",
                 "date_created >=",fecha_inicio, "and",
                 "date_created <=", fecha_final,
                 ";")
  ###########
  
  #hacer query con la categoría y estado selecionado
  rs <- dbSendQuery(con, query)
  #score <- as.character(paste("score_", categoria, sep = "", collapse = NULL))
  #dframe <- fetch(rs,n=-1) 
  dframe <- fetch(rs,n=-1) %>%
    gather(concepto, puntuacion, -date_created, -estado) %>%
    filter(str_detect(concepto,'score')) 
  #dbClearResult(rs)
  dbDisconnect(con)  
  
  dframe
}


###################################################################################
#     OBTENER LAS PALABRAS CLAVE DE TODAS LAS CATEGORÍAS DEL ESTADO
###################################################################################

TopWords <- function(estado){
  library(RMySQL)
  library(lubridate)
  library(stringr)
  library(RCurl)
  library(dplyr)
  library(tidyr)
  library(knitr)
  library(Rstem)
  library(irlba)
  library(Matrix)
  library(tm)
  library(ggplot2)
  library(rCharts)
  library(ggmap)
  library(mapproj)
  library(gridExtra)
  library(png)
  library(grid)
  library(rMaps)
  library(tmcn.word2vec)
  library(RTextTools)
  library(topicmodels)
  library(wordcloud)
  library(topicmodels)
  library(ggthemes)
  library(RPostgreSQL)
  library(slam)
  library(reshape2)
  library(textcat)
  drv <- dbDriver("PostgreSQL")
  con <- dbConnect(drv, host="postgres.cvbe158gtbog.us-west-2.rds.amazonaws.com",
                   port="5432",
                   dbname="postgres",
                   user = 'smcp',
                   password = 'smcp1234')
  #####tabla con los nombres de los estados 
  #NOTA: HAY QUE CAMBIAR POR EL ARCHIVO QUE ESTÁ EN EL SERVER QUE CORRESPONDE A ESTA TABLA
  #
  tabla_estados <- read.csv("/home/ubuntu/dashboard/reportes/utils_reporte/tabla_cruce.csv")
  tabla_estados <- tabla_estados %>%
    select(estado,estado.1)
  colnames(tabla_estados) <- c("id", "estados")
  #get id del estado
  id_estado <- filter(tabla_estados, estados == as.character(estado))
  id_estado1 <- id_estado[1,1]
  edo <- id_estado1  
  #query de estado 
  tabla_estado <- "tbl_topWords"
  step_estado <- sprintf("\"%s\"", tabla_estado)
  part_query <- "select * from "
  edo <- sprintf("'%s'", estado)
  
  #query de categoria
  #cat_pre <- sprintf("'%s'", categoria)
  #fecha
  fecha_inicio <- sprintf("'%s'",  as.character(as.Date(format(Sys.time(), "%Y-%m-%d"))-7))
  fecha_final <- sprintf("'%s'", as.character(as.Date(format(Sys.time(), "%Y-%m-%d"))))
  #query final
  #query <- paste(part_query,step_estado,"where categoria =",cat_pre ,";")
  query <- paste(part_query,step_estado,"where estado = ",edo,"and date_created >=",fecha_inicio, "and date_created <=", fecha_final,";")
  
  #hacer query con la categoría y estado selecionado
  rs <- dbSendQuery(con, query)
  dframe <- fetch(rs,n=-1)
  dbDisconnect(con) 
  dframe <- dframe %>%
    mutate(lang = lapply(dframe$term, textcat)) %>%
    filter(lang != "scots", lang != "english") %>%
    select(-lang)
  df_top20 <- dframe %>%
    group_by(categoria) %>%
    arrange(desc(freq)) %>%
    distinct(term) %>% 
    top_n(n = 10, wt = freq)
  df_top20
  
}

###################################################################################
#     OBTENER EL MAPA DEL ESTADO
###################################################################################

Map <- function(estado){
  library(RMySQL)
  library(lubridate)
  library(stringr)
  library(RCurl)
  library(dplyr)
  library(tidyr)
  library(knitr)
  library(Rstem)
  library(irlba)
  library(Matrix)
  library(tm)
  library(ggplot2)
  library(rCharts)
  library(ggmap)
  library(mapproj)
  library(gridExtra)
  library(png)
  library(grid)
  library(rMaps)
  library(tmcn.word2vec)
  library(RTextTools)
  library(topicmodels)
  library(wordcloud)
  library(topicmodels)
  library(ggthemes)
  library(RPostgreSQL)
  library(slam)
  library(reshape2)
  drv <- dbDriver("PostgreSQL")
  con <- dbConnect(drv, host="postgres.cvbe158gtbog.us-west-2.rds.amazonaws.com",
                   port="5432",
                   dbname="postgres",
                   user = 'smcp',
                   password = 'smcp1234')
  #####tabla con los nombres de los estados 
  #NOTA: HAY QUE CAMBIAR POR EL ARCHIVO QUE ESTÁ EN EL SERVER QUE CORRESPONDE A ESTA TABLA
  tabla_estados <- read.csv("/home/ubuntu/dashboard/reportes/utils_reporte/tabla_cruce.csv")
  tabla_estados <- tabla_estados %>%
    select(estado,estado.1)
  colnames(tabla_estados) <- c("id", "estados")
  #get id del estado
  id_estado <- filter(tabla_estados, estados == as.character(estado))
  id_estado1 <- id_estado[1,1]
  edo <- id_estado1  
  #query de estado 
  tabla_estado <- paste("tb2",edo, sep ="_")
  step_estado <- sprintf("\"%s\"", tabla_estado)
  part_query <- "select * from "
  
  #query de categoria
  #cat_pre <- sprintf("'%s'", categoria)
  #fecha
  fecha_inicio <- sprintf("'%s'",  as.character(as.Date(format(Sys.time(), "%Y-%m-%d"))-7))
  fecha_final <- sprintf("'%s'", as.character(as.Date(format(Sys.time(), "%Y-%m-%d"))))
  #query final
  #query <- paste(part_query,step_estado,"where categoria =",cat_pre ,";")
  query <- paste(part_query,step_estado,"where date_created >=",fecha_inicio, "and",
                 "date_created <=", fecha_final,
                 ";")
  
  #hacer query con la categoría y estado selecionado
  rs <- dbSendQuery(con, query)
  dframe <- fetch(rs,n=-1)
  dbDisconnect(con) 
  #generar los datos para plotear en el mapa
  dfMaps <- dframe %>%
    select(lon, lat, polarizacion,categoria)
  dfMaps
  
}


###################################################################################
#     OBTENER LA TABLA DE CORRELACIÓN DEL ESTADO
###################################################################################


corTable <- function(estado){
  library(dplyr)
  library(httr)
  library(XML)
  library(inegiR)
  library(RCurl)
  library(zoo)
  library(reshape)
  #rm(list=ls(all = TRUE ))
  #gc(reset=TRUE)
  options(scipen=999)
  library(RMySQL)
  #library(plyr)
  library(RPostgreSQL)
  library(RMySQL)
  options(digits=4)
  library(forecast)
  library(xts)
  library(ggplot2)
  #library(clusterSim)
  #query 1
  db <-tbl(src_postgres(host="postgres.cvbe158gtbog.us-west-2.rds.amazonaws.com", 
                        port=5432,
                        dbname="postgres", 
                        user = 'smcp',
                        password = 'smcp1234'
  ), "tb4")
  # extraemos a un df
  db <- collect(db)
  twt<-db%>% 
    mutate(year = as.numeric(format(date_created, format = "%Y")),  
           month = as.numeric(format(date_created, format = "%m")))%>%
    mutate(Fechas=as.Date(paste(year,"-",month,"-","01",sep=""),"%Y-%m-%d"))%>%
    group_by(Fechas,estado)%>%
    summarise(score_salud=mean(score_salud),score_economia=mean(score_economia),score_seguridad=mean(score_seguridad),score_servicios=mean(score_servicios),score=mean(score))
  
  media_nac<-db%>% mutate(year = as.numeric(format(date_created, format = "%Y")),  
                          month = as.numeric(format(date_created, format = "%m")))%>%
    mutate(Fechas=as.Date(paste(year,"-",month,"-","01",sep=""),"%Y-%m-%d"))%>%
    group_by(Fechas)%>%
    summarise(score_salud=mean(score_salud),score_economia=mean(score_economia),score_seguridad=mean(score_seguridad),score_servicios=mean(score_servicios),score=mean(score))
  #nos desconectamos
  #dbDisconnect(con) 
  #se filtra por el estado
  edos<-as.data.frame(estado)
  ######################################transpose de los scores por categorias y estados
  for (i in 1:dim(edos)[1]){
    for (j in 3:7){
      subconjunto<-subset(twt,estado==edos[i,1])[j]
      cat<-colnames(subconjunto)
      colnames(subconjunto)<-c(paste(edos[i,1],cat,sep = "_"))
      media_nac<-cbind(media_nac,subconjunto)}
  }
  ##############################################    inegi mensual
  
  token<-"6691298a-289d-dcfb-38ee-87315be3d107"
  
  
  ###########################################################################  MENSUAL
  
  #Obtiene tasa de desocupación (serie unificada) urbana 
  #(agregado de 32 ciudades) /NACIONAL+MENSUAL
  
  Desempleo<-tasa_desempleo(token)   
  colnames(Desempleo)<-c("Indice_Desempleo_Nacional","Fechas")
  
  #2005-01-01:2015-10-01
  
  ###########Obtiene principales tasas de crecimiento  de componentes de Actividad Industrial (series originales):
  ###Construcción, Manufacturas, Minería y Generación de Luz y Agua.  NACIONAL/MENSUAL
  
  ActividadIndustrial<-series_actividad_industrial(token)
  ActividadIndustrial<-ActividadIndustrial[complete.cases(ActividadIndustrial),]
  colnames(ActividadIndustrial)<-c("Fechas", "Actividad_Industrial_Nacional",
                                   "Construccion_Nacional","Manufacturas_Nacional",
                                   "Mineria_Nacional","Generacion_LyA_Nacional")
  
  
  #################  TIPO DE CAMBIO MENSUAL
  tipodecambio<-series_tipocambio(token)
  colnames(tipodecambio)<-c("tipo_cambio","Fechas")
  
  mensual<-inner_join(ActividadIndustrial, Desempleo)
  mensual<-inner_join(mensual,tipodecambio)
  mensual<-inner_join(mensual,media_nac)
  #################inpc
  
  correlacion<-subset(mensual, select = -c(Fechas))
  #correlacion<-clusterSim::data.Normalization (as.matrix(correlacion),type="n1",normalization="column")
  ###########esto se cambia
  estandar <- function(x) {((x-mean(x))/sd(x))} 
  normed <- as.data.frame(lapply(correlacion, estandar)) 
  ##############
  correlacion<-as.data.frame(correlacion)
  correlacion_m<-as.data.frame(cor(correlacion))
  
  ######
  cor1<-ggplot(data = melt(cor(correlacion)), aes(X1, X2, fill = value))+
    geom_tile(color = "white")+
    scale_fill_gradient2(low = "blue", high = "red", mid = "white", 
                         midpoint = 0, limit = c(-1,1), space = "Lab", 
                         name="Correlación") +
    theme_minimal()+ 
    theme(axis.text.x = element_text(angle = 45, vjust = 1, 
                                     size = 12, hjust = 1))+
    coord_fixed()
  
  cor1
}

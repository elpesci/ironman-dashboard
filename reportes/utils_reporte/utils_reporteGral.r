###################################################################################
#
#     FUNCIONES PARA GENERAR EL REPORTE GENERAL, ES DECIR POR ESTADO
#
###################################################################################

######################################### obtener el ranking general
getG_rank <- function(estado){
  library(lubridate)
  library(stringr)
  library(RCurl)
  library(dplyr)
  library(tidyr)
  library(knitr)
  library(irlba)
  library(Matrix)
  library(tm)
  library(ggplot2)
  library(ggmap)
  library(mapproj)
  library(gridExtra)
  library(png)
  library(grid)
  library(RTextTools)
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
    select(rank)
  edo_rank
  
}

####################################### obtener el desempeño del indicador

getG_indicadorPerformance <- function(estado){
  library(RMySQL)
  library(lubridate)
  library(stringr)
  library(RCurl)
  library(dplyr)
  library(tidyr)
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
  dframe <- fetch(rs,n=-1) %>%
    select(date_created, score)
  #dbClearResult(rs)
  dbDisconnect(con)  
  
  dframe
}

###################################### TOP WORDS ###########################

getG_topWords <- function(estado){
  library(lubridate)
  library(stringr)
  library(RCurl)
  library(dplyr)
  library(tidyr)
  library(knitr)
  library(irlba)
  library(Matrix)
  library(tm)
  library(ggplot2)
  library(ggmap)
  library(mapproj)
  library(gridExtra)
  library(png)
  library(grid)
  library(RTextTools)
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
  #query <- paste(part_query,step_estado,"where estado =", edo,"and categoria =", cat_pre , "and date_created >=",fecha_inicio," and date_created <=", fecha_final,";")
  query <- paste(part_query,step_estado,"where estado =", edo,"and date_created >=",fecha_inicio," and date_created <=", fecha_final,";")
  
  #hacer query con la categoría y estado selecionado
  rs <- dbSendQuery(con, query)
  dframe <- fetch(rs,n=-1)
  dbDisconnect(con)
  dframe <- dframe %>%
      mutate(lang = lapply(dframe$term, textcat)) %>%
      filter(lang != "scots", lang != "english") %>%
          select(-lang)
  df_top20 <- dframe %>%
    arrange(desc(freq)) %>%
    distinct(term) %>%
    head(20)
  df_top20
  
}

############################################## GET MAP #########################

getG_Map <- function(estado){
  library(lubridate)
  library(stringr)
  library(RCurl)
  library(dplyr)
  library(tidyr)
  library(knitr)
  library(irlba)
  library(Matrix)
  library(tm)
  library(ggplot2)
  library(ggmap)
  library(mapproj)
  library(gridExtra)
  library(png)
  library(grid)
  library(RTextTools)
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
    select(lon, lat, polarizacion)
  dfMaps
  
}



get_correlation_week <- function(){
  gc()
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
  
  fecha_inicio <- sprintf("'%s'",  as.character(as.Date(format(Sys.time(), "%Y-%m-%d"))-7))
  fecha_final <- sprintf("'%s'", as.character(as.Date(format(Sys.time(), "%Y-%m-%d"))))
  
  query <- paste("select * from \"tb4\" where date_created >=",fecha_inicio, "and",
                 "date_created <=", fecha_final,";")
  
  ## tabla 4, tabla tweets. 
  rank_tw <- dbGetQuery(con,query)
  ################## traemos informacion del rank de noticias
  # fechas para quedarnos con la ultima semana.
  semana_final <- as.numeric(week(as.Date(format(Sys.time(), "%Y-%m-%d"))))
  ano_final <- as.numeric(year(as.Date(format(Sys.time(), "%Y-%m-%d"))))
  
  query <- paste("select * from \"tbl_rank_news\" where semana =",semana_final, "and",
                 "ano =", ano_final,";")
  ## tabla noticias. 
  rank_noticias <- dbGetQuery(con,query)
  
  rank_combinado <- rank_tw %>%
    group_by(ano = year(date_created),semana = week(date_created),estado)%>%
    summarise(score_general = mean(score),
              score_salud = mean(score_salud),
              score_economia = mean(score_economia),
              score_seguridad = mean(score_seguridad),
              score_servicios = mean(score_servicios))
  
  # corregimos diferencia en los nombres de los estados
  rank_combinado$estado <- ifelse(rank_combinado$estado =="Aguascaliente","Aguascalientes",ifelse(rank_combinado$estado =="D F","Distrito Federal",ifelse(rank_combinado$estado =="Michoacan","Michoacán",ifelse(rank_combinado$estado =="Queretaro","Querétaro",ifelse(rank_combinado$estado =="Nuevo Leon","Nuevo León",ifelse(rank_combinado$estado =="San Luis Potosi","San Luis Potosí",ifelse(rank_combinado$estado =="Yucatan","Yucatán",rank_combinado$estado)))))))
  
  # with(rank, cor(score_general, score_salud))
  correlacion_gral <- left_join(rank_combinado, rank_noticias, by = c("estado", "semana")) %>%
    na.omit(a) %>%
    #group_by(estado) %>%
    summarize(cor_general = cor(score_general.x, score_general.y),
              cor_salud = cor(score_salud.x, score_salud.y),
              cor_economia = cor(score_economia.x,score_economia.y),
              cor_seguridad = cor(score_seguridad.x, score_seguridad.y),
              cor_servicios = cor(score_servicios.x, score_servicios.y)) %>%
    t()
  
  tabla_cor <- as.data.frame(correlacion_gral)
  colnames(tabla_cor) <- "cor"
  tabla_cor
}




get_corTable <- function(estado){
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
                        password = 'smcp1234')
   , "tb4")
  # extraemos a un df
  db <- collect(db)
  twt<-db%>%
  mutate(year = as.numeric(format(date_created, format = "%Y")),
        month = as.numeric(format(date_created, format = "%m")))%>%
  mutate(Fechas=as.Date(paste(year,"-",month,"-","01",sep=""),"%Y-%m-%d"))%>%
  group_by(Fechas,estado)%>%
  summarise(score_salud=mean(score_salud),score_economia=mean(score_economia),score_seguridad=mean(score_seguridad),score_servicios=mean(score_servicios),score=mean(score))

  media_nac<-db%>% 
  mutate(year = as.numeric(format(date_created, format = "%Y")),
         month = as.numeric(format(date_created, format = "%m")))%>%
  mutate(Fechas=as.Date(paste(year,"-",month,"-","01",sep=""),"%Y-%m-%d"))%>%
  group_by(Fechas)%>%
  summarise(score_salud=mean(score_salud),
            score_economia=mean(score_economia),
            score_seguridad=mean(score_seguridad),
            score_servicios=mean(score_servicios),
            score=mean(score))
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
  ###########Obtiene principales tasas de crecimiento  de componentes de Actividad Industrial (series originales):

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
  estandar <- function(x) {((x-mean(x))/sd(x))}
  normed <- as.data.frame(lapply(correlacion, estandar))
  correlacion<-as.data.frame(correlacion)
  correlacion_m<-as.data.frame(cor(correlacion))
  cor1<-ggplot(data = melt(cor(correlacion)), aes(X1, X2, fill = value))+
        geom_tile(color = "white")+
        scale_fill_gradient2(low = "blue", high = "red", mid = "white",
                             midpoint = 0, limit = c(-1,1), space = "Lab",
                             name="Correlación") +
    theme_minimal()+
    theme(axis.text.x = element_text(angle = 45, vjust = 1,size = 12, hjust = 1))+
    coord_fixed()

  cor1
}

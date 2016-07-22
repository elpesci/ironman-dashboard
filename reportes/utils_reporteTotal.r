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
    gather(concepto, puntuacion, -date_created, -estado) %>% 
    filter(str_detect(concepto,'rank')) %>% 
    select(concepto, puntuacion) 
  
  edo_rank
  
}

###################################################################################
#   RANKING CON INTERVALO DE DE DÍAS
###################################################################################

Rank_days <- function(estado,days=7){
    #Funcion para comparar ranks y diferencial con base en la fecha en que se genera la info. Toma como input un estado (character) y el número de días anteriores a comparar.
    library(RMySQL)
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
    library(mapproj)
    library(gridExtra)
    library(png)
    library(grid)
    library(RTextTools)
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
    date_end <- as.Date(format(Sys.time(), "%Y-%m-%d")) -1
    date_ini <- date_end - days
    edo_rank <- dframe %>% 
      arrange(desc(date_created)) %>%
      filter(date_created == date_ini | date_created == date_end) %>% 
      gather(concepto, puntuacion, -date_created, -estado) %>% 
      filter(str_detect(concepto,'rank')) %>% 
      select(date_created,concepto, puntuacion) 
    rank1 <- edo_rank %>%
      filter(date_created == date_end)
    rank2 <- edo_rank %>%
      filter(date_created == date_ini)
    rank_total <- left_join(rank2, rank1, by = "concepto") %>%
      select(concepto, date_created.x, puntuacion.x, date_created.y, puntuacion.y) %>%
      mutate(incremento = puntuacion.x - puntuacion.y)
    colnames(rank_total) <- c ('concepto', 'fecha_inicio','posicion_inicio','fecha_fin','posicion_fin', 'incremento_lugares')

    rank_total
}




###################################################################################
#     OBTENER EL PERFORMANCE DE TODOS LOS INDICADORES DE UN ESTADO
###################################################################################


Performance <- function(estado,days){
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
  fecha_inicio <- sprintf("'%s'",  as.character(as.Date(format(Sys.time(), "%Y-%m-%d"))-days))
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
    gather(concepto, puntuacion, -date_created, -estado)  
    #filter(str_detect(concepto,'score')) 
  #dbClearResult(rs)
  dbDisconnect(con)  
  
  dframe
}


###################################################################################
#     OBTENER LAS PALABRAS CLAVE DE TODAS LAS CATEGORÍAS DEL ESTADO
###################################################################################

TopWords <- function(estado,days){
  library(RMySQL)
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
  tabla_estado <- "tbl_topWordsPol"
  step_estado <- sprintf("\"%s\"", tabla_estado)
  part_query <- "select * from "
  edo <- sprintf("'%s'", estado)
  
  #query de categoria
  #cat_pre <- sprintf("'%s'", categoria)
  #fecha
  if(days==7){
    fecha_inicio <- sprintf("'%s'",  as.character(as.Date(format(Sys.time(), "%Y-%m-%d"))-days*2))  
    } else {
    fecha_inicio <- sprintf("'%s'",  as.character(as.Date(format(Sys.time(), "%Y-%m-%d"))-days))  
   }
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

Map <- function(estado,days){
  library(RMySQL)
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
  #library(rMaps)
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
  fecha_inicio <- sprintf("'%s'",  as.character(as.Date(format(Sys.time(), "%Y-%m-%d"))-days))
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


######################################contar "-" en los headings

strcount <- function(x, pattern, split){
  
  unlist(lapply(
    strsplit(x, split),
    function(z) na.omit(length(grep(pattern, z)))
  ))
  
}

######################################################################################
#
#   FUNCION PARA JALAR LOS DATOS Y GENERR LI INFORMACION RESPECTO A POLITICAS PUBLICAS
#
######################################################################################

polPublica <- function(estado){
  library(dplyr)
  library(lubridate)
  library(plotly)
  library(knitr)
  #library(DT)
  #require(RColorBrewer)
  drv <- dbDriver("PostgreSQL")
  con <- dbConnect(drv, host="postgres.cvbe158gtbog.us-west-2.rds.amazonaws.com",
                   port="5432",
                   dbname="postgres",
                   user = 'smcp',
                   password = 'smcp1234')

  part_query <- "select * from tb4_pp"
  #fecha
  fecha_inicio <- sprintf("'%s'",  as.character(as.Date(format(Sys.time(), "%Y-%m-%d"))-8))
  fecha_final <- sprintf("'%s'", as.character(as.Date(format(Sys.time(), "%Y-%m-%d"))-1))
  #query final
  query <- paste(part_query,"where date_created >=",fecha_inicio, "and date_created <=", fecha_final,";")
  #hacer query con la categoría y estado selecionado
  rs <- dbSendQuery(con, query)
  dframe <- fetch(rs,n=-1)
  dbDisconnect(con)
  dframe
}



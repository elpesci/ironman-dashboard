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
  df_top20 <- dframe %>%
    arrange(desc(freq)) %>% 
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

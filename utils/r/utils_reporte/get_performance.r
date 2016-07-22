#### función para obtener el 


get_indicadorPerformance <- function(estado, categoria){
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
  score <- as.character(paste("score_", categoria, sep = "", collapse = NULL))
  dframe <- fetch(rs,n=-1) %>%
    select(date_created, score)
  #dbClearResult(rs)
  dbDisconnect(con)  
  
  dframe
}


#a <- get_indicadorPerformance('Aguascaliente', 'seguridad')



#paste("score_", categoria, sep = "", collapse = NULL)

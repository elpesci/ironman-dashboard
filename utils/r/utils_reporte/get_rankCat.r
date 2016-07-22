#### obtener el ranking
get_rankCat <- function(estado, categoria){
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
  pre_catEdo <- ifelse(categoria == "salud", 6, 0)
  pre_catEdo <- ifelse(categoria == "economia", 8, pre_catEdo)
  pre_catEdo <- ifelse(categoria == "seguridad", 10, pre_catEdo)
  pre_catEdo <- ifelse(categoria == "servicios", 12, pre_catEdo)
  
  edo_rankCategoria <- dframe %>% 
    arrange(desc(date_created)) %>%
    head(1) %>% 
    dplyr::select(pre_catEdo)
  
  edo_rankCategoria
  
}

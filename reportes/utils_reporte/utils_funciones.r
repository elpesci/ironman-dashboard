#utils funciones

###########################################################################################
#   FUNCIÓN QUE HACE UN QUERY A LA BASE DE DATOS Y OBTIENE EL STRING DE LOS USUARIOS TOP
###########################################################################################
#library(twitteR)
#setup_twitter_oauth(consumer_key="UWTWoiY04fgfWMmdJK96axbsz", consumer_secret="d9jtM8SVFyPxRYJpNSfRjtHMsWuz0tBJIszo4PNJvRHMw3Dtsl", access_token= "2315641352-NBpeHxvMHJVvs0WIENpxmKOObdCwMWaFbbDhZoE", access_secret= "pS08ki553vq8so7XKbuzekn9Y0cPJtqS9ndi8DkCJFUC9")

#token <- get("oauth_token", twitteR:::oauth_cache)
#token$cache()
#save(token,file="/Users/lechuga/Dropbox/smcp (1)/Lechuga_smpc/desarrollo_indicadoresDashboard/generacion_reporte/oauth_cache.RData")

get_topUsers <- function(estado, categoria){
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
  tabla_estado <- paste("tb1",edo, sep ="_")
  step_estado <- sprintf("\"%s\"", tabla_estado)
  part_query <- "select * from "
  
  #query de categoria
  cat_pre <- sprintf("'%s'", categoria)
  
  #fecha
  fecha_inicio <- sprintf("'%s'",  as.character(as.Date(format(Sys.time(), "%Y-%m-%d"))-7))
  fecha_final <- sprintf("'%s'", as.character(as.Date(format(Sys.time(), "%Y-%m-%d"))))
  #query final
  #query <- paste(part_query,step_estado,"where categoria =",cat_pre ,";")
  query <- paste(part_query,step_estado,"where categoria =",cat_pre, "and",
                 "date_created >=",fecha_inicio, "and",
                 "date_created <=", fecha_final,
                 ";")
  ###########
  
  #hacer query con la categoría y estado selecionado
  rs <- dbSendQuery(con, query)
  dframe <- fetch(rs,n=-1)
  #dbClearResult(rs)
  dbDisconnect(con)      #<-------- HACER PRUEBAS
  #dbUnloadDriver(drv)
  # Se hace el filtro para obtener la información de la última semana
  df_test <- dframe %>% 
    select(tweet_id_str, from_user_id,tweet, date_created, in_reply_to_status_id_str) #%>%
  #filter(date_created >= as.Date(format(Sys.time(), "%Y-%m-%d"))-7 & ### OJO
  #        date_created <= as.Date(format(Sys.time(), "%Y-%m-%d")))
  
  #seleccionamos las colunas deseadas y los usuarios con más actividad en el contexto deseado (categoría)
  df_nodes <- df_test %>% 
    select(tweet_id_str, from_user_id,tweet, date_created, in_reply_to_status_id_str) %>%
    unique() %>% #solo para este caso 
    group_by(from_user_id) %>%
    summarize(freq_users=n()) %>% 
    arrange(desc(freq_users)) %>% 
    head(10)
  
  #Seleccionamos los comentarios de los usuarios más importantes 
  df_1 <- filter(df_nodes, from_user_id == as.numeric(df_nodes[1,1]))
  for(users in 2:dim(df_nodes)[1]){
    a <- filter(df_nodes, from_user_id == as.numeric(df_nodes[users,1]))
    df_1 <- rbind(df_1,a)
  }
  
  #como lista (otra opción)
  #df_0 <- lapply(1:dim(df_nodes)[1], function(x) filter(df, from_user_id == as.numeric(df_nodes[x,1])))
  
  ############################################################################################
  ####################### AUTENTIFICACIÓN DE TWITTER #######################
  # Hay que ver si esto corre sin pedos 
  
  #library(twitteR)
  #setup_twitter_oauth(consumer_key="UWTWoiY04fgfWMmdJK96axbsz", consumer_secret="d9jtM8SVFyPxRYJpNSfRjtHMsWuz0tBJIszo4PNJvRHMw3Dtsl", access_token= "2315641352-NBpeHxvMHJVvs0WIENpxmKOObdCwMWaFbbDhZoE", access_secret= "pS08ki553vq8so7XKbuzekn9Y0cPJtqS9ndi8DkCJFUC9")
  #1
  
  ############################################################################################
  ####################################### Obtener los nombres de los usuarios más importantes
  
  #pasamos a un vector los id´s de los usuarios importantes
  users_id <- as.vector(df_nodes[,1])
  
  #users_names0 <- lapply(users_id, function(x) lookupUsers(x))
  #users_names <- apply(users_id, 2, function(x) getUser(x))
  
  users_names <- getUser(users_id[1,])
  for(names in 2:dim(users_id)[1]){
    a <- getUser(users_id[names,])
    users_names <- append(users_names, a)
  }
  
  
  ################
  #extraemos los nombres de los usuarios
  users_names <- twListToDF(users_names) %>%
    select(screenName) 
  
  #Asociamos los nombres de los usuarios con los ID´s
  top_usersNamesID <- cbind(users_names, users_id[1:dim(users_names)[1],])
  
  #Creamos la lista final de usuarios y frecuencia de comentarios
  top_users <- left_join(top_usersNamesID, df_nodes, by = "from_user_id") %>%
    select(screenName, freq_users) %>%
    mutate(date_created = format(Sys.time(), "%Y-%m-%d"),
           categoria = categoria,
           estado = estado
    )
  
  top_users
}

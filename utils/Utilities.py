import datetime

class Constants:

    @staticmethod
    def general_ranking_category():
        return "general"

    @staticmethod
    def default_ranking_category():
        return Constants.general_ranking_category()

    @staticmethod
    def ranking_categories():
        return ["economia", "gobernador", "gobierno", \
                "judicial", "legislativo", "obra.publica", \
                "pavimentacion", "presidente", "recoleccion.basura", \
                "salud", "seguridad", "servicio.agua", \
                "servicios", "transporte.publico"]

    @staticmethod
    def ranking_categories_in_general_rank():
        return ["gobernador", "legislativo", "obra.publica", "servicios", "economia", "seguridad"]

    @staticmethod
    def ranking_combinado_table_name():
        return "tbl_rank_general"

    @staticmethod
    def ranking_noticias_table_name():
        return "tbl_rank_news"

    @staticmethod
    def ranking_social_table_name():
        return "tbl_rank_tw"

class Utilities:

    @staticmethod
    def array_to_csv(array):
        result = "'" + "','".join(array) + "'"

        return  result

    @staticmethod
    def last_week_start_date():
        today = datetime.date.today()

        start_date = today - datetime.timedelta(days=today.weekday(), weeks=1)

        return start_date

    @staticmethod
    def last_week_end_date():
        end_date = Utilities.last_week_start_date() + datetime.timedelta(days=6)

        return end_date


import datetime
import re

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

    @staticmethod
    def categories_dict():
        cd = dict([('economia', "Econom&iacute;a"), ('gobernador', "Gobernador"), ('gobierno', "Gobierno"), \
                   ('judicial', "Jueces"), ('legislativo', "Diputados y Senadores"), ('obra.publica', "Obra p&uacute;blica"), \
                   ('pavimentacion', "Pavimentaci&oacute;n"), ('presidente', "Presidente"), \
                   ('recoleccion.basura', "Recolecci&oacute;n de basura"), ('salud', "Salud"), ('seguridad', "Seguridad"), \
                   ('servicio.agua', "Servicio de agua"), ('servicios', "Servicios"), ('transporte.publico', "Transporte p&uacute;blico")
                   ])
        return cd

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

    @staticmethod
    def to_utf8_html_encoding(tagged_text):
        converted_text = tagged_text

        reg_exp = re.compile(r"<[a-fA-F0-9]{2}>", re.IGNORECASE)
        tags = re.findall(reg_exp, tagged_text)

        if(len(tags) > 0):
            for replaceable_tag in tags:
                html_encoded_char = str(replaceable_tag).upper().replace("<", "&#x").replace(">", ";")
                converted_text = converted_text.replace(str(replaceable_tag), html_encoded_char)

        return converted_text

    @staticmethod
    def get_category_label(category_key):
        categries_dict = Constants.categories_dict()
        category_label = ""

        for item in categries_dict.keys():
            if item == category_key:
                category_label = categries_dict[category_key]
                continue

        return category_label

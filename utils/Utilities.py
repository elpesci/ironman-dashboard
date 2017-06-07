#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import re
import csv
from sortedcontainers import SortedDict

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
        cd = [('economia', "Economía"),
              ('gobernador', "Gobernador"),
              ('gobierno', "Gobierno"),
              ('judicial', "Jueces"),
              ('legislativo', "Diputados y Senadores"),
              ('obra.publica', "Obra pública"),
              ('pavimentacion', "Pavimentación"),
              ('presidente', "Presidente"),
              ('recoleccion.basura', "Recolección de basura"),
              ('salud', "Salud"),
              ('seguridad', "Seguridad"),
              ('servicio.agua', "Servicio de agua"),
              ('servicios', "Servicios"),
              ('transporte.publico', "Transporte público")]
        return cd

    @staticmethod
    def states_dict():
        reader = csv.reader(open("./utils/formato_estados.csv"))
        _ = reader.next()

        estados = [(row[0], row[1]) for row in reader]

        return estados

    @staticmethod
    def state_performance_categories_dict():
        cd = [('gobernador', "Gobernador"),
              ('obra.publica', "Obra pública"),
              ('pavimentacion', "Pavimentación"),
              ('recoleccion.basura', "Recolección de basura"),
              ('salud', "Salud"),
              ('seguridad', "Seguridad"),
              ('servicio.agua', "Servicio de agua"),
              ('transporte.publico', "Transporte público")]
        return cd

    @staticmethod
    def s_and_h_categories_dict():
        cd = [('presidente', 'Presidente de la república'),
              ('gobernador', 'Gobernadores'),
              ('gobierno', 'Gobierno'),
              ('legislativo', 'Diputados y Senadores'),
              ('seguridad', 'Seguridad'),
              ('servicios', 'Servicios'),
              ('economia', 'Economía')]

        return cd

    @staticmethod
    def grouping_options_dict():
        od = [('week', 'Semanal'), ('month', 'Mensual')]

        return od


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
    def last_monday_date(my_date = None):
        if my_date:
            seed_date = my_date
        else:
            seed_date = datetime.datetime.today()

        last_monday_date = seed_date - datetime.timedelta(days = seed_date.weekday())

        return last_monday_date

    @staticmethod
    def next_sunday_date(my_date = None):
        if my_date:
            seed_date = my_date
        else:
            seed_date = datetime.datetime.now()

        next_sunday_date = seed_date + datetime.timedelta(days = 6 - seed_date.weekday())

        return next_sunday_date

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
        categries_dict = dict(Constants.categories_dict())
        category_label = "General"

        for item in categries_dict.keys():
            if item == category_key:
                category_label = categries_dict[category_key]
                continue

        return category_label

    @staticmethod
    def get_state_label(state_key):
        states_dict = dict(Constants.states_dict())
        state_label = ""

        if state_key == 'pais':
            return 'País'

        for item in states_dict.keys():
            if item == state_key:
                state_label = states_dict[state_key]
                continue

        return state_label

    @staticmethod
    def get_exportpp_csv_columns_header(category):
        score_header_label = "Score"
        rank_header_label = "Rank"

        if category:
            cat_label = Utilities.get_category_label(category)
            score_header_label = " ".join([score_header_label, cat_label])
            rank_header_label = " ".join([rank_header_label, cat_label])

        headers = ("Estado", "Fecha", rank_header_label, score_header_label)

        return headers

    @staticmethod
    def get_export_states_performance_csv_column_header(category):
        score_header_label = "Score"
        rank_header_label = "Rank"

        if category:
            cat_label = Utilities.get_category_label(category)
            score_header_label = " ".join([score_header_label, cat_label])
            rank_header_label = " ".join([rank_header_label, cat_label])

        headers = ("Estado", "Inicio Periodo", "Fin Periodo", rank_header_label, score_header_label)

        return headers

    @staticmethod
    def full_state_performance_categories_dict():
        full_dict = Constants.state_performance_categories_dict()
        full_dict.insert(0, ('general', "General"))
        return full_dict

    @staticmethod
    def datepickerstring_to_date(datepickerstring):
        converted = datetime.datetime.strptime(datepickerstring, "%m/%d/%Y").date()
        return converted

    @staticmethod
    def is_number(value):
        try:
            float(value)  # for int, long and float
        except ValueError:
            return False

        return True

from DatabaseManager import *
from Utilities import Utilities
from data_utils import *
import StringIO, csv
import datetime

class BaseExportHelper:
    def __init__(self, export_form):
        self.__export_form = export_form

    def get_filtering_state(self):
        return self.__export_form.data['estado']

    def get_filtering_category(self):
        return self.__export_form.data['categoria']

    def get_period_start_date(self):
        return self.__export_form['periodo'].data.split("-")[0].strip()

    def get_period_end_date(self):
        return self.__export_form['periodo'].data.split("-")[1].strip()

    def get_period_start_week_id(self):
        sd = Utilities.datepickerstring_to_date(self.get_period_start_date())
        actual_start_date = Utilities.last_monday_date(sd)

        actual_week = actual_start_date.isocalendar()[1]
        str_actual_week = "00" + str(actual_week)

        return "{0}{1}".format(actual_start_date.year, str_actual_week[-2:])

    def get_period_end_week_id(self):
        ed = Utilities.datepickerstring_to_date(self.get_period_end_date())
        actual_end_date = Utilities.next_sunday_date(ed)

        actual_week = actual_end_date.isocalendar()[1]
        str_actual_week = "00" + str(actual_week)

        return "{0}{1}".format(actual_end_date.year, str_actual_week[-2:])

    def generate_results_csv_file(self, data_to_export, file_headers):
        # Building exportable file
        csv_file = StringIO.StringIO()
        cw = csv.writer(csv_file)

        cw.writerows([file_headers])
        cw.writerows(data_to_export)

        # Returning the attachment file
        return csv_file.getvalue()


class StatesPerformanceExportHelper(BaseExportHelper):
    def __init__(self, export_form):
        BaseExportHelper.__init__(self, export_form)

        self._form = export_form
        self._data_grouped_weekly_query_template = """SELECT	act.estado,
                wid.dia_inicial as inicio_semana,
                wid.dia_inicial + integer '6' as fin_semana,
                act."rank_{4}",
                act."score_{4}"
            FROM
                {0} as act
            INNER JOIN
                tbl_id as wid on CAST(act.id as text) = CAST(wid.id as text)
            WHERE
                CASE
                    WHEN '{1}' = 'pais' THEN
                        act.estado != 'pais'
                    ELSE
                        (act.estado = (select nombre from "tbl_catEstado" where clave = '{1}')
                        OR
                        act.estado = (select alias from "tbl_catEstado" where clave = '{1}'))
                END
            AND
                CAST(act.id as int) >= CAST('{2}' as int)
            AND
                CAST(act.id as int) <= CAST('{3}' as int)
            GROUP BY act.estado, wid.dia_inicial, act."rank_general", act."score_general"
            ORDER BY act.estado"""
        self._data_grouped_monthly_query_template = """SELECT	to_char(to_timestamp(date_part('year', super_set.inicio_semana)::text, 'yyyy'), 'yyyy') as Year,
                month_name_to_spanish(to_char(to_timestamp(date_part('month', super_set.inicio_semana)::text, 'MM'), 'Month')) as Month,
                super_set.estado,
                avg(super_set.rank_general) as promedio_rank_general,
                avg(super_set.score_general) as promedio_score_general
            FROM (
                SELECT	act.estado,
                    wid.dia_inicial as inicio_semana,
                    wid.dia_inicial + integer '6' as fin_semana,
                    act."rank_{4}",
                    act."score_{4}"
                FROM
                    {0} as act
                INNER JOIN
                    tbl_id as wid on CAST(act.id as text) = CAST(wid.id as text)
                WHERE
                    CASE
                        WHEN '{1}' = 'pais' THEN
                            act.estado != 'pais'
                        ELSE
                            (act.estado = (select nombre from "tbl_catEstado" where clave = 'pais')
                            OR
                            act.estado = (select alias from "tbl_catEstado" where clave = 'pais'))
                    END
                AND
                    CAST(act.id as int) >= CAST('{2}' as int)
                AND
                    CAST(act.id as int) <= CAST('{3}' as int)
                GROUP BY
                    act.estado, wid.dia_inicial, act."rank_general", act."score_general"
                ORDER BY
                    act.estado, inicio_semana
                ) as super_set
            GROUP BY
                super_set.estado, date_part('year', super_set.inicio_semana), date_part('month', super_set.inicio_semana)
            ORDER BY
                super_set.estado"""

    def get_query_template_from_grouping_option(self, grouping_opt):
        return {
            'week' : self._data_grouped_weekly_query_template,
            'month' : self._data_grouped_monthly_query_template
        }.get(grouping_opt, self._data_grouped_weekly_query_template)

    def __add_header_row(self, data_to_export):
        selected_grouping = self.get_grouping_option()

        header_row = {
            'week': ("Estado", "Inicio periodo", "Fin periodo", "Rank {0}".format(self.get_filtering_category()), "Score {0}".format(self.get_filtering_category())),
            'month': ("Year", "Month", "Estado", "Promedio Rank {0}".format(self.get_filtering_category()), "Promedio Score {0}".format(self.get_filtering_category()))
        }.get(selected_grouping, ())

        data_to_export.insert(0, header_row)

        return data_to_export

    def get_performance_data_export_from(self, from_table_name):
        selected_grouping = self.get_grouping_option()
        query_template = self.get_query_template_from_grouping_option(selected_grouping)

        query = query_template.format(from_table_name,
                                        self.get_filtering_state(),
                                        self.get_period_start_week_id(),
                                        self.get_period_end_week_id(),
                                        self.get_filtering_category())
        pg = PGDatabaseManager()
        rows = pg.get_rows(query)

        rows = self.__add_header_row(rows)

        return rows

    def get_grouping_option(self):
        return self._form.data['agrupado']


class PoliticasPublicasExportHelper(BaseExportHelper):
    def __init__(self, export_form):
        BaseExportHelper.__init__(self, export_form)

    def get_export_data(self):

        data = filter_data_politicas_publicas_export(self.get_filtering_state(),
                                                     self.get_filtering_category(),
                                                     self.get_period_start_date(),
                                                     self.get_period_end_date())
        data = self.__add_header_row(data)

        return data

    def __add_header_row(self, data_to_export):
        headers = ("Estado",
                   "Fecha",
                   "Rank_{0}".format(self.get_filtering_category()),
                   "Score_{0}".format(self.get_filtering_category()))

        data_to_export.insert(0, headers)

        return data_to_export


class S_and_H_ExportHelper(BaseExportHelper):
    def __init__(self, export_form):
        BaseExportHelper.__init__(self, export_form)

    def get_export_data(self):

        period_start = datetime.datetime.strptime(self.get_period_start_date(), "%m/%d/%Y").strftime("%Y-%m-%d")
        period_end = datetime.datetime.strptime(self.get_period_end_date(), "%m/%d/%Y").strftime("%Y-%m-%d")

        data = filter_data_s_and_h_export(self.get_filtering_state(),
                                          None,
                                          period_start,
                                          period_end)

        data = self.__calculate_averages(data)
        data = self.__add_header_row(data)

        return data

    def __add_header_row(self, data_to_export):
        headers = ("Estado",
                   "InicioPeriodo",
                   "FinPeriodo",
                   "Score_Presidente",
                   "Score_Gobernador",
                   "Score_Gobierno",
                   "Score_DiputadosSenadores",
                   "Score_Seguridad",
                   "Score_Servicios",
                   "Score_Economia",
                   "Promedio_Estado")

        data_to_export.insert(0, headers)

        return data_to_export

    def __calculate_averages(self, exportable_data):
        # Para cada estado, sacar el promedio de los indicadores:
        # ScorePresidente, ScoreGobernador, ScoreGobierno, ScoreLegislativo, ScoreSeguridad, ScoreServicios, ScoreEconomia

        result = []

        # Recorrer el arreglo de estados
        for tupla_estado in exportable_data:
            counter, total = 0, 0
            for indice in range(0, len(tupla_estado)):
                if (Utilities.is_number(tupla_estado[indice])):
                    counter = counter + 1
                    total = total + tupla_estado[indice]
                    #print "{0}: Valor: {1}".format(tupla_estado[0], tupla_estado[indice])
            #print "{0}: Total {1}, Contador {2}".format(tupla_estado[0], total, counter)
            tupla_estado += total / counter,
            result.append(tupla_estado)

        avg_per_score_key = self.__calculate_score_key_average(exportable_data)
        result.append(avg_per_score_key)

        return result

    def __calculate_score_key_average(self, exportable_data):
        averages_per_score_tuple = ("Promedio por indicador", "", "")

        temp = ["", "", "", 0,0,0,0,0,0,0]
        counter = 0
        for tupla_estado in exportable_data:
            counter = counter + 1
            for indice in range(3, len(tupla_estado)):
                temp[indice] = temp[indice] + tupla_estado[indice]

        for temp_index in range(3, len(temp)):
            averages_per_score_tuple +=  temp[temp_index] / counter,

        return averages_per_score_tuple

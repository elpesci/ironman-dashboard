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

    def get_performance_data_export_from(self, from_table_name):
        query = """SELECT	act.estado,
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
	        act.estado = 'pais'
	    ELSE
	        (act.estado = (select nombre from "tbl_catEstado" where clave = '{1}')
            OR
            act.estado = (select alias from "tbl_catEstado" where clave = '{1}'))
	END
AND
    CAST(act.id as int) >= CAST('{2}' as int)
AND
    CAST(act.id as int) <= CAST('{3}' as int)""".format(from_table_name,
                                                        self.get_filtering_state(),
                                                        self.get_period_start_week_id(),
                                                        self.get_period_end_week_id(),
                                                        self.get_filtering_category())
        pg = PGDatabaseManager()
        rows = pg.get_rows(query)

        return rows

    def get_results_file(self, data_to_export):
        headers = Utilities.get_export_states_performance_csv_column_header(self.get_filtering_category())

        return self.generate_results_csv_file(data_to_export, headers)


class PoliticasPublicasExportHelper(BaseExportHelper):
    def __init__(self, export_form):
        BaseExportHelper.__init__(self, export_form)

    def get_export_data(self):

        data = filter_data_politicas_publicas_export(self.get_filtering_state(),
                                                     self.get_filtering_category(),
                                                     self.get_period_start_date(),
                                                     self.get_period_end_date())
        return data

    def get_results_file(self, data_to_export):
        headers = Utilities.get_exportpp_csv_columns_header(self.get_filtering_category())

        return self.generate_results_csv_file(data_to_export, headers)


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
        return data

    def get_results_file(self, data_to_export):
        headers = ("Estado",
                   "InicioPeriodo",
                   "FinPeriodo",
                   "Score_Presidente",
                   "Score_Gobernador",
                   "Score_Gobierno",
                   "Score_DiputadosSenadores",
                   "Score_Seguridad",
                   "Score_Servicios",
                   "Score_Economia")

        return self.generate_results_csv_file(data_to_export, headers)

from DatabaseManager import *
from Utilities import Utilities
import StringIO, csv

class StatesPerformanceExportHelper:
    def __init__(self, export_form):
        self.export_form = export_form

    def get_filtering_state(self):
        return self.export_form.data['estado']

    def get_filtering_category(self):
        return self.export_form.data['categoria']

    def get_period_start_date(self):
        return self.export_form['periodo'].data.split("-")[0].strip()

    def get_period_end_date(self):
        return self.export_form['periodo'].data.split("-")[1].strip()

    def get_period_start_week_id(self):
        sd = Utilities.datepickerstring_to_date(self.get_period_start_date())
        actual_start_date = Utilities.last_monday_date(sd)

        return "{0}{1}".format(actual_start_date.year, actual_start_date.isocalendar()[1])

    def get_period_end_week_id(self):
        ed = Utilities.datepickerstring_to_date(self.get_period_end_date())
        actual_end_date = Utilities.next_sunday_date(ed)

        return "{0}{1}".format(actual_end_date.year, actual_end_date.isocalendar()[1])

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
WHERE	(act.estado = (select nombre from "tbl_catEstado" where clave = '{1}')
    OR
    act.estado = (select alias from "tbl_catEstado" where clave = '{1}'))
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

    def generate_results_csv_file(self, data_to_export):
        # Building exportable file
        headers = Utilities.get_export_states_performance_csv_column_header(self.get_filtering_category())

        csv_file = StringIO.StringIO()
        cw = csv.writer(csv_file)

        cw.writerows([headers])
        cw.writerows(data_to_export)

        # Returning the attachment file
        return csv_file.getvalue()

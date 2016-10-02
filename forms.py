#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import Form, BooleanField, StringField, PasswordField, validators, SelectField, HiddenField
from wtforms.validators import DataRequired
from utils.Utilities import *

class RegistrationForm(Form):
    nombre = StringField('Nombre y apellido', validators=[DataRequired()])
    login = StringField('Nombre de usuario (username)', validators=[DataRequired()])
    password = PasswordField('Contrase&ntilde;a (password)', [
                validators.DataRequired(),
                validators.EqualTo('confirm', message='La confirmación de contraseña no coincide con el valor inicial de contraseña')
            ])
    confirm = PasswordField('Confirme el password')
    descripcion = StringField('Describa su institucion')

class PaymentForm(Form):
    contract = SelectField("Seleccione su plan a contratar", \
                choices=[("100", "Membresía Mensual - $100"), ("900", "Membresía Anual - $900")])
    card_number = StringField()
    c_c_v = StringField()
    expiration = StringField()

class ExportPoliticasPublicasForm(Form):
    estados = Constants.states_dict()
    estados.insert(0, ['pais', 'País'])

    estado = SelectField(u'Estado',
                         choices = estados,
                         validators = [DataRequired(message='Por favor, seleccione estado')])
    categoria = SelectField(u'Categor&iacute;a',
                            choices = Constants.categories_dict(),
                            validators = [DataRequired(message='Por favor, seleccione categoría')])
    periodo = StringField(validators = [DataRequired(message='Por favor, indique período')])

class ExportStatePerformanceForm(Form):
    estados = Constants.states_dict()
    estados.insert(0, ['pais', 'País'])

    estado = SelectField(u'Estado',
                         choices = estados,
                         validators = [DataRequired(message='Por favor, seleccione estado')])
    categoria = SelectField(u'Categor&iacute;a',
                            choices = Utilities.full_state_performance_categories_dict(),
                            validators = [DataRequired(message='Por favor, seleccione categoría')])
    periodo = StringField(validators = [DataRequired(message='Por favor, indique período')])
    inicio_periodo = HiddenField(default = Utilities.last_monday_date(datetime.datetime.today() - datetime.timedelta(days=14)).strftime("%m/%d/%Y"))
    fin_periodo = HiddenField(default = Utilities.next_sunday_date(datetime.datetime.today() - datetime.timedelta(days=7)).strftime("%m/%d/%Y"))

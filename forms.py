#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import Form, BooleanField, StringField, PasswordField, validators, SelectField
from wtforms.validators import DataRequired
from utils.Utilities import Constants

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
    estado = SelectField(u'Estado', choices=Constants.states_dict(), validators=[DataRequired(message='Por favor, seleccione estado')])
    categoria = SelectField(u'Categor&iacute;a',  choices=Constants.categories_dict(), validators=[DataRequired(message='Por favor, seleccione categoría')])
    periodo = StringField(validators=[DataRequired(message='Por favor, indique período')])


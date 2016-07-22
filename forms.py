from flask.ext.wtf import Form
from wtforms import Form, BooleanField, StringField, PasswordField, validators, SelectField
from wtforms.validators import DataRequired

class RegistrationForm(Form):
    nombre = StringField('Nombre', validators=[DataRequired()])
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Introduzca un password', [
                validators.DataRequired(),
                validators.EqualTo('confirm', message='Los passwords deben coincidir')
            ])
    confirm = PasswordField('Confirme el password')
    descripcion = StringField('Describa su institucion')

class PaymentForm(Form):
    contract = SelectField("Seleccione su plan a contratar", \
                choices=[("100", "Membresia Mensual - $100"), ("900", "Membresia Anual - $900")])
    card_number = StringField()
    c_c_v = StringField()
    expiration = StringField()




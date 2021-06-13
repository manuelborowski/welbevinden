from wtforms import Form, PasswordField, StringField, BooleanField, ValidationError, IntegerField, SelectField


class EditForm(Form):
    full_name = StringField('Naam ouder')
    child_name = StringField('Naam kind')
    phone = StringField('Telefoon')
    email = StringField('E-mail')


class AddForm(EditForm):
    pass


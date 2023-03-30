from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, Length
from app.models import User

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('LastName')
    email = StringField('Email', validators=[DataRequired(), Email()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=200)])
    submit = SubmitField('Submit')

    # overloaded constructor that accepts original username as argument
    def __init__(self, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        # saves username as instance variable
        self.original_email = original_email
    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=self.email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email.')
    

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(),
        Length(min=1, max=140)
        ]
    )
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    q = StringField('Search...', validators=[DataRequired()])
    
    def __init__(self, *args, **kwargs):
        # provides values for form if not provided by caller
        if 'formdata' not in kwargs:
            # froms submitted as GET have field values in request.args
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'crsf': False}
        super(SearchForm, self).__init__(*args, **kwargs)
from django.contrib.auth.models import User
from import_export.resources import ModelResource


class UserResource(ModelResource):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'mail_status', 'activity')

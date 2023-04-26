from users.models import User

from import_export import resources, fields


class UserResource(resources.ModelResource):

    class Meta:
        model = User
        fields = ('user_email', 'mail_status',)
        skip_unchanged = True
        report_skipped = False
        import_id_fields = []

    def get_instance(self, instance_loader, row):
        # Check if there's an existing user with the email address in the row
        try:
            user = User.objects.get(user_email=row['user_email'])
        except User.DoesNotExist:
            user = None

        # Create a new user if there's no existing user with the email address
        if not user:
            user = super().get_instance(instance_loader, row)

        return user

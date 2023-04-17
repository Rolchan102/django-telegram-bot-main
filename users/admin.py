from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from import_export.admin import ImportExportModelAdmin
from dtb.settings import DEBUG
from dtb.resources import UserResource

# from users.models import Location
from users.models import User
from users.forms import BroadcastForm

from users.tasks import broadcast_message
from tgbot.handlers.broadcast_message.utils import send_one_message


class UserAdmin(admin.ModelAdmin):

    def broadcast(self, request, queryset):
        """ Выберите пользователей с помощью галочки в панели администратора django, затем выберите "Broadcast" для отправки сообщений"""
        user_ids = queryset.values_list('user_id', flat=True).distinct().iterator()
        if 'apply' in request.POST:
            broadcast_message_text = request.POST["broadcast_text"]

            if DEBUG:  # for test / debug purposes - run in same thread
                for user_id in user_ids:
                    send_one_message(
                        user_id=user_id,
                        text=broadcast_message_text,
                    )
                self.message_user(request, f"Just broadcasted to {len(queryset)} users")
            else:
                broadcast_message.delay(text=broadcast_message_text, user_ids=list(user_ids))
                self.message_user(request, f"Broadcasting of {len(queryset)} messages has been started")

            return HttpResponseRedirect(request.get_full_path())
        else:
            form = BroadcastForm(initial={'_selected_action': user_ids})
            return render(
                request, "admin/broadcast_message.html", {'form': form, 'title': u'Broadcast message'}
            )


@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    resource_class = UserResource
    list_display = [
        'user_email', 'user_id', 'username',
        'first_name', 'last_name',  'city',
        'mail_status', 'activity', 'language_code',
        'created_at', 'updated_at',
        "is_blocked_bot", "is_admin",
    ]
    list_filter = ["is_blocked_bot", "is_admin", "city", ]
    search_fields = ('username', 'user_id')

    actions = ['broadcast']

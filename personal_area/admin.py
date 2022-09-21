from django.contrib import admin, auth
from elink_index.models import LinkRegUser
from users.models import User

admin.site.unregister(auth.models.Group)


@admin.register(LinkRegUser)
class LinkRegUserAdmin(admin.ModelAdmin):
    fields = [
        "description",
        "long_link",
        "date_add",
        "limited_link",
        "secure_link",
        "start_link",
        "date_stop",
        "how_many_clicked",
        "again_how_many_clicked",
        "short_code",
        "author",
    ]
    list_display = [
        "id",
        "description",
        "date_add",
        "limited_link",
        "secure_link",
        "start_link",
        "date_stop",
        "how_many_clicked",
        "again_how_many_clicked",
        "short_code",
        "author",
    ]
    search_fields = ["short_code"]
    list_filter = ["author", "limited_link"]

    def has_add_permission(self, request):
        return False


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    actions = [
        "rights_default",
        "rights_tester",
        "rights_moderator",
        "ban_user",
        "unban_user",
        "my_timezone",
        "violations",
        "stop_send_stat_email",
        "go_send_stat_email",
        "delete_bad_account",
        "ban_bad_account",
    ]
    list_display = [
        "id",
        "email",
        "subs_type",
        "date_join",
        "banned",
        "my_timezone",
        "violations",
        "send_stat_email",
        "trust_rating",
    ]
    fields = [
        "email",
        "subs_type",
        "link_count",
        "trust",
        "my_timezone",
        "violations",
        "send_stat_email",
        "trust_rating",
    ]
    search_fields = ["email"]
    list_filter = ["subs_type", "my_timezone", "trust", "send_stat_email"]

    @admin.action(description="Выдать права REGISTERED(стандартные рейты)")
    def rights_default(modeladmin, request, queryset):
        queryset.update(subs_type="REG")

    @admin.action(description="Выдать права BETA_TESTER(х10 рейты)")
    def rights_tester(modeladmin, request, queryset):
        queryset.update(subs_type="BTEST")

    @admin.action(description="Выдать права MODERATOR(без ограничений)")
    def rights_moderator(modeladmin, request, queryset):
        queryset.update(subs_type="MOD")

    @admin.action(description="Забанить")
    def ban_user(modeladmin, request, queryset):
        queryset.update(banned=True)

    @admin.action(description="Разбанить")
    def unban_user(modeladmin, request, queryset):
        queryset.update(banned=False)

    @admin.action(description="Отключить рассылку статистики")
    def stop_send_stat_email(modeladmin, request, queryset):
        queryset.update(send_stat_email=False)

    @admin.action(description="Включить рассылку статистики")
    def go_send_stat_email(modeladmin, request, queryset):
        queryset.update(send_stat_email=True)

    @admin.action(description="Удалить пользователей с рейтингом доверия 0")
    def delete_bad_account(modeladmin, request, queryset):
        queryset.filter(trust_rating__lte=0).delete()

    @admin.action(description="Заблокировать пользователей с рейтингом доверия 0")
    def ban_bad_account(modeladmin, request, queryset):
        queryset.filter(trust_rating__lte=0).update(banned=True)

    def has_add_permission(self, request):
        return False

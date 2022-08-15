from django.contrib import admin
from elink_index.models import LinkRegUser
from users.models import User


@admin.register(LinkRegUser)
class LinkRegUserAdmin(admin.ModelAdmin):
    fields = ['short_code', 'author', ]
    search_fields = ['short_code', 'secure_link', 'author', 'how_many_clicked']

    def has_add_permission(self, request):
        return False


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    actions = ['rights_default',
               'rights_tester',
               'rights_moderator',
               'ban_user',
               'unban_user',
               ]
    list_display = ['email', 'subs_type', 'date_join', 'banned']
    fields = ['email', 'subs_type', 'link_count', 'trust']
    search_fields = ['email']

    @admin.action(description='Выдать права REGISTERED(стандартные рейты)')
    def rights_default(modeladmin, request, queryset):
        print(queryset)
        queryset.update(subs_type='REG')

    @admin.action(description='Выдать права BETA_TESTER(х10 рейты)')
    def rights_tester(modeladmin, request, queryset):
        queryset.update(subs_type='BTEST')

    @admin.action(description='Выдать права MODERATOR(без ограничений)')
    def rights_moderator(modeladmin, request, queryset):
        queryset.update(subs_type='MOD')

    @admin.action(description='Забанить')
    def ban_user(modeladmin, request, queryset):
        queryset.update(banned=True)

    @admin.action(description='Разбанить')
    def unban_user(modeladmin, request, queryset):
        queryset.update(banned=False)

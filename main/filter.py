from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import Group
from django.utils.translation import ugettext as _


class GroupListFilter(SimpleListFilter):
    title = _('group')
    parameter_name = 'group'

    def lookups(self, request, model_admin):
        items = ()
        for group in Group.objects.all():
            items += ((str(group.id), str(group.name),),)
        return items

    def queryset(self, request, queryset):
        group_id = request.GET.get(self.parameter_name, None)
        if group_id:
            return queryset.filter(groups=group_id)
        return queryset

from bootstrap4 import widgets
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms.util import flatatt
from django.forms.widgets import Select
from django.template import loader
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

from main.models import Product, ProductAttribute


class ReadOnlySelectWidget(forms.Select):
    def render(self, name, value, attrs=None):
        if value:
            final_attrs = self.build_attrs(attrs, name=name)
            output = u'<input value="%s" type="hidden" %s />' % (value, flatatt(final_attrs))
            return mark_safe(output + str(self.choices.queryset.get(id=value)))
        else:
            return super(ReadOnlySelectWidget, self).render(name, value, attrs)


class DisablePopulatedText(forms.TextInput):
    def __init__(self, obj, attrs=None):
        self.object = obj
        super(DisablePopulatedText, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_text(self._format_value(value))
        if "__prefix__" not in name and not value:
            return format_html('<input{0} disabled />', flatatt(final_attrs))
        else:
            return format_html('<input{0} />', flatatt(final_attrs))


class DisableText(forms.TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        """Render the widget as an HTML string."""
        if value is not None:
            # Just return the value, as normal read_only fields do
            # Add Hidden Input otherwise the old fields are still required
            HiddenInput = forms.HiddenInput()
            return format_html("{}\n" + HiddenInput.render(name, value), self.format_value(value))
        else:
            return super().render(name, value, attrs, renderer)


# https://www.abidibo.net/blog/2017/10/16/add-data-attributes-option-tags-django-admin-select-field/
class DataAttributesSelect(Select):
    def __init__(self, attrs=None, choices=(), data={}):
        super(DataAttributesSelect, self).__init__(attrs, choices)
        self.data = data

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):  # noqa
        option = super(DataAttributesSelect, self).create_option(name, value, label, selected, index, subindex=None,
                                                                 attrs=None)  # noqa
        # adds the data-attributes to the attrs context var
        for data_attr, values in self.data.iteritems():
            option['attrs'][data_attr] = values[option['value']]
        return option


class HtmlWidget(widgets.Widget):
    """A widget to display HTML in admin fields."""
    input_type = None  # Subclasses must define this.

    def get_context(self, name, value, attrs=None):
        return {'widget': {
            'name': name,
            'value': value,
        }}

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        return mark_safe(u'%s' % value)


class PreviewWidget(forms.Widget):
    """A widget to display HTML in admin fields."""
    input_type = None  # Subclasses must define this.
    template_name = 'slider_template.html'

    def get_context(self, name, value, attrs=None):
        return {'widget': {
            'name': name,
            'value': value,
        }}

    def render(self, name, value, attrs=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)


class DynamicArrayWidget(forms.TextInput):
    template_name = 'widgets/dynamic_array.html'

    def get_context(self, name, value, attrs):
        value = value or ['']
        context = super().get_context(name, value, attrs)
        final_attrs = context['widget']['attrs']
        id_ = context['widget']['attrs'].get('id')

        subwidgets = []
        for index, item in enumerate(context['widget']['value']):
            widget_attrs = final_attrs.copy()
            if id_:
                widget_attrs['id'] = '%s_%s' % (id_, index)
            widget = forms.TextInput()
            widget.is_required = self.is_required
            subwidgets.append(widget.get_context(name, item, widget_attrs)['widget'])

        context['widget']['subwidgets'] = subwidgets
        return context

    def value_from_datadict(self, data, files, name):
        try:
            getter = data.getlist
        except AttributeError:
            getter = data.get
        return getter(name)

    def format_value(self, value):
        return value or []


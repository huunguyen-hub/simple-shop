from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def set_global_context(context, key, value):
    """
    Sets a value to the global template context, so it can
    be accessible across blocks.

    Note that the block where the global context variable is set must appear
    before the other blocks using the variable IN THE BASE TEMPLATE.  The order
    of the blocks in the extending template is not important.

    Usage::
        {% extends 'base.html' %}

        {% block first %}
            {% set_global_context 'foo' 'bar' %}
        {% endblock %}

        {% block second %}
            {{ foo }}
        {% endblock %}
    """
    context.dicts[0][key] = value
    return ''


class GlobalVariable(object):
    def __init__(self, varname, varval):
        self.varname = varname
        self.varval = varval

    def name(self):
        return self.varname

    def value(self):
        return self.varval

    def set(self, newval):
        self.varval = newval


class GlobalVariableSetNode(template.Node):
    def __init__(self, varname, varval):
        self.varname = varname
        self.varval = varval

    def render(self, context):
        gv = context.get(self.varname, None)
        if gv:
            gv.set(self.varval)
        else:
            gv = context[self.varname] = GlobalVariable(
                self.varname, self.varval)
        return ''


def setglobal(parser, token):
    try:
        tag_name, varname, varval = token.contents.split(None, 2)
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires 2 arguments" % token.contents.split()[0])
    return GlobalVariableSetNode(varname, varval)


register.tag('setglobal', setglobal)


class GlobalVariableGetNode(template.Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        try:
            return context[self.varname].value()
        except AttributeError:
            return ''


def getglobal(parser, token):
    try:
        tag_name, varname = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires arguments" % token.contents.split()[0])
    return GlobalVariableGetNode(varname)


register.tag('getglobal', getglobal)


class GlobalVariableIncrementNode(template.Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        gv = context.get(self.varname, None)
        if gv is None:
            return ''
        gv.set(int(gv.value()) + 1)
        return ''


def incrementglobal(parser, token):
    try:
        tag_name, varname = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires arguments" % token.contents.split()[0])
    return GlobalVariableIncrementNode(varname)


register.tag('incrementglobal', incrementglobal)

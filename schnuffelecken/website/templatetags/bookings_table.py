from django import template

register = template.Library()


@register.inclusion_tag('table.html')
def bookings_table(week, which):

    anchor, prev, next = None, None, None

    if which:
        anchor = "woche{}".format(which)
        prev = "woche{}".format(which - 1) if which > 1 else None
        next = "woche{}".format(which + 1) if which < 4 else None

    return {'week': week, 'anchor': anchor, 'prev': prev, 'next': next, 'current': which}

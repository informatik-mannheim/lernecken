from django import template

register = template.Library()


@register.inclusion_tag('table.html')
def bookings_table(week, which):
    """Reusable component that renders the booking table which is used
    in several places.
    """
    anchor, prev_week, next_week = None, None, None

    if which:
        anchor = "woche{}".format(which)
        prev_week = "woche{}".format(which - 1) if which > 1 else None
        next_week = "woche{}".format(which + 1) if which < 4 else None

    return {'week': week,
            'anchor': anchor,
            'prev': prev_week,
            'next': next_week,
            'current': which}

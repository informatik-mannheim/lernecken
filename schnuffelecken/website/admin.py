from django.contrib import admin

from website.models import Booking, Statistic

"""
Register model classes to be modifiable from the admin backend.
Only makes sense for persisted models, of course.
"""
admin.site.register(Booking)
admin.site.register(Statistic)
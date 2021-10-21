from datetime import datetime, timedelta
from django.contrib.auth.models import User
from calendar import HTMLCalendar
# from .models import Event
from aidApp.models import Appointment

class Calendar(HTMLCalendar):
	def __init__(self, hp, year=None, month=None,):
		self.year = year
		self.month = month
		self.hp = hp
		super(Calendar, self).__init__()

	# formats a day as a td
	# filter events by day
	def formatday(self, day, events):
		events_per_day = events.filter(appointment_date__day=day)
		d = ''
		for event in events_per_day:
			# d += f'<li> {event.patient} </li>'
			d += f'<li> {event.get_html_url} </li>'

		if day != 0:
			return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
		return '<td></td>'

	# formats a week as a tr 
	def formatweek(self, theweek, events):
		week = ''
		for d, weekday in theweek:
			week += self.formatday(d, events)
		return f'<tr> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	def formatmonth(self, withyear=True):
		
		events = Appointment.objects.filter(appointment_date__year=self.year, appointment_date__month=self.month, health_practitioner=self.hp)

		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week, events)}\n'
		return cal
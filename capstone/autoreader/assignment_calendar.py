from calendar import HTMLCalendar
from django.urls import reverse
from datetime import datetime

class AssignmentCalendar(HTMLCalendar):
	cssclasses_weekday_head = ['weekday-header'] * 7
	cssclass_month_head = 'month-head'

	def __init__(self, firstweekday=0, assignments=[], is_current_month = True):
		super().__init__(firstweekday)
		self.assignments = assignments
		self.is_current_month = is_current_month

	def formatday(self, day, weekday):
		"""
		Return a day as a table cell.
		"""
		# assignments = '<br>' + self.assignments_to_html(self.assignments_due_on_day(day))
		assignments_due_today = self.assignments_due_on_day(day)
		assignment_links = '<br>' + '<br>'.join([self.assignment_link(assignment) for assignment in assignments_due_today])

		if day < datetime.now().day and self.is_current_month:
			background_css = 'day-in-past'
		else:
			background_css = 'day-in-future'

		if day == 0:
			# day outside month
			return '<td class="%s">&nbsp;%s</td>' % (self.cssclass_noday, assignment_links)
		else:
			return '<td class="%s %s">%d%s</td>' % (self.cssclasses[weekday], background_css, day, assignment_links)

	def assignments_due_on_day(self, day):
		return [a for a in self.assignments if a.due_date.day == day]

	def assignment_link(self, assignment):
		return '<a href="%s">%s</a>' % (
			reverse('autoreader:student_assignment', args=[assignment.course_id, assignment.id]),
			assignment.assignment_name,
		)

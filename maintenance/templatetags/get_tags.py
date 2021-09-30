from django import template

from core.generalSupportRoutines import MaintenanceDetails

register=template.Library()

def get_tags(tags):
	return (u",  ".join(o.name for o in  tags.all()))

register.filter('get_tags',get_tags)
from django import template

from core.generalSupportRoutines import MaintenanceDetails

register=template.Library()

def get_MaintenanceDetails(select):
	return MaintenanceDetails(select)

register.filter('get_MaintenanceDetails',get_MaintenanceDetails)
from django import template

from core.utilitySupportRoutines import getSupportLookup

register=template.Library()

def get_SupportLookup(select):
	return getSupportLookup(select)

register.filter('get_SupportLookup',get_SupportLookup)
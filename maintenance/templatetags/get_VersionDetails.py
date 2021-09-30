from django import template

from core.generalSupportRoutines import get_Version

register=template.Library()

def get_VersionDetails(select):
	return get_Version(select)

register.filter('get_VersionDetails',get_VersionDetails)


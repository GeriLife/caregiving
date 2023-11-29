from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from preferences.forms import PreferencesForm
from preferences.models import Preferences
from django.core import serializers

# this function creates a blank preference model form on GET request
# and returns a context with the form and the fields from the preference
# object tagged to the current user
# on non GET request we update the database to save the new preferences
@login_required
def setPreferences (request):
    context = {}
    if request.method == 'GET':
        context['form'] = PreferencesForm ()
        # null check for preferences field
        if request.user.preferences:
            fields = [(field.name, field.value_to_string(request.user.preferences)) for field in Preferences._meta.fields]
            context['fields'] = fields
        return render(request, '../templates/preferences.html', context)

    # for any other request type that is not GET
    form = PreferencesForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, '../templates/preferences.html', context)

    preferences = Preferences(
                Language = form.cleaned_data['Language'], 
                Mode = form.cleaned_data['Mode'],
                )

    preferences.save ()

    request.user.preferences = preferences
    request.user.save ()

    # extract the fields to be displayed from the preferences
    fields = [(field.name, field.value_to_string(request.user.preferences)) for field in Preferences._meta.fields]
    context['fields'] = fields

    return render(request, '../templates/preferences.html', context)
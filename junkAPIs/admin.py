from django.contrib import admin
from django.apps import apps

junk_models = apps.get_models()
for model in junk_models:
    try:
        if model._meta.model_name != 'tokenproxy':
            admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass

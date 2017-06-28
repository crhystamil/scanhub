from django.contrib import admin
from .models import Collection
from .models import Host
from .models import Port

admin.site.register(Collection)
admin.site.register(Host)
admin.site.register(Port)


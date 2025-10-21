from django.contrib import admin
from .models import Students,Contest,IsLogin,ContestLeaderboard

# Register your models here.
admin.site.register(Students)
admin.site.register(Contest)
admin.site.register(IsLogin)
admin.site.register(ContestLeaderboard)
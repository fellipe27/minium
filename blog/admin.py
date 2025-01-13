from django.contrib import admin
from .models import Post

class PostAdmin(admin.ModelAdmin):
    model = Post
    list_display = ('title', 'author', 'created_at')
    fieldsets = (
        ('Post Info', { 'fields': ('id', 'title', 'content', 'author', 'created_at') }),
    )
    readonly_fields = ('id',)

admin.site.register(Post, PostAdmin)

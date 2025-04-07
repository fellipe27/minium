from django.contrib import admin
from .models import Post

class PostAdm(admin.ModelAdmin):
    model = Post
    list_display = ('title', 'story', 'created_at')
    fieldsets = (
        (None, {
            'fields': (
                'id', 'title', 'story', 'author', 'created_at'
            )
        }),
    )
    readonly_fields = ('id',)

admin.site.register(Post, PostAdm)

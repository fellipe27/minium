from django.contrib import admin
from .models import Post, Comment

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('id', 'content', 'created_at', 'author')

class PostAdmin(admin.ModelAdmin):
    model = Post
    list_display = ('title', 'author', 'created_at')
    fieldsets = (
        (None, {
            'fields': (
                'id', 'title', 'content', 'author', 'created_at', 'keywords', 'clap_count'
            )
        }),
    )
    readonly_fields = ('id', 'clap_count')

    def clap_count(self, obj):
        return obj.claps.count()

    clap_count.short_description = 'Claps'
    inlines = [CommentInline]

admin.site.register(Post, PostAdmin)

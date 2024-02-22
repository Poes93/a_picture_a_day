from django.contrib import admin
from .models import Post, Comment
from django_summernote.admin import SummernoteModelAdmin


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):

    list_display = ('title', 'slug', 'status', 'created_on', 'updated_on', 'mood')
    search_fields = ['title', 'content']
    list_filter = ('status', 'created_on', 'updated_on', 'mood')
    prepopulated_fields = {'slug': ('title',)}
    summernote_fields = ('content',)
    actions = ['make_published']

    def make_published(self, request, queryset):
        queryset.update(status=1)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'body', 'post', 'created_on', 'email', 'name')
    list_filter = ('created_on',)
    search_fields = ('name', 'email', 'body')

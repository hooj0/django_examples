from django.contrib import admin

from apps.polls.models import Question, Choice


# Register your models here.
# StackedInline 允许在同一行中添加或删除字段
# TabularInline 允许在表格中添加或删除字段
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3
    classes = ['collapse']

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('Date Info', {'fields': ['published_date'], 'classes': ['collapse']})
    ]
    inlines = [ChoiceInline]
    list_display = ('question_text', 'published_date', 'was_published_recently')
    list_filter = ['published_date']
    search_fields = ['question_text']

admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
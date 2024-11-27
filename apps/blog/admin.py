from django.contrib import admin

# Register your models here.
from .models import Post, Choices, Comment, Book, Author

admin.site.register(Post)
admin.site.register(Choices)
admin.site.register(Comment)
admin.site.register(Book)
admin.site.register(Author)
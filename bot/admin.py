from django.contrib import admin

# Register your models here.
from .models import Post, Region, User




admin.site.register(Region)
admin.site.register(User)





class PostAdmin(admin.ModelAdmin):
    model = Post
    def has_add_permission(self, request) -> bool:
        return not Post.objects.exists()


admin.site.register(Post, PostAdmin)

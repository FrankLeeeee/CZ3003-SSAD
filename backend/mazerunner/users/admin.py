from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.shortcuts import render
from django.urls import path
from django.template.response import TemplateResponse

from .models import User


   # email = models.EmailField(max_length=255, unique=True)
   # name = models.CharField(max_length=100)
   ## distanceToNPC = models.IntegerField(default = 0)
   ## overallScore= models.IntegerField(default = 0)
   # containBonus = models.BooleanField(default = False)
   # role = models.CharField(max_length=30)

   # is_active = models.BooleanField(default=True)
   # is_staff = models.BooleanField(default=False)

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'name','distanceToNPC','overallScore','containBonus','role' , 'is_staff')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user



   # email = models.EmailField(max_length=255, unique=True)
   # name = models.CharField(max_length=100)
   ## distanceToNPC = models.IntegerField(default = 0)
   ## overallScore= models.IntegerField(default = 0)
   # containBonus = models.BooleanField(default = False)
   # role = models.CharField(max_length=30)

   # is_active = models.BooleanField(default=True)
   # is_staff = models.BooleanField(default=False)

class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password =  forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'password', 'name', 'distanceToNPC','overallScore','containBonus','role','is_active', 'is_staff')

    #def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
     #   return self.initial["password"]

class UserAdmin(BaseUserAdmin, admin.ModelAdmin):
    change_form_template = 'users/custom_change_form.html'

    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    def save_model(self, request, obj, form, change):

    # Override this to set the password to the value in the field if it's
    # changed.
        if obj.pk:
            orig_obj = User.objects.get(pk=obj.pk)
            if obj.password != orig_obj.password:
                obj.set_password(obj.password)
        else:
            obj.set_password(obj.password)
        obj.save()

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'password', 'name', 'distanceToNPC','overallScore','containBonus','role','is_active', 'is_staff')
    list_filter = ('is_staff',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'distanceToNPC','overallScore','containBonus','role',)}),
        ('Permissions', {'fields': ('is_staff',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'distanceToNPC','overallScore','containBonus','role','is_staff', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


#    def get_urls(self):
#        urls = super().get_urls()
#        my_urls = [
#            path('stats/', self.gostats)
#        ]
#        return my_urls + urls

#    def gostats(self, request):
#        return TemplateResponse(
#            request,
#            'users/post_assignment.html',
#           context,
#       )


# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)



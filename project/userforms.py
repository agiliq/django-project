from django import newforms as forms
import re
from django.newforms import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.sites.models import Site
from django.template import Context, loader
from django.utils.translation import ugettext as _

class PasswordResetForm(forms.Form):
    """A form that lets a user request a password reset"""
    email = forms.EmailField(required = True)

    def clean_email (self):
        try:
           self.user = User.objects.get(email__iexact=self.cleaned_data['email'])
        except User.DoesNotExist:
            print '***'
            raise ValidationError(_("That e-mail address doesn't have an associated user account. Are you sure you've registered?"))
        return self.cleaned_data['email']

    def save(self, domain_override=None, email_template_name='registration/password_reset_email.html'):
        "Calculates a new password randomly and sends it to the user"
        from django.core.mail import send_mail
        user = self.user
        new_pass = User.objects.make_random_password()
        user.set_password(new_pass)
        user.save()
        if not domain_override:
            current_site = Site.objects.get_current()
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        t = loader.get_template(email_template_name)
        c = {
        'new_password': new_pass,
        'email': user.email,
        'domain': domain,
        'site_name': site_name,
        'user': user,
        }
        send_mail(_('Password reset on %s') % site_name, t.render(Context(c)), None, [user.email])

class PasswordChangeForm(forms.Form):
    """A form that lets a user change his password."""
    old_password = forms.CharField(widget=forms.PasswordInput, required = True, max_length = 30)
    new_password1 = forms.CharField(widget=forms.PasswordInput, required = True, max_length = 30)
    new_password2 = forms.CharField(widget=forms.PasswordInput, required = True, max_length = 30)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        

    def clean_old_password (self):
        if not self.user.check_password(self.cleaned_data['old_password']):
            raise ValidationError(_("Your old password was entered incorrectly. Please enter it again."))
        return self.cleaned_data['old_password']

    def clean (self):
         if self.cleaned_data['new_password1'] != self.cleaned_data['new_password2']:
             raise ValidationError(_("The two new password fields didn't match."))
         return super(forms.Form, self).clean()

    def save (self):
        "Saves the new password."
        self.user.set_password(self.cleaned_data['new_password1'])
        self.user.save()


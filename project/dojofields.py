from django import forms

class DojoCharField(forms.CharField):
    def __init__(self, *args, **kwargs):
        if kwargs.get('required', True):
            if not kwargs.has_key('widget'):
                kwargs.update({'widget' : forms.TextInput(attrs={'class':'textfield required input'})})
        else:
            if not kwargs.has_key('widget'):
                kwargs.update({'widget' : forms.TextInput(attrs={'class':'textfield input'})})
        super(DojoCharField, self).__init__(*args, **kwargs)

class DojoPasswordField(forms.CharField):
    def __init__(self, *args, **kwargs):
        if kwargs.get('required', True):
            if not kwargs.has_key('widget'):
                kwargs.update({'widget' : forms.PasswordInput(attrs={'class':'textfield required input'})})
        else:
            if not kwargs.has_key('widget'):
                kwargs.update({'widget' : forms.PasswordInput(attrs={'class':'textfield input'})})
        super(DojoPasswordField, self).__init__(*args, **kwargs)        
        
class DojoDateField(forms.CharField):
    def __init__(self, *args, **kwargs):
        if kwargs.get('required', True):
            if not kwargs.has_key('widget'):
                kwargs.update({'widget' : forms.TextInput(attrs={'class':'datefield required input'})})
        else:
            if not kwargs.has_key('widget'):
                kwargs.update({'widget' : forms.TextInput(attrs={'class':'datefield input'})})
        
        super(DojoDateField, self).__init__(*args, **kwargs)
        
class DojoDecimalField(forms.DecimalField):
    def __init__(self, *args, **kwargs):
        if kwargs.get('required', True):
            if not kwargs.has_key('widget'):
                kwargs.update({'widget' : forms.TextInput(attrs={'class':'required number input'})})
        else:
            if not kwargs.has_key('widget'):
                kwargs.update({'widget' : forms.TextInput(attrs={'class':'number input'})})
        super(DojoDecimalField, self).__init__(*args, **kwargs)

class DojoChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        if kwargs.get('required', True):
            if not kwargs.has_key('widget'):
                kwargs.update({'widget' : forms.Select(attrs={'class':'required'})})
        super(DojoChoiceField, self).__init__(*args, **kwargs)
        
class DojoTextArea(forms.CharField):
    def __init__(self, *args, **kwargs):
        if kwargs.get('required', True):    
            if not kwargs.has_key('widget'):
                kwargs.update({'widget' : forms.Textarea(attrs={'class':'required'})})
        else:
            if not kwargs.has_key('widget'):
                kwargs.update({'widget' : forms.Textarea})
        super(DojoTextArea, self).__init__(*args, **kwargs)
        
class MarkedForm(forms.Form):
    """A form with a little more markup."""
    def as_p(self):
        "Returns this form rendered as HTML <p>s."
        return self._html_output(u'<p>%(label)s %(field)s<span class="help_text">%(help_text)s</span></p>', u'%s', '</p>', u' %s', True)
        
import django.newforms as forms

class DojoCharField(forms.CharField):
    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('widget'):
            kwargs.update({'widget' : forms.TextInput(attrs={'dojoType':'dijit.form.TextBox'})})                          
        super(DojoCharField, self).__init__(*args, **kwargs)
        
        
class DojoDateField(forms.CharField):
    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('widget'):
            kwargs.update({'widget' : forms.TextInput(attrs={'dojoType':'dijit.form.DateTextBox'})})                          
        super(DojoDateField, self).__init__(*args, **kwargs)
        
class DojoDecimalField(forms.DecimalField):
    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('widget'):
            kwargs.update({'widget' : forms.TextInput(attrs={'dojoType':'dijit.form.NumberTextBox'})})                          
        super(DojoDecimalField, self).__init__(*args, **kwargs)    

class DojoChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('widget'):
            kwargs.update({'widget' : forms.Select(attrs={'dojoType':'dijit.form.ComboBox'})})                          
        super(DojoChoiceField, self).__init__(*args, **kwargs)
        
class DojoTextArea(forms.CharField):
    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('widget'):
            #kwargs.update({'widget' : forms.Textarea})
            kwargs.update({'widget' : forms.Textarea(attrs={'dojoType':'dijit.Editor', 'width':'300px'})})                          
        super(DojoTextArea, self).__init__(*args, **kwargs)          
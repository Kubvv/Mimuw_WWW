from django import forms
from .models import Directory, File
from django.core.exceptions import ValidationError

tab_options = {
    "prover": [
        "None",
        "Alt-Ergo",
        "cvc4",
        "Z3"
    ],

    "vcs": [
        "@invariant", 
        "@lemma", 
        "@ensures", 
        "@requires", 
        "@assigns", 
        "@exits",
        "@assert",
        "@check",
        "@variant",
        "@breaks",
        "@continues",
        "@returns"
    ]
}

class DirectoryCreate(forms.ModelForm):
    class Meta:
        model = Directory
        fields = ['name', 'description', 'parentDirectory']

class FileCreate(forms.ModelForm):
    class Meta:
        model = File
        fields = ['name', 'description', 'ffile', 'directory']

    def clean_ffile(self, *args, **kwargs):
        ffile = self.cleaned_data.get("ffile")
        fname = ffile.name.translate ({
            ord('.'): None,
            ord('_'): None,
            ord('-'): None
        })
        if fname.isalnum():
            return ffile
        raise ValidationError("File name can contain alphanumeric characters and dot, dash, minus signs only")

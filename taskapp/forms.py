# from django import forms
# from .models import task

# class TaskForm(forms.ModelForm):
#     class Meta:
#         model = task
#         fields = ['first_name', 'last_name', 'technology', 'mail_id', 'salary']
from django import forms
from .models import task, Technology  # Ensure you import the Technology model

class TaskForm(forms.ModelForm):
    class Meta:
        model = task
        fields = ['first_name', 'last_name', 'technology', 'mail_id', 'salary']

    technology = forms.ModelMultipleChoiceField(
        queryset=Technology.objects.all(),  # Get all technologies
        widget=forms.CheckboxSelectMultiple,  # Render as checkboxes
        required=False  # Make this optional if needed
    )

    def clean(self):
        cleaned_data = super().clean()
        
        # Trim spaces for specific fields
        for field in cleaned_data:
            cleaned_data[field] = cleaned_data[field].strip() if isinstance(cleaned_data[field], str) else cleaned_data[field]

        return cleaned_data

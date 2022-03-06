from django import forms

class NewPostForm(forms.Form):
    post_text = forms.Field(widget=forms.Textarea(
        {'rows': '3', 'maxlength': 160, 'class': 'form-control', 'placeholder': "Post Something"}), label="New Post", required=True)
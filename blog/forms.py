from django import forms
from .models import Post, Category, Comment

class PostForm(forms.ModelForm):
    # Add a field for category selection; assumes categories are predefined
    categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Post
        fields = ['photo', 'caption', 'text', 'mood']
        widgets = {
            'mood': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        # Initialize your category field here if needed

    def save(self, *args, **kwargs):
        instance = super(PostForm, self).save(commit=False)
        self.fields['categories'].initial.update(instance.post_categories.all())
        instance.save()
        # Assuming you're handling category assignment in your view
        return instance


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


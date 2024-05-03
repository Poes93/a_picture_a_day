from django import forms
from .models import Comment, Post
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import FormActions

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content', 'mood', 'status', 'featured_image')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        # Set the choices to match the integer values expected by the model
        self.fields['status'].choices = [
            (0, 'Draft'),  # 0 for Draft
            (1, 'Publish')  # 1 for Publish
        ]
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'title',
            'content',
            'mood',
            'status',
            'featured_image',
            FormActions(
                Submit('submit', 'Save Post', css_class='btn-primary')
            )
        )

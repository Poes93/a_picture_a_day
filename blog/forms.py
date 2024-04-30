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
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save Post'))
        self.helper.layout = Layout(
            'title',
            'content',
            'mood',
            'status',
            'featured_image',
            FormActions(
                Submit('save', 'Save Changes'),
                Submit('cancel', 'Cancel', css_class='btn-secondary')
            )
        )

from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'group': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'text': 'текст поста',
            'group': 'наименование группы',
        }
        help_texts = {
            'text': 'текст нового поста',
            'group': 'группа поста',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

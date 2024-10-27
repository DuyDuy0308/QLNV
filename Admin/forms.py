from django import forms
from .models import News, Lesson, Lesson_KN, Slide, Taikhoan


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'media']

class LessonUploadForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'video', 'image', 'ppt', 'vip_only']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'video': forms.FileInput(attrs={'class': 'form-control-file'}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
            'ppt': forms.FileInput(attrs={'class': 'form-control-file'}),
            'vip_only': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class LessonUploadForm_KN(forms.ModelForm):
    class Meta:
        model = Lesson_KN
        fields = ['title', 'description', 'video', 'image', 'ppt', 'vip_only']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'video': forms.FileInput(attrs={'class': 'form-control-file'}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
            'ppt': forms.FileInput(attrs={'class': 'form-control-file'}),
            'vip_only': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class TaikhoanForm(forms.ModelForm):
    class Meta:
        model = Taikhoan
        fields = ['tai_khoan', 'mat_khau', 'phan_quyen', 'khachhang']
        widgets = {
            'mat_khau': forms.PasswordInput(),
        }

    def clean_mat_khau(self):
        password = self.cleaned_data.get('mat_khau')
        # Additional password validation can go here
        return password
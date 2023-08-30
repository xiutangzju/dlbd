# -*- coding: UTF-8 -*-
from django import forms


class MyForm:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环ModelForm中的所有字段，给每个字段的插件设置
        for name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})


class BootstrapForm(MyForm, forms.Form):
    pass


class BootstrapModalForm(MyForm, forms.ModelForm):
    pass

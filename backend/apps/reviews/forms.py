from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        coerce=int,
        choices=[(value, f"{value} star{'s' if value != 1 else ''}") for value in range(5, 0, -1)],
        widget=forms.RadioSelect,
    )
    title = forms.CharField(
        required=False,
        max_length=80,
        widget=forms.TextInput(attrs={"class": "input", "autocomplete": "off"}),
    )
    body = forms.CharField(
        min_length=10,
        max_length=1000,
        widget=forms.Textarea(attrs={"class": "textarea", "rows": 5}),
    )

    class Meta:
        model = Review
        fields = ("rating", "title", "body")

from django import forms


class CancelRideForm(forms.Form):
    reason = forms.CharField(
        min_length=5,
        max_length=500,
        strip=True,
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="Tell the rider why you are cancelling (5–500 characters).",
    )
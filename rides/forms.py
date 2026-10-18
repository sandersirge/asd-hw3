from django import forms


class CancelRideForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="Tell the rider why you are cancelling.",
    )
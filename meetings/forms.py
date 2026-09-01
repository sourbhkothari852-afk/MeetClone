from django import forms

from .models import Meeting


class MeetingForm(forms.ModelForm):

    class Meta:

        model = Meeting

        fields = [
            "title",
            "description",
            "scheduled_at",
        ]

        widgets = {

            "title": forms.TextInput(
                attrs={
                    "placeholder": "Enter meeting title",
                    "autocomplete": "off",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "placeholder": "Enter meeting description (optional)",
                    "rows": 4,
                }
            ),

            "scheduled_at": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                }
            ),
        }


    # =====================================================
    # TITLE VALIDATION
    # =====================================================

    def clean_title(self):

        title = self.cleaned_data["title"].strip()

        if not title:

            raise forms.ValidationError(
                "Meeting title is required."
            )

        return title


    # =====================================================
    # DESCRIPTION
    # =====================================================

    def clean_description(self):

        description = (
            self.cleaned_data.get("description") or ""
        )

        return description.strip()


    
class JoinMeetingForm(forms.Form):

    meeting_code = forms.CharField(
        max_length=20,
        label="Meeting Code",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter meeting code",
                "autocomplete": "off",
                "class": "meeting-code-input",
            }
        )
    )


    def clean_meeting_code(self):

        meeting_code = (
            self.cleaned_data["meeting_code"]
            .strip()
            .upper()
        )

        if not meeting_code:

            raise forms.ValidationError(
                "Please enter a meeting code."
            )

        return meeting_code
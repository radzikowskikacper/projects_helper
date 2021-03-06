from django.core.exceptions import NON_FIELD_ERRORS
from django import forms
from django.db.models import Count
from projects_helper.apps.teams.models import Team
from projects_helper.apps.courses.models import Course
from projects_helper.apps.projects.models import Project
from projects_helper.apps.students.models import Student
from django.utils.translation import ugettext_lazy as _
from markdownx.widgets import MarkdownxWidget


class UploadFileForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={'style':'display:none'})
    )

class CustomMarkdownxWidget(MarkdownxWidget):
    template_name = 'lecturers/markdown-widget.html'

class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ['title', 'description']
        required_css_class = 'required'
        widgets = {
            'title': forms.TextInput(attrs={'autofocus': ''}),
            'description' : CustomMarkdownxWidget()
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together':
                    _("%(model_name)s's %(field_labels)s are not unique."),
            }
        }

# this callables will be necessary to avoid executing queries
# at the time this models.py is imported
def get_Students_with_no_team_or_alone(currCourse, team=None):
    # Returns students that have no team on currCourse
    # OR students that have such team but are alone in that team
    # AND the team is NOT assigned to any project
    teams_with_up_to_one_stud = Team.objects.annotate(
        num_Stud=Count('student')).filter(course=currCourse, num_Stud__gte=2)
    return Student.objects.filter(teams__course=currCourse, teams__project=None) \
        .exclude(teams__in=teams_with_up_to_one_stud)


def get_Projects_with_no_assigned_team(currCourse, lecturer):
    return Project.objects.filter(course=currCourse, lecturer=lecturer, team_assigned=None)


class TeamForm(forms.Form):

    member_1 = forms.ModelChoiceField(
        queryset=None,
        label=_("Add team member"),
        required=True
    )

    next_stud_check = forms.BooleanField(
        label=_("Add another member"),
        required=False,
    )

    member_2 = forms.ModelChoiceField(
        queryset=None,
        label="",
        required=False,
    )

    project_check = forms.BooleanField(
        label=_("Assign this team to existing project"),
        required=False,
    )

    project = forms.ModelChoiceField(
        queryset=None,
        label="",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        try:
            lecturer = kwargs.pop('lecturer')
            course = kwargs.pop('course')
        except KeyError as e:
            print("Exception: TeamModifyForm: missing key argument: " + str(e))

        super(TeamForm, self).__init__(*args, **kwargs)
        self.fields['project'].queryset = \
            get_Projects_with_no_assigned_team(course, lecturer)
        self.fields['member_1'].queryset = get_Students_with_no_team_or_alone(course)
        self.fields['member_2'].queryset = get_Students_with_no_team_or_alone(course)
        self.fields['member_2'].widget.attrs['style'] = 'display:none'
        self.fields['member_2'].widget.attrs['id'] = 'member_2_select'
        self.fields['project'].widget.attrs['style'] = 'display:none'
        self.fields['project'].widget.attrs['id'] = 'project_select'
        self.fields['next_stud_check'].widget.attrs[
            'onclick'] = "javascript:toggleDiv('member_2_select');"
        self.fields['project_check'].widget.attrs[
            'onclick'] = "javascript:toggleDiv('project_select');"


class TeamModifyForm(forms.Form):

    display_member_1 = forms.CharField(
        label="Student 1",
        required=False,
    )

    display_member_2 = forms.CharField(
        label="Student 2",
        required=False,
    )

    member_1_select = forms.ModelChoiceField(
        queryset=None,
        label="",
        empty_label=_("None"),
        required=False
    )

    change_member_1 = forms.BooleanField(
        label=_("Change"),
        required=False,
    )

    member_2_select = forms.ModelChoiceField(
        queryset=None,
        label="",
        empty_label=_("None"),
        required=False,
    )

    change_member_2 = forms.BooleanField(
        label=_("Change"),
        required=False,
    )

    display_project = forms.CharField(
        label=_("Assigned project"),
        required=False,
    )

    change_project = forms.BooleanField(
        label=_("Change"),
        required=False,
    )

    project_select = forms.ModelChoiceField(
        queryset=None,
        label="",
        empty_label=_("None"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        try:
            lecturer = kwargs.pop('lecturer')
            team = kwargs.pop('team')
            course = kwargs.pop('course')
        except KeyError as e:
            print("Exception: TeamModifyForm: missing key argument: " + str(e))

        super(TeamModifyForm, self).__init__(*args, **kwargs)

        self.fields['project_select'].queryset = \
            get_Projects_with_no_assigned_team(course, lecturer)
        self.fields['member_1_select'].queryset = \
            get_Students_with_no_team_or_alone(course)
        self.fields['member_2_select'].queryset = \
            get_Students_with_no_team_or_alone(course)

        self.fields['display_member_1'].widget.attrs['readonly'] = 'true'
        self.fields['display_member_2'].widget.attrs['readonly'] = 'true'
        self.fields['display_project'].widget.attrs['readonly'] = 'true'
        self.fields['display_member_1'].initial = _("None")
        self.fields['display_member_2'].initial = _("None")
        self.fields['display_project'].initial = _("None")

        if team.project_assigned:
            self.fields['display_project'].initial = team.project_assigned

        members = team.team_members
        if members:
            if len(members) == 1:
                self.fields['display_member_1'].initial = members[0]
            elif len(members) == 2:
                self.fields['display_member_1'].initial = members[0]
                self.fields['display_member_2'].initial = members[1]

        # hide selects
        self.fields['member_1_select'].widget.attrs['style'] = 'display:none'
        self.fields['member_2_select'].widget.attrs['style'] = 'display:none'
        self.fields['project_select'].widget.attrs['style'] = "display:none;width:100%"

        # set ids
        self.fields['member_2_select'].widget.attrs['id'] = 'member_2_select'
        self.fields['member_1_select'].widget.attrs['id'] = 'member_1_select'
        self.fields['project_select'].widget.attrs['id'] = 'project_select'

        # add js
        self.fields['change_member_1'].widget.attrs[
            'onclick'] = "javascript:toggleDiv('member_1_select');"
        self.fields['change_member_2'].widget.attrs[
            'onclick'] = "javascript:toggleDiv('member_2_select');"
        self.fields['change_project'].widget.attrs[
            'onclick'] = "javascript:toggleDiv('project_select');"

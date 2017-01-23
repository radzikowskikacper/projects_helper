from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from projects_helper.apps.common.models import Project, Course, Team
from projects_helper.apps.students.models import Student
from projects_helper.apps.lecturers.forms import ProjectForm, TeamForm, TeamModifyForm


def is_lecturer(user):
    return user.user_type == "L" or user.is_superuser


@login_required
@user_passes_test(is_lecturer)
def profile(request):
    course = get_object_or_404(
        Course, code__iexact=request.session['selectedCourse'])
    return render(request,
                  "lecturers/profile.html",
                  {'selectedCourse': course})


@login_required
@user_passes_test(is_lecturer)
def project_list(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    projects = Project.objects.filter(
        lecturer=request.user.lecturer).filter(course=course)
    return render(request,
                  template_name="lecturers/project_list.html",
                  context={"projects": projects,
                           "selectedCourse": course})


@login_required
@user_passes_test(is_lecturer)
def filtered_project_list(request, course_code=None):
    title = request.GET.get('title')
    course = get_object_or_404(Course, code__iexact=course_code)
    projects = Project.objects.filter(
        lecturer=request.user.lecturer).filter(course=course)
    filtered_projects = projects.filter(title__icontains=title)

    return render(request,
                  template_name="lecturers/project_list.html",
                  context={"projects": filtered_projects,
                           "selectedCourse": course})


@login_required
@user_passes_test(is_lecturer)
def project(request, project_pk, course_code=None):
    proj = Project.objects.get(pk=project_pk)
    course = get_object_or_404(Course, code__iexact=course_code)
    return render(request, "lecturers/project_detail.html",
                  context={'project': proj,
                           'selectedCourse': course})


@login_required
@user_passes_test(is_lecturer)
def project_delete(request):
    projects_to_delete = Project.objects.filter(
        pk__in=request.POST.getlist('to_delete'))

    for proj in projects_to_delete:
        if proj.lecturer.user == request.user:
            if proj.status() == 'free':
                proj.delete()
            else:
                messages.info(request, _(
                    "Cannot delete occupied project: ") + proj.title)
        else:
            messages.error(request,
                           _("Cannot delete project: " + proj.title + " - access denied"))
    return redirect(reverse('lecturers:project_list',
                            kwargs={'course_code': request.session['selectedCourse']}))


@login_required
@user_passes_test(is_lecturer)
def project_new(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    form = ProjectForm(request.POST or None)
    context = {
        'form': form,
        'selectedCourse': course
    }

    if form.is_valid():
        try:
            proj = form.save(commit=False)
            proj.lecturer = request.user.lecturer
            proj.course = course
            proj.save()
        except IntegrityError:
            messages.error(request, _(
                "\n You must provide unique project name"))
            return render(request, "lecturers/project_new.html", context)

        messages.success(request, _(
            "You have succesfully added new project: ") + proj.title)
        return redirect(reverse('lecturers:project_list',
                                kwargs={'course_code': course_code}))

    # GET
    return render(request, "lecturers/project_new.html", context)


@login_required
@user_passes_test(is_lecturer)
def modify_project(request, project_pk, course_code=None):
    proj = get_object_or_404(Project, pk=project_pk)
    form = ProjectForm(request.POST or None, instance=proj)
    course = get_object_or_404(Course, code__iexact=course_code)

    if form.is_valid():
        try:
            form.save()
        except IntegrityError:
            messages.error(request, _(
                "\n You must provide unique project name"))
            return redirect(reverse("lecturers:modify_project",
                                    kwargs={'project_pk': proj.pk,
                                            'course_code': course_code}))

        messages.success(request, _(
            "You have successfully updated project: ") + proj.title)
        return redirect(reverse('lecturers:project_list',
                                kwargs={'course_code': course_code}))

    return render(request, "lecturers/project_modify.html",
                  context={'form': form,
                           'project': proj,
                           'selectedCourse': course})


@login_required
@user_passes_test(is_lecturer)
def project_copy(request, project_pk, course_code=None):
    new_proj = get_object_or_404(Project, pk=project_pk)
    new_proj.pk = None  # autogen a new pk
    new_proj.title = new_proj.title + " - " + str(_("copy"))
    form = ProjectForm(request.POST or None, instance=new_proj)
    course = get_object_or_404(Course, code__iexact=course_code)
    context = {
        'form': form,
        'selectedCourse': course
    }

    if form.is_valid():
        try:
            form.save()
        except IntegrityError:
            messages.error(request, _(
                "\n You must provide unique project name"))
            return render(request, "lecturers/project_new.html", context)

        messages.success(request, _(
            "You have succesfully added new project: ") + new_proj.title)
        return redirect(reverse('lecturers:project_list',
                                kwargs={'course_code': course_code}))

    return render(request, "lecturers/project_new.html", context)


@login_required
@user_passes_test(is_lecturer)
def team_list(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    my_teams = Team.objects.filter(project_preference__lecturer=request.user.lecturer).filter(
        course=course).exclude(project_preference__isnull=True)
    teams_with_no_project = Team.objects.filter(project_preference__isnull=True)
    return render(request,
                  template_name="lecturers/team_list.html",
                  context={"teams": my_teams,
                           "teams_with_no_project": teams_with_no_project,
                           "selectedCourse": course})


@login_required
@user_passes_test(is_lecturer)
def team_new(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    form = None
    if request.method == 'POST':
        form = TeamForm(request.POST, lecturer=request.user.lecturer)
    else:
        form = TeamForm(lecturer=request.user.lecturer)
    context = {
        'form': form,
        'selectedCourse': course
    }

    if request.method == 'POST' and form.is_valid():
        stud_1 = form.cleaned_data['member_1']
        next_stud = form.cleaned_data['next_stud_check']
        stud_2 = form.cleaned_data['member_2']
        project_check = form.cleaned_data['project_check']
        proj = form.cleaned_data['project']
        try:
            with transaction.atomic():
                new_team = Team.objects.create(course=course)
                if project_check and proj:
                    new_team.select_preference(proj)
                    new_team.save()
                    proj.assign_team(new_team)
                    proj.save()
                if stud_1.team and not stud_1.team.is_full:
                    stud_1.team.delete()
                stud_1.team = new_team
                stud_1.save()
                if next_stud and stud_2:
                    if stud_2.team and not stud_2.team.is_full:
                        stud_2.team.delete()
                    stud_2.team = new_team
                    stud_2.save()

        except IntegrityError as e:
            print("Exception: " + str(e))
            messages.error(request, _(
                "Something went wrong. Try again."))
            return render(request, "lecturers/team_new.html", context)

        messages.success(request, _(
            "You have succesfully added new team: ") + str(new_team))
        return redirect(reverse('lecturers:team_list',
                                kwargs={'course_code': course_code}))

    # GET
    return render(request, "lecturers/team_new.html", context)


@login_required
@user_passes_test(is_lecturer)
def modify_team(request, team_pk, course_code=None):
    team = get_object_or_404(Team, pk=team_pk)
    team_str = str(team)
    course = get_object_or_404(Course, code__iexact=course_code)
    members = team.team_members

    if request.method == 'POST':
        form = TeamModifyForm(request.POST, lecturer=request.user.lecturer, team=team)
    else:
        form = TeamModifyForm(lecturer=request.user.lecturer, team=team)

    if form.is_valid():
        stud_1 = form.cleaned_data['member_1_select']
        stud_2 = form.cleaned_data['member_2_select']
        proj_pref = form.cleaned_data['project_preffered_select']
        proj = form.cleaned_data['project_select']
        change_member_1 = form.cleaned_data['change_member_1']
        change_member_2 = form.cleaned_data['change_member_2']
        change_project_pref = form.cleaned_data['change_preffered_project']
        change_project = form.cleaned_data['change_project']

        try:
            deleted_count = 0
            with transaction.atomic():
                if not team.course:
                    team.course = course
                    team.save()
                if change_member_1:
                    if members and stud_1 not in members:
                        members[0].team = None
                        members[0].save()
                        if stud_1:
                            if stud_1.team and not stud_1.team.is_full:
                                stud_1.team.delete()
                            stud_1.team = team
                            stud_1.save()
                        else:
                            deleted_count += 1
                if change_member_2:
                    if stud_2 not in members:
                        if len(members) > 1:
                            members[1].team = None
                            members[1].save()
                        if stud_2:
                            if stud_2.team and not stud_2.team.is_full:
                                stud_2.team.delete()
                            stud_2.team = team
                            stud_2.save()
                        else:
                            deleted_count += 1
                if len(members) == deleted_count:
                    if deleted_count == 2:
                        messages.success(request, _(
                            "You have successfully deleted team: ") + team_str)
                    team.delete()
                    return redirect(reverse('lecturers:team_list',
                                        kwargs={'course_code': course_code}))

                if change_project:
                    if team.project_assigned != proj:
                        team.project_preference = proj
                        team.save()
                        if team.project_assigned:
                            project_to_unassign = team.project_assigned
                            project_to_unassign.assign_team(None)
                            project_to_unassign.save()
                        if proj:
                            proj.assign_team(team)
                            proj.save()
                elif change_project_pref:
                    if team.project_preference != proj_pref:
                        if team.project_assigned \
                                and proj_pref != team.project_assigned:
                            messages.info(request,
                                    _("Cannot change project preference, "
                                    + " because this team is assigned."
                                    + " Unassign team first."))
                            return redirect(reverse('lecturers:team_list',
                                    kwargs={'course_code': course_code}))
                        team.project_preference = proj_pref
                        team.save()
        except IntegrityError as e:
            import sys, traceback
            import os
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno) +
                  os.linesep + str(e))
            messages.error(request, _(
                "Something went wrong. Try again."))
            return redirect(reverse('lecturers:team_list',
                                    kwargs={'course_code': course_code}))

        messages.success(request, _(
            "You have successfully updated team: ") + team_str)
        return redirect(reverse('lecturers:team_list',
                                kwargs={'course_code': course_code}))

    return render(request, "lecturers/team_modify.html",
                  context={'form': form,
                           'team': team,
                           'selectedCourse': course})


@login_required
@user_passes_test(is_lecturer)
def team_delete(request):
    teams_to_delete = Team.objects.filter(
        pk__in=request.POST.getlist('to_delete'))

    for team in teams_to_delete:
        if team.project_preference is None or team.project_preference.lecturer.user == request.user:
            messages.success(request, _(
                "You have succesfully deleted team: ") + str(team))
            team.delete()
        else:
            messages.error(request, _("Cannot delete team: " +
                                      str(team) + " - access denied"))
    return redirect(reverse('lecturers:team_list',
                            kwargs={'course_code': request.session['selectedCourse']}))


@login_required
@user_passes_test(is_lecturer)
def assign_selected_team(request, project_pk, team_pk):
    if request.method == 'POST':
        try:
            project = Project.objects.get(pk=project_pk)
            team = Team.objects.get(pk=team_pk)
        except ObjectDoesNotExist as e:
            print(str(e))
            messages.error(request, _(
                "Cannot assign team. Team or project not found!"))

        if project.lecturer.user == request.user:
            if team and project:
                project.assign_team(team)
                project.save()
                messages.success(request, _(
                    "You have successfully assigned team: " +
                    str(team) + " to project: " + str(project)))
        else:
            messages.error(request, _("Cannot assign: access denied"))

    return redirect(reverse_lazy('lecturers:project',
                                 kwargs={'project_pk': project.pk,
                                         'course_code': request.session['selectedCourse']}))


@login_required
@user_passes_test(is_lecturer)
def assign_team(request, project_pk):
    proj = Project.objects.get(pk=project_pk)
    if proj.lecturer.user == request.user:
        if proj.teams_with_preference().count() == 0:
            messages.error(request, _(
                "Cannot assign: No teams waiting for project"))
        else:
            proj.assign_random_team()
            messages.success(request, _(
                "You have successfully assigned team: " +
                str(proj.team_assigned) + " to project: " + str(proj)))
    else:
        messages.error(request, _("Cannot assign: access denied"))

    return redirect(reverse_lazy('lecturers:project',
                                 kwargs={'project_pk': proj.pk,
                                         'course_code': request.session['selectedCourse']}))


@login_required
@user_passes_test(is_lecturer)
def assign_teams_to_projects(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    projects = Project.objects.filter(
        lecturer=request.user.lecturer).filter(course=course)
    if projects:
        for proj in projects:
            proj.assign_random_team()
        messages.success(request, _(
            "You have successfully assigned teams to projects"))
    else:
        messages.info(request, _("You don't have any projects"))
    return redirect(reverse('lecturers:project_list',
                            kwargs={'course_code': course_code}))


@login_required
@user_passes_test(is_lecturer)
def unassign_team(request, project_pk):
    proj = Project.objects.get(pk=project_pk)
    if proj.lecturer.user == request.user:
        proj.team_assigned = None
        proj.save()
        messages.success(request, _(
            "You have successfully unassigned team from project: ") + str(proj))
    return redirect(reverse_lazy('lecturers:project',
                                 kwargs={'project_pk': proj.pk,
                                         'course_code': request.session['selectedCourse']}))

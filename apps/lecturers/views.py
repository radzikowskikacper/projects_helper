from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404

from projects_helper.apps.common.models import Project, Lecturer, Course
from projects_helper.apps.lecturers import is_lecturer
from projects_helper.apps.lecturers.forms import ProjectForm


@login_required
@user_passes_test(is_lecturer)
def profile(request):
    return render(request, "lecturers/profile.html")




@login_required
@user_passes_test(is_lecturer)
def project_list(request):
    title = request.GET.get('title')
    lecturer = Lecturer.objects.get(user=request.user)
    course = Course.objects.get(name=request.session['selectedCourse'])
    projects = Project.objects.filter(lecturer=lecturer).filter(course=course)
    return render(request,
                  template_name="lecturers/project_list.html",
                  context={"projects": projects,
                           "lecturer": lecturer})

@login_required
@user_passes_test(is_lecturer)
def filtered_project_list(request):
    title = request.GET.get('title')
    lecturer = Lecturer.objects.get(user=request.user)
    course = Course.objects.get(name=request.session['selectedCourse'])
    projects = Project.objects.filter(lecturer=lecturer).filter(course=course)

    filtered_projects = projects.filter(
        title__contains=title
    )
    return render(request,
                  template_name="lecturers/project_list.html",
                  context={"projects": filtered_projects,
                           "lecturer": lecturer})


@login_required
@user_passes_test(is_lecturer)
def project(request, project_pk):
    proj = Project.objects.get(pk=project_pk)
    return render(request, "lecturers/project_detail.html",
                  context={'project': proj,
                           'lecturer': Lecturer.objects.get(user=request.user)})


@login_required
@user_passes_test(is_lecturer)
def project_delete(request):
    projects_to_delete = Project.objects.filter(pk__in=request.POST.getlist('to_delete'))

    for proj in projects_to_delete:
        if proj.lecturer.user == request.user:
            if proj.status() == 'free':
                proj.delete()
            else:
                messages.error(request, "Cannot delete occupied project: " + proj.title)
        else:
            messages.error(request, "Cannot delete project: " + proj.title + " - access denied")
    return redirect(reverse('lecturers:project_list'))


@login_required
@user_passes_test(is_lecturer)
def project_new(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
    else:
        form = ProjectForm()
    if form.is_valid():
        try:
            proj = form.save(commit=False)
            proj.lecturer = Lecturer.objects.get(user=request.user)
            proj.course = Course.objects.get(name=request.session['selectedCourse'])
            proj.save()
        except IntegrityError as error:
            messages.error(request, "\n You must provide unique project name")
            return render(request, "lecturers/project_new.html",
                          context={'form': form})

        messages.info(request, "You have succesfully added new project: " + proj.title)
        return redirect(reverse('lecturers:project_list'))
    return render(request, "lecturers/project_new.html",
                  context={'form': form})


@login_required
@user_passes_test(is_lecturer)
def assign_team(request, project_pk):
    proj = Project.objects.get(pk=project_pk)
    if proj.lecturer.user == request.user:
        if proj.teams_with_preference().count() == 0:
            messages.error(request, "Cannot assign: No teams waiting for project")
        else:
            proj.assign_random_team()
    else:
        messages.error(request, "Cannot assign: access denied")

    return redirect(reverse_lazy('lecturers:project', kwargs={'project_pk': proj.pk}))


@login_required
@user_passes_test(is_lecturer)
def modify_project(request, project_pk):
    proj = get_object_or_404(Project, pk=project_pk)
    form = ProjectForm(request.POST or None, instance=proj)
    if form.is_valid():
        if proj.lecturer == Lecturer.objects.get(user = request.user):
            form.save()
            messages.info(request, "You have successfully updated project:" + proj.title)
        else:
            messages.error(request, "Access denied")
        return redirect(reverse("lecturers:modify_project", kwargs={'project_pk': proj.pk}))
    return render(request, "lecturers/project_modify.html",
                  context={'form': form,
                           'project': proj})
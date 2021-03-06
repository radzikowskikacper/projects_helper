from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.urls import reverse
from projects_helper.apps.students.views import is_student
from projects_helper.apps.lecturers.views import is_lecturer
from projects_helper.apps.courses.models import Course
import logging


## Instantiating module's logger.
logger = logging.getLogger('projects_helper.apps.about.views')


@ensure_csrf_cookie
def info(request):
    context = {
        "basetemplate": "users/base.html",
        "selectedCourse": None
    }

    # set proper base template (student's/lecturer's) containing
    # label of selected course only if user already logged in
    # AND chose any course from list
    if request.user.is_authenticated() and ('selectedCourse' in request.session):
        if is_student(request.user):
            context["basetemplate"] = "students/base.html"
        elif is_lecturer(request.user):
            context["basetemplate"] = "lecturers/base.html"

        course = get_object_or_404(
            Course, code__iexact=request.session['selectedCourse'])
        context["selectedCourse"] = course

    return render(request, 'about.html', context=context)

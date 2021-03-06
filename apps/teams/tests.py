from django.test import TestCase

# def create_student(name):
#     custom_user = CustomUser.objects.create(username=name)
#     return Student.objects.create(user=custom_user)
#
# 
# class TeamTest(TestCase):
#
#     def setUp(self):
#         custom_user = CustomUser.objects.create(username="Wiktor")
#         self.lecturer = Lecturer.objects.create(user=custom_user)
#         self.course = Course.objects.create(name="kurs")
#         self.project = Project.objects.create(lecturer=self.lecturer, course=self.course)
#
#     def test_str(self):
#         team1 = Team.objects.create(course=self.course)
#         team1.student_set.add(create_student("Stasiek"))
#         team1.student_set.add(create_student("Kazik"))
#
#         team2 = Team.objects.create(course=self.course)
#         team2.student_set.add(create_student("Zbyszek"))
#
#         self.assertEqual(str(team2), "Zbyszek")
#         self.assertEqual(str(team1), "Kazik, Stasiek")
#
#     def test_select_preference(self):
#         team = Team.objects.create(course=self.course)
#         team.select_preference(self.project)
#         self.assertEqual(team.project_preference, self.project)
#
#     def test_set_course(self):
#         team = Team.objects.create()
#         self.assertEqual(team.course, None)
#         team.set_course(self.course)
#         self.assertEqual(team.course, self.course)
#
#     def test_project_assigned(self):
#         team = Team.objects.create(course=self.course)
#         self.assertEqual(team.project_assigned, None)
#         project = Project.objects.create(lecturer=self.lecturer, title="Project", course=self.course)
#         project.team_assigned = team
#         project.save()
#         self.assertEqual(team.project_assigned, project)
#
#     def test_is_full(self):
#         team = Team.objects.create(course=self.course)
#         team.student_set.add(create_student("Stasiek"))
#         self.assertFalse(team.is_full)
#         team.student_set.add(create_student("Kazik"))
#         self.assertTrue(team.is_full)
#
#     def test_is_locked(self):
#         team = Team.objects.create(course=self.course)
#         project = Project.objects.create(lecturer=self.lecturer, title="Project", course=self.course)
#         project.team_assigned = team
#         project.save()
#         self.assertTrue(team.is_locked)
#
#     def test_remove_empty(self):
#         team1 = Team.objects.create()
#         team2 = Team.objects.create()
#         Team.remove_empty()
#         teams_count_after = Team.objects.all().count()
#         self.assertEqual(teams_count_after, 0)

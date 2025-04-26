from decimal import Decimal
from django.conf import settings
from django.db import models
from django.urls import reverse

from accounts.models import Student
from core.models import Semester
from course.models import Course

# Grade Definitions
A_PLUS = "A+"
A = "A"
A_MINUS = "A-"
B_PLUS = "B+"
B = "B"
B_MINUS = "B-"
C_PLUS = "C+"
C = "C"
C_MINUS = "C-"
D = "D"
F = "F"
NG = "NG"

GRADE_CHOICES = (
    (A_PLUS, "A+"),
    (A, "A"),
    (A_MINUS, "A-"),
    (B_PLUS, "B+"),
    (B, "B"),
    (B_MINUS, "B-"),
    (C_PLUS, "C+"),
    (C, "C"),
    (C_MINUS, "C-"),
    (D, "D"),
    (F, "F"),
    (NG, "NG"),
)

PASS = "PASS"
FAIL = "FAIL"

COMMENT_CHOICES = (
    (PASS, "PASS"),
    (FAIL, "FAIL"),
)

GRADE_BOUNDARIES = [
    (96, A_PLUS),
    (94, A),
    (91, A_MINUS),
    (88, B_PLUS),
    (85, B),
    (83, B_MINUS),
    (80, C_PLUS),
    (78, C),
    (75, C_MINUS),
    (0, F),  # anything below 75 is F
]


GRADE_POINT_MAPPING = {
    A_PLUS: 1.00,     # 96–100
    A: 1.25,          # 94–95
    A_MINUS: 1.50,    # 91–93
    B_PLUS: 1.75,     # 88–90
    B: 2.00,          # 85–87
    B_MINUS: 2.25,    # 83–84
    C_PLUS: 2.50,     # 80–82
    C: 2.75,          # 78–79
    C_MINUS: 3.00,    # 75–77
    F: 5.00,          # 74 and below
    NG: 5.00,         # No Grade
}



class TakenCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="taken_courses")

    assignment = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    mid_exam = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    quiz = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    attendance = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    final_exam = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    project = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"), editable=True)
    total = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"), editable=False)
    grade = models.CharField(choices=GRADE_CHOICES, max_length=2, blank=True, editable=False)
    point = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"), editable=False)
    comment = models.CharField(choices=COMMENT_CHOICES, max_length=200, blank=True, editable=False)

    def __str__(self):
        return f"{self.course.title} ({self.course.code})"

    def get_absolute_url(self):
        return reverse("course_detail", kwargs={"slug": self.course.slug})

    def get_total(self):
        return (
            Decimal(self.assignment) * Decimal("0.10") +
            Decimal(self.quiz) * Decimal("0.20") +
            Decimal(self.mid_exam) * Decimal("0.10") +
            Decimal(self.attendance) * Decimal("0.10") +
             Decimal(self.project) * Decimal("0.20") +
            Decimal(self.final_exam) * Decimal("0.30")
        )

    def get_grade(self):
        total = self.total
        for boundary, grade in GRADE_BOUNDARIES:
            if total >= boundary:
                return grade
        return NG

    def get_comment(self):
        if self.total <= 74.90:
            return FAIL
        return PASS

    def get_point(self):
        credit = self.course.credit
        grade_point = GRADE_POINT_MAPPING.get(self.grade, 0.0)
        return Decimal(credit) * Decimal(grade_point)

    def save(self, *args, **kwargs):
        self.total = self.get_total()
        self.grade = self.get_grade()
        self.point = self.get_point()
        self.comment = self.get_comment()
        super().save(*args, **kwargs)

    def calculate_gpa(self):
        current_semester = Semester.objects.filter(is_current_semester=True).first()
        if not current_semester:
            return Decimal("0.00")

        taken_courses = TakenCourse.objects.filter(
            student=self.student,
            course__level=self.student.level,
            course__semester=current_semester.semester,
        )

        total_points = sum(tc.point for tc in taken_courses)
        total_credits = sum(tc.course.credit for tc in taken_courses)

        if total_credits > 0:
            gpa = total_points / Decimal(total_credits)
            return round(gpa, 2)
        return Decimal("0.00")

    def calculate_cgpa(self):
        taken_courses = TakenCourse.objects.filter(student=self.student)

        total_points = sum(tc.point for tc in taken_courses)
        total_credits = sum(tc.course.credit for tc in taken_courses)

        if total_credits > 0:
            cgpa = total_points / Decimal(total_credits)
            return round(cgpa, 2)
        return Decimal("0.00")


class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    gpa = models.FloatField(null=True)
    cgpa = models.FloatField(null=True)
    semester = models.CharField(max_length=100, choices=settings.SEMESTER_CHOICES)
    session = models.CharField(max_length=100, blank=True, null=True)
    level = models.CharField(max_length=25, choices=settings.LEVEL_CHOICES, null=True)

    def __str__(self):
        return f"Result for {self.student} - Semester: {self.semester}, Level: {self.level}"

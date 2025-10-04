from django.shortcuts import render
from .models import Student

class StudentNotFoundMiddleware:
    """
    Middleware to catch Student.DoesNotExist and show a custom page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Student.DoesNotExist:
            return render(request, 'student_not_found.html')
        return response

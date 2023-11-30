from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'index.html')

def process_form(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        # Now you can run your Python script with the 'username' variable

        # For example, print the username:
        print(f"Received username: {username}")

        # Add your Python script execution logic here

        return render(request, 'result.html', {'username': username})

    # Handle GET requests or other cases
    return HttpResponse("Invalid request method")

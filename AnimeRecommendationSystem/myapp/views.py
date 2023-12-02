from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

def index(request):
    template = loader.get_template("myapp/index.html")
    context = {"testing":"hello"}
    return HttpResponse(template.render(context, request))

def process_form(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        # Now you can run your Python script with the 'username' variable

        # For example, print the username:
        # print(f"Received username: {username}")

        template = loader.get_template("myapp/result.html")
        # Add your Python script execution logic here
        context = {"username":username}
        return HttpResponse(template.render(context, request))

    # Handle GET requests or other cases
    return HttpResponse("Invalid request method")

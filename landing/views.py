from django.shortcuts import redirect, render

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('/')

    return render(request, 'landing/landing_page.html')

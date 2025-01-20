from django.shortcuts import redirect, render

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('blog:home')

    return render(request, 'landing/landing_page.html')

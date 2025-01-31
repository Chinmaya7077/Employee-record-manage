from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from rest_framework import viewsets
from .models import Technology, task
from .serializers import taskSerializer
from .forms import TaskForm
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
import re
from django.utils import timezone

class taskViewSet(viewsets.ModelViewSet):
    queryset = task.objects.all()
    serializer_class = taskSerializer


def index(request):
    # Get filter parameters
    per_page = request.GET.get('per_page', 10)
    search_query = request.GET.get('search', '').strip()
    selected_technologies = request.GET.getlist('technology')
    page_number = request.GET.get('page', 1)

    # Start with all tasks
    tasks_list = task.objects.all().order_by('-updated_at')

    # Apply technology filter if selected
    selected_technologies = [tech for tech in selected_technologies if tech.isdigit()]
    if selected_technologies:
        tasks_list = tasks_list.filter(technology__id__in=selected_technologies).distinct()


    if search_query:
        # Split the search query into words
        query_words = search_query.split()
        
        # Create a Q object for the search conditions
        search_query_q = Q()
        
        # Add individual name searches
        search_query_q |= Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query) | Q(mail_id__icontains=search_query)   
        
        if len(query_words) > 1:
            # Combine adjacent words to search for full name
            for i in range(len(query_words) - 1):
                first = query_words[i]
                last = query_words[i + 1]
                search_query_q |= (Q(first_name__icontains=first) & Q(last_name__icontains=last))
        
        tasks_list = tasks_list.filter(search_query_q)

    # Paginate results
    paginator = Paginator(tasks_list, per_page)
    tasks = paginator.get_page(page_number)

    # Handle AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        task_data = []
        for task_item in tasks:
            task_data.append({
                'id': task_item.id,
                'first_name': f"{task_item.first_name} {task_item.last_name}",
                'mail_id': task_item.mail_id,
                'salary': float(task_item.salary),
                'technologies': ", ".join([t.name for t in task_item.technology.all()]),
            })

        return JsonResponse({
            'tasks': task_data,
            'found': bool(task_data),
            'page_number': tasks.number,
            'has_previous': tasks.has_previous(),
            'has_next': tasks.has_next(),
            'total_pages': paginator.num_pages,
        })

    # Get all technologies for the filter dropdown
    technologies = Technology.objects.all()

    # Prepare context
    context = {
        'tasks': tasks,
        'technologies': technologies,
        'selected_technologies': selected_technologies,
        'search_query': search_query,
        'per_page': int(per_page),
    }

    return render(request, 'taskapp/index.html', context)


def display_tasks(request):
    # tasks = task.objects.all()
    # return render(request, 'taskapp/display_all.html', {'task': tasks})
     # Get filter parameters
    per_page = request.GET.get('per_page', 10)
    search_query = request.GET.get('search', '').strip()
    page_number = request.GET.get('page', 1)

    # Start with all tasks
    tasks_list = task.objects.all().order_by('-updated_at')

    # Apply search if query exists
    if search_query:
        # Split the search query into words
        query_words = search_query.split()
        
        # Create a Q object for the search conditions
        search_query_q = Q()
        
        # Add individual name and email searches
        search_query_q |= (
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) | 
            Q(mail_id__icontains=search_query)
        )
        
        # If there are multiple words, search for full name matches
        if len(query_words) > 1:
            for i in range(len(query_words) - 1):
                first = query_words[i]
                last = query_words[i + 1]
                search_query_q |= (Q(first_name__icontains=first) & Q(last_name__icontains=last))
        
        tasks_list = tasks_list.filter(search_query_q)

    # Paginate results
    paginator = Paginator(tasks_list, per_page)
    tasks = paginator.get_page(page_number)

    # Handle AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        task_data = []
        start_index = (tasks.number - 1) * int(per_page)
        
        for index, task_item in enumerate(tasks):
            task_data.append({
                'index': start_index + index + 1,
                'name': f"{task_item.first_name} {task_item.last_name}",
                'mail_id': task_item.mail_id,
                'technologies': ", ".join([t.name for t in task_item.technology.all()]),
                'salary': float(task_item.salary),
            })

        return JsonResponse({
            'tasks': task_data,
            'found': bool(task_data),
            'page_number': tasks.number,
            'has_previous': tasks.has_previous(),
            'has_next': tasks.has_next(),
            'total_pages': paginator.num_pages,
        })

    context = {
        'tasks': tasks,
        'search_query': search_query,
        'per_page': int(per_page),
    }

    return render(request, 'taskapp/display_all.html', context)




def search_view(request):
    query = request.GET.get('search', '').strip()
    selected_technologies = request.GET.getlist('technology')
    page_number = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 10))

    # Start with all tasks
    tasks = task.objects.all()

    # Apply search filter if query exists
    if query:
        # Split the search query into words
        query_words = query.split()
        
        # Create a Q object for the search conditions
        search_query = Q()
        
        # Add individual name searches
        search_query |= Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(mail_id__icontains=query)
        
        # If there are multiple words, search for full name matches
        if len(query_words) > 1:
            # Combine adjacent words to search for full name
            for i in range(len(query_words) - 1):
                first = query_words[i]
                last = query_words[i + 1]
                search_query |= (Q(first_name__icontains=first) & Q(last_name__icontains=last))
        
        tasks = tasks.filter(search_query)

    # Apply technology filter
    if selected_technologies:
        tasks = tasks.filter(technology__id__in=selected_technologies)

    # Ensure distinct results and proper ordering
    tasks = tasks.distinct().order_by('-updated_at')

    # Paginate results
    paginator = Paginator(tasks, per_page)
    page_obj = paginator.get_page(page_number)

    # Prepare task list with proper indexing
    task_list = []
    start_index = (page_obj.number - 1) * per_page + 1
    
    for index, t in enumerate(page_obj):
        task_list.append({
            'index': start_index + index,
            'id': t.id,
            'first_name': f"{t.first_name} {t.last_name}",
            'mail_id': t.mail_id,
            'salary': str(t.salary),
            'technologies': ', '.join([tech.name for tech in t.technology.all()]),
        })

    return JsonResponse({
        'tasks': task_list,
        'found': bool(task_list),
        'page_number': page_obj.number,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'total_pages': paginator.num_pages,
        'current_search': query,
        'current_technologies': selected_technologies,
    })
def add_records(request):
    technologies = Technology.objects.all()

    if request.method == 'POST':
        # Fetch and process form data
        first_name = request.POST['first_name'].strip()
        last_name = request.POST['last_name'].strip()
        mail_id = request.POST['mail_id'].strip()
        salary = float(request.POST['salary'].strip())
        selected_technologies = request.POST.getlist('technologies')

        errors = {}

        # Validation checks
        if not first_name:
            errors['first_name'] = "First name is required."
        elif len(first_name) < 3:
            errors['first_name'] = "First name must be at least 3 characters long."
        elif len(first_name) > 15:
            errors['first_name'] = "First name must be at most 15 characters long."
            
        elif not re.match(r'^[^\d\s][^\d]*$', first_name):
            errors['first_name'] = "First name must not contain numbers or start with a space."


        elif '  ' in first_name:  # Check for consecutive spaces
            errors['first_name'] = "First name must not contain consecutive spaces."
        
      
            
        if not last_name:
            errors['last_name'] = "Last name is required."
        elif len(last_name) < 3:
            errors['last_name'] = "Last name must be at least 3 characters long."  
        elif len(last_name) > 15:
            errors['last_name'] = "Last name must be at most 15 characters long."
            
        elif not re.match(r'^[^\d\s][^\d]*$', last_name):
            errors['last_name'] = "First name must not contain numbers or start with a space."
 
        
        elif '  ' in last_name:  # Check for consecutive spaces
            errors['last_name'] = "last name must not contain consecutive spaces."
            
        if not mail_id:
            errors['mail_id'] = "Email is required."
        elif '@' not in mail_id:
            errors['mail_id'] = "Email must have '@'."
        else:
            # Check if the email is already in use
            if task.objects.filter(mail_id=mail_id).exists():
                errors['mail_id'] = "This email is already in use. Please use a different email."

            
        if not salary:
            errors['salary'] = "Salary is required."
       
        elif salary>9999999:
            errors['salary'] = "Salary must be less than 9999999."
        elif salary<=0:
            errors['salary'] = "Salary must be a positive number or greater then 0."
        else:
            try:
                salary = float(salary)
                if salary <= 0:
                    errors['salary'] = "Salary must be a positive number."
            except ValueError:
                errors['salary'] = "Salary must be a valid number."
        if not selected_technologies:
            errors['technologies'] = "At least one technology must be selected."

        # Handle errors
        if errors:
            return render(request, 'taskapp/add.html', {
                'technologies': technologies,
                'form_data': {
                    'first_name': first_name,
                    'last_name': last_name,
                    'mail_id': mail_id,
                    'salary': salary,
                    'selected_technologies': selected_technologies
                },
                'errors': errors,  # Pass errors to the template
            })

        # Create the task
        task_instance = task.objects.create(
            first_name=first_name,
            last_name=last_name,
            mail_id=mail_id,
            salary=salary
        )
        tech_objects = Technology.objects.filter(id__in=selected_technologies)
        task_instance.technology.add(*tech_objects)

        messages.success(request, "Employee added successfully!")
        return redirect('index')

    return render(request, 'taskapp/add.html', {'technologies': technologies})



from django.urls import reverse
def remove_records(request, task_id):
    records = get_object_or_404(task, id=task_id)

    if request.method == "POST":
        records.delete()
        messages.success(request, "Employee record removed successfully!")
        return redirect(reverse('index'))  # Ensuring correct URL resolution

    return render(request, 'taskapp/remove.html', {'task': records})


def update_records(request, task_id):
    # Get the task instance that we need to update
    task_instance = get_object_or_404(task, id=task_id)
    technologies = Technology.objects.all()

    if request.method == 'POST':
        # Fetch and process form data
        first_name = request.POST['first_name'].strip()
        last_name = request.POST['last_name'].strip()
        mail_id = request.POST['mail_id'].strip()
        salary = float(request.POST['salary'].strip())
        selected_technologies = request.POST.getlist('technologies')  # Get selected technologies from the form

        errors = {}

        # Validation checks
        if not first_name:
            errors['first_name'] = "First name is required."
        elif len(first_name) < 3:
            errors['first_name'] = "First name must be at least 3 characters long."
        elif len(first_name) > 15:
            errors['first_name'] = "First name must be at most 15 characters long."
        elif not re.match(r'^[^\d\s][^\d]*$', first_name):
            errors['first_name'] = "First name must not contain numbers or start with a space."

        elif '  ' in first_name:  # Check for consecutive spaces
            errors['first_name'] = "First name must not contain consecutive spaces."

        if not last_name:
            errors['last_name'] = "Last name is required."
        elif len(last_name) < 3:
            errors['last_name'] = "Last name must be at least 3 characters long."
        elif len(last_name) > 15:
            errors['last_name'] = "Last name must be at most 15 characters long."
        elif not re.match(r'^[^\d\s][^\d]*$', last_name):
            errors['last_name'] = "First name must not contain numbers or start with a space."

            
            
        elif '  ' in last_name:  # Check for consecutive spaces
            errors['last_name'] = "Last name must not contain consecutive spaces."

        if not salary:
            errors['salary'] = "Salary is required."

        elif salary>9999999:
            errors['salary'] = "Salary must be less than 9999999."
            
        elif salary<=0:
            errors['salary'] = "Salary must be a positive number or greater then 0."
        else:
            try:
                salary = float(salary)
                if salary <= 0:
                    errors['salary'] = "Salary must be a positive number."
            except ValueError:
                errors['salary'] = "Salary must be a valid number."

        if not selected_technologies:
            errors['technologies'] = "At least one technology must be selected."

        # Handle errors
        if errors:
            # Re-render the form with the selected technologies and errors
            return render(request, 'taskapp/update.html', {
                'task_instance': task_instance,
                'technologies': technologies,
                'selected_technologies': [int(tech) for tech in selected_technologies],  # Pass selected technologies back
                'errors': errors,
            })

        # Update the task
        task_instance.first_name = first_name
        task_instance.last_name = last_name
        task_instance.mail_id = mail_id
        task_instance.salary = salary

        # Update technologies
        tech_objects = Technology.objects.filter(id__in=selected_technologies)
        task_instance.technology.set(tech_objects)  # Set the new technologies

        task_instance.save()

        messages.success(request, "Employee updated successfully!")
        return redirect('index')

    else:
        # For GET request, populate the form with the current employee details
        selected_technologies = task_instance.technology.values_list('id', flat=True)  # Get IDs of assigned technologies

    return render(request, 'taskapp/update.html', {
        'task_instance': task_instance,
        'technologies': technologies,
        'selected_technologies': selected_technologies,  # Pass selected technologies to the template
    })



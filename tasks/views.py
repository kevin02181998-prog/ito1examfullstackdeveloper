from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task
from .forms import RegisterForm, TaskForm, TaskStatusForm, AdminTaskForm


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


@login_required
def dashboard_view(request):
    if request.user.is_staff:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(assigned_to=request.user)

    pending = tasks.filter(status='pending').count()
    in_progress = tasks.filter(status='in_progress').count()
    done = tasks.filter(status='done').count()

    context = {
        'tasks': tasks,
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
    }
    return render(request, 'dashboard.html', context)


@login_required
def create_task_view(request):
    if request.method == 'POST':
        if request.user.is_staff:
            form = AdminTaskForm(request.POST)
        else:
            form = TaskForm(request.POST)

        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            if not request.user.is_staff:
                task.assigned_to = request.user
            task.save()
            messages.success(request, 'Task created!')
            return redirect('dashboard')
    else:
        if request.user.is_staff:
            form = AdminTaskForm()
        else:
            form = TaskForm()

    return render(request, 'create_task.html', {'form': form})


@login_required
def update_task_view(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if not request.user.is_staff and task.assigned_to != request.user:
        messages.error(request, 'You cannot edit this task.')
        return redirect('dashboard')

    if request.method == 'POST':
        if request.user.is_staff:
            form = AdminTaskForm(request.POST, instance=task)
        else:
            form = TaskStatusForm(request.POST, instance=task)

        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated!')
            return redirect('dashboard')
    else:
        if request.user.is_staff:
            form = AdminTaskForm(instance=task)
        else:
            form = TaskStatusForm(instance=task)

    return render(request, 'update_task.html', {'form': form, 'task': task})


@login_required
def delete_task_view(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if not request.user.is_staff and task.created_by != request.user:
        messages.error(request, 'You cannot delete this task.')
        return redirect('dashboard')

    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted!')
        return redirect('dashboard')

    return render(request, 'delete_task.html', {'task': task})

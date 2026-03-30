from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
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


def reset_password_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        else:
            try:
                user = User.objects.get(username=username)
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password reset successful! You can now login.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'Username not found.')

    return render(request, 'reset_password.html')


@login_required
def dashboard_view(request):
    if request.user.is_staff:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(assigned_to=request.user)

    status_filter = request.GET.get('status', '')
    if status_filter in ['pending', 'in_progress', 'done']:
        filtered_tasks = tasks.filter(status=status_filter)
    else:
        filtered_tasks = tasks

    pending = tasks.filter(status='pending').count()
    in_progress = tasks.filter(status='in_progress').count()
    done = tasks.filter(status='done').count()
    total = tasks.count()

    context = {
        'tasks': filtered_tasks,
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'total': total,
        'current_filter': status_filter,
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

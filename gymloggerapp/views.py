from django.shortcuts import render
from django.forms import modelformset_factory, inlineformset_factory
from .models import SetLogger, ExerciseName, MuscleGroup
from .forms import ExerciseForeignKeyForm, DeleteAccountForm, UpdateProfile, ExerciseNameForm, MuscleGroupForm, MuscleDropDownForm, GraphDropDownForm, SetCardsTimeframeForm, SignUpForm
from django.http import JsonResponse
import datetime
from datetime import datetime, timedelta
from django.shortcuts import redirect
from django import forms
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

#Authentication views.
def signup(request):

    user_emails = []
    for each_user in User.objects.all():
        user_emails.append(str(each_user.email))

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            if str(form.cleaned_data.get('email')) in user_emails:
                return redirect('signup')
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('name_list')
    else:
        form = SignUpForm()
    return render(request, 'gymloggerapp/signup.html', {'form': form})

#Account settings views.
def user_settings_edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user_emails = []
    for each_user in User.objects.all():
        user_emails.append(str(each_user.email))

    username = request.user.username

    form = UpdateProfile(instance=request.user)

    if request.method == 'POST':
        form = UpdateProfile(request.POST, instance=request.user)
        if form.is_valid():
           if str(form.cleaned_data.get('email')) in user_emails:
             if str(form.cleaned_data.get('email')) != str(request.user.email):
               return redirect('user_settings_edit_profile')
           form.save()
           return redirect('name_list')


    return render(request, 'gymloggerapp/user_settings_edit_profile.html', { 'username': username, 'form': form})

def user_settings_change_password(request):
    if not request.user.is_authenticated:
        return redirect('login')

    form = PasswordChangeForm(request.user)

    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('name_list')

    username = request.user.username

    return render(request, 'gymloggerapp/user_settings_change_password.html', { 'username': username, 'form': form})


def user_settings_delete_account(request):
    if not request.user.is_authenticated:
        return redirect('login')
    username = request.user.username

    form = DeleteAccountForm()

    if request.method == "POST":
        form = DeleteAccountForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=username)
            user.is_active = False
            user.save()
            return redirect('login')

    return render(request, 'gymloggerapp/user_settings_delete_account.html', { 'username': username, 'form': form})


#Auxiliary functions for post-authentication app views.
def sets_from_last_21_entry_dates(user_id):
    '''
    #This function returns the queryset of all sets logged by the
    #user in the last 21 ACTIVE days (a day where at least 1 set
    #has been logged).
    #The queryset is in decreasing order. 
    '''
    sets = SetLogger.objects.filter(user=user_id)
    date_list = []
    reverse_date_list = reversed(date_list)
    object_counter = 0
    date_change_counter = 0

    for set_object in sets:
        date_list.append(set_object.date)

    for date in reverse_date_list:
        object_counter += 1
        date_index = reverse_date_list.index(date)
        if date_index > 0 and date != reverse_date_list[date_index - 1]:
           date_change_counter += 1 
        if date_change_counter == 21:
            return object_counter - 1

def exercises_without_recent_sets(user_id):
    '''
    This function returns a list of all ExerciseName objects
    which do not have sets logged in the last 21 active days.
    '''
    sets = SetLogger.objects.filter(user=user_id).order_by('-id')[:sets_from_last_21_entry_dates(user_id)]
    exercises = ExerciseName.objects.filter(user=user_id)
    set_exercises = []
    exercises_no_recent_sets = []

    for set_object in sets: 
        set_exercises.append(set_object.exercisegroup.name_of_exercise)

    for exercise in exercises:
        if exercise.name_of_exercise not in set_exercises:
            exercises_no_recent_sets.append(exercise.name_of_exercise)

    return exercises_no_recent_sets


# All post-authentication views for gymlogger.
def name_list(request):
    '''
    This view is the homepage view. It primarily displays exercises and their associated 
    recent sets, and allows adding and editing of exercises and muscle groups.
    '''

    if not request.user.is_authenticated:
        return redirect('login')
    
    username = request.user.username
    number_of_exercises = 0
    muscle_choice='All'
    exercise_muscle_groups = []
    form = ExerciseNameForm(user_id=request.user)
    form2 = MuscleGroupForm()
    form3 = MuscleDropDownForm(user_id=request.user)
    exercises_no_recent_sets = exercises_without_recent_sets(request.user)
    muscles = MuscleGroup.objects.filter(user=request.user)

    exercise_name = ExerciseName.objects.filter(user=request.user).order_by('muscle_group')
    sets = SetLogger.objects.filter(user=request.user).order_by('-date')[:sets_from_last_21_entry_dates(request.user)]
    
    MuscleGroupFormSet = modelformset_factory(MuscleGroup, fields=('muscle', 'delete_true',), extra=0, widgets={
        'muscle': forms.TextInput(attrs={'class': 'muscle-form'}), 
        'delete_true': forms.CheckboxInput(attrs={ 'class': 'delete' })
        }, labels={'delete_true': ''})
    formset = MuscleGroupFormSet(queryset=muscles)

    ExerciseFormSet = modelformset_factory(ExerciseName, form=ExerciseForeignKeyForm, extra=0)
    formset2 = ExerciseFormSet(form_kwargs={'user_id': request.user}, queryset=exercise_name)

    for exercise in exercise_name:
        number_of_exercises += 1
        exercise_muscle_groups.append(str(exercise.muscle_group))
    
    muscle_edit_button = True
    if muscles.count() == 0:
        muscle_edit_button = False

    exercise_edit_button = True
    if exercise_name.count() == 0:
        exercise_edit_button = False

    if request.method == 'GET':
      form3 = MuscleDropDownForm(request.GET, user_id=request.user)
      if form3.is_valid():
        muscle_choice = form3.cleaned_data.get('muscle_choice')

    if request.method == 'POST':
      form = ExerciseNameForm(request.POST, user_id=request.user)
      if form.is_valid():
         added_exercise = form.save(commit=False)
         added_exercise.user = request.user
         added_exercise.save()
         exercise_name = ExerciseName.objects.filter(user=request.user).order_by('muscle_group')
         return redirect('name_list')
      else:
         form = ExerciseNameForm(user_id=request.user)
         
      form2 = MuscleGroupForm(request.POST)
      if form2.is_valid():
         added_muscle = form2.save(commit=False)
         added_muscle.user = request.user
         added_muscle.save()
         formset = MuscleGroupFormSet(queryset=muscles)
         return redirect('name_list')
      else:
         form2 = MuscleGroupForm()

      formset = MuscleGroupFormSet(request.POST, queryset=muscles)
      if formset.is_valid():
         formset.save()
         for obj in muscles:
            if obj.delete_true == True:
               obj.delete()
         exercise_name = ExerciseName.objects.filter(user=request.user).order_by('muscle_group')
         sets = SetLogger.objects.filter(user=request.user).order_by('-date')[:sets_from_last_21_entry_dates(user_id=request.user)]
         muscles = MuscleGroup.objects.filter(user=request.user)
         MuscleGroupFormSet = modelformset_factory(MuscleGroup, fields=('muscle', 'delete_true',), extra=0)
         formset = MuscleGroupFormSet(queryset=muscles)
         return redirect('name_list')
       
      formset2 = ExerciseFormSet(request.POST, form_kwargs={'user_id': request.user}, queryset=exercise_name)
      if formset2.is_valid():
         formset2.save()
         for ex in exercise_name:
            if ex.delete_true == True:
               ex.delete()
         exercise_name = ExerciseName.objects.filter(user=request.user).order_by('muscle_group')
         sets = SetLogger.objects.filter(user=request.user).order_by('-date')[:sets_from_last_21_entry_dates(user_id=request.user)]
         muscles = MuscleGroup.objects.filter(user=request.user)
         ExerciseFormSet = modelformset_factory(ExerciseName, form=ExerciseForeignKeyForm, extra=0)
         formset2 = ExerciseFormSet(form_kwargs={'user_id': request.user}, queryset=exercise_name)
         return redirect('name_list')
         
    return render(request, 'gymloggerapp/name_list.html', { 'username': username, 'muscle_edit_button': muscle_edit_button, 'exercise_edit_button': exercise_edit_button, 'exercise_formset': formset2, 'muscle_formset': formset, 'number_of_exercises': number_of_exercises, 'exercise_muscle_groups': exercise_muscle_groups, 'muscle_choice': str(muscle_choice), 'form3': form3, 'exercises_no_recent_sets': exercises_no_recent_sets, 'exercise_name': exercise_name, 'form': form, 'form2': form2, 'sets': sets})

def set_forms(request, exercisegroup_id):
    '''
    This view displays addding and displaying of sets related to an exercise.
    '''

    if not request.user.is_authenticated:
        return redirect('login')

    username = request.user.username

    exercisename = ExerciseName.objects.get(pk=exercisegroup_id)
    SetLoggerFormSet = inlineformset_factory(ExerciseName, SetLogger, fields=('weight','reps', 'date',), extra=1, can_delete=False, widgets={
    'date': forms.SelectDateWidget(empty_label="Nothing", attrs={ 'class': 'date'}), 'weight': forms.TextInput(attrs={ 'class': 'weight', 'autocomplete':'off'}), 
    'reps': forms.TextInput(attrs={ 'class': 'reps', 'autocomplete':'off'})})

    form = SetCardsTimeframeForm(user_id=request.user)
    formset = SetLoggerFormSet()
    
    month = 'All months'
    year = 'All years'
    
    form_dates = []
    date_created = datetime.now().date

    if request.method == 'POST':  

      formset = SetLoggerFormSet(request.POST, instance=exercisename)
      if formset.is_valid():
        for form in formset: 
            form_dates.append(form.cleaned_data.get('date'))
            added_set = form.save(commit=False)
            added_set.user = request.user
            added_set.save()
            
        date_created = form_dates[-1]  
        
        return redirect('set_forms', exercisegroup_id=exercisegroup_id)

      else:
        formset = SetLoggerFormSet()

    if request.method == 'GET':
      form = SetCardsTimeframeForm(request.GET, user_id=request.user)
      if form.is_valid():
        month = form.cleaned_data.get('month')
        year = form.cleaned_data.get('year')
        date_created = datetime.now().date

  
    formset = SetLoggerFormSet()

    sets = SetLogger.objects.filter(exercisegroup=exercisename).order_by('date')
    set_list = []
    for each_set in sets:
        set_list.append(each_set)

    if len(set_list) == 0:
        no_set_message = 'No sets recorded.'
    else:
        no_set_message = ''

    #Getting date of each different workout.
    
    dates = []
    i = 0
    for set_instance in set_list:
        if i == 0: 
            dates.append(set_instance.date)
        elif i > 0:
            if set_instance.date != set_list[i-1].date:
                dates.append(set_instance.date)
        i += 1

    #Grouping sets together by date. 
    all_set_groups = []
    instances_per_group = []
    for date in dates:
        for set_instance in set_list:
            if set_instance.date == date:
                instances_per_group.append(set_instance)
        all_set_groups.append((date.strftime("%B %Y"), date, instances_per_group))
        instances_per_group = []


    return render(request, 'gymloggerapp/set_forms.html', { 'username': username, 'no_set_message': no_set_message,'date_created': date_created, 'year': year, 'month': month, 'form': form, 'all_set_groups': all_set_groups, 'sets': sets, 'formset': formset, 'exercisename': exercisename})

def edit_sets(request, exercisegroup_id, setgroup_id):
    '''
    This view allows editing of a group of sets from the same day, which
    are related to the same exercise. 
    '''

    if not request.user.is_authenticated:
        return redirect('login')

    exercisename = ExerciseName.objects.get(pk=exercisegroup_id)
    sets = SetLogger.objects.filter(exercisegroup=exercisename).order_by('date')
    edit_date = datetime.strptime(setgroup_id,"%Y-%m-%d").date()

    SetsFormSet = inlineformset_factory(ExerciseName, SetLogger, fields=('weight','reps', 'delete_true'), can_delete=True, extra=0, 
          widgets = {
        'weight': forms.TextInput(attrs={ 'class': 'weight', 'autocomplete':'off'}),
        'reps': forms.TextInput(attrs={ 'class': 'reps', 'autocomplete':'off'}),
        'delete_true': forms.CheckboxInput(attrs={ 'class': 'delete' }) 
        })
        
    formset = SetsFormSet(instance=exercisename)

    set_list = []
    for each_set in sets:
        if each_set.date.strftime("%Y-%m-%d") == setgroup_id: 
            set_list.append(each_set)

    if request.method == 'POST':  
      formset = SetsFormSet(request.POST, instance=exercisename)
      for form in formset:
          if form.is_valid():
            form.save(commit=True)
          sets = SetLogger.objects.filter(exercisegroup=exercisename).order_by('date')
          for obj in sets:
               if obj.delete_true == True:
                  obj.delete()
      return redirect('set_forms', exercisegroup_id=exercisegroup_id)
         
       
    return render(request, 'gymloggerapp/edit_sets.html', { "exercisegroup_id": exercisegroup_id, "edit_date": edit_date, 'exercisename': exercisename, 'set_list': set_list, 'formset': formset, 'setgroup_id': setgroup_id })

# Global variable for SetLogger objects required for graph view and graph JsonResponses. 
global_sets_used = SetLogger.objects.all().order_by('date')

# Graph page main view.
def graph_page(request, exercisegroup_id):
    '''
    This view displays graphs for sets in a particular exercise over specific timeframes.
    '''

    if not request.user.is_authenticated:
        return redirect('login')

    username = request.user.username

    global global_sets_used

    exercisename = ExerciseName.objects.get(pk=exercisegroup_id)
    
    show_graph = True

    #Receiving and displaying forms data. 
    timeframe = 'All'
    graph = 'Highest recorded weight over time'

    time_threshold_1_month = datetime.now() - timedelta(days=30)
    time_threshold_3_months = datetime.now() - timedelta(days=90)
    time_threshold_6_months = datetime.now() - timedelta(days=180)
    time_threshold_1_year = datetime.now() - timedelta(days=365)

    if request.method == 'GET':
      form = GraphDropDownForm(request.GET)
      if form.is_valid():
        graph = form.cleaned_data.get('graph')
        timeframe = form.cleaned_data.get('timeframe')

        if timeframe == 'All':
            global_sets_used = SetLogger.objects.all().order_by('date')
        elif timeframe == '1 month':
            global_sets_used = SetLogger.objects.filter(date__gte=time_threshold_1_month).order_by('date')
        elif timeframe == '3 months':
            global_sets_used = SetLogger.objects.filter(date__gte=time_threshold_3_months).order_by('date')
        elif timeframe == '6 months':
            global_sets_used = SetLogger.objects.filter(date__gte=time_threshold_6_months).order_by('date')
        elif timeframe == '1 year':
            global_sets_used = SetLogger.objects.filter(date__gte=time_threshold_1_year).order_by('date')

    sets = global_sets_used.filter(exercisegroup=exercisename).order_by('date')
    set_list = []
    weight_pb_list = []
    volume_pb_list = []

    if sets.count() == 0:
        show_graph = False
        return render(request, 'gymloggerapp/graph_page.html', { 'username': username, 'show_graph': show_graph, 'timeframe': timeframe, 'graph': graph, 'form': GraphDropDownForm(request.GET),'exercisegroup_id': exercisegroup_id, 'exercisename': exercisename, 'sets': sets})

    #Calculating personal bests
    for each_set in sets:
        set_list.append(each_set)
        weight_pb_list.append(int(each_set.weight))
        volume_pb_list.append(int(each_set.weight) * int(each_set.reps))


    weight_pb = max(weight_pb_list)
    volume_pb = max(volume_pb_list)
    volume_pb_instance = []
    for every_set in set_list:
        if int(every_set.weight)*int(every_set.reps) == volume_pb:
           volume_pb_instance.append(every_set)
    volume_pb_detail = volume_pb_instance[-1]
                

    #Data to display max weight over time.
    i = 0
    check_weight_list = []
    highest_weight_list = []
    for set_instance in set_list:
        check_weight_list.append(set_instance.weight)
        if i == 0:
            highest_weight_list.append(set_list[0])
        elif max(check_weight_list) <= set_instance.weight:
            if highest_weight_list[-1].date != set_instance.date:
                highest_weight_list.append(set_instance)
            elif highest_weight_list[-1].date == set_instance.date:
                highest_weight_list.remove(highest_weight_list[-1])
                highest_weight_list.append(set_instance)
        i += 1

    #Data to display max volume over time.
    i = 0
    check_volume_list = []
    highest_volume_list = []
    for set_instance in set_list:
        check_volume_list.append(int(set_instance.weight)*int(set_instance.reps))
        if i == 0:
            highest_volume_list.append(set_list[0])
        elif max(check_volume_list) <= int(set_instance.weight)*int(set_instance.reps):
            if highest_volume_list[-1].date != set_instance.date:
                highest_volume_list.append(set_instance)
            elif highest_volume_list[-1].date == set_instance.date:
                highest_volume_list.remove(highest_volume_list[-1])
                highest_volume_list.append(set_instance)
        i += 1

    template_volume = []
    for template_object in highest_volume_list:
        template_volume.append((template_object.date, int(template_object.weight)*int(template_object.reps)))

    #Data to display max weight per workout over time. 
    same_date_set = []
    same_date_weight_set = []
    max_weight_objects = []
    single_max_weight_objects = []
    i = 0
    for instance in set_list:
        same_date_set.append(instance)
        if set_list[-1] == set_list[i] or set_list[i+1].date != instance.date:
            for same_date_instance in same_date_set:
                same_date_weight_set.append(int(same_date_instance.weight))
            for same_date_object in same_date_set:
                if int(same_date_object.weight) == max(same_date_weight_set):
                    max_weight_objects.append(same_date_object)
            single_max_weight_objects.append(max_weight_objects[0])
            same_date_set = []
            same_date_weight_set = []
            max_weight_objects = []
        i += 1

    #Data to display max volume per workout over time.
    same_date_set = []
    same_date_volume_set = []
    max_volume_objects = []
    single_max_volume_objects = []

    i = 0
    for instance in set_list:
        same_date_set.append(instance)
        if set_list[-1] == set_list[i] or set_list[i+1].date != instance.date:
            for same_date_instance in same_date_set:
                same_date_volume_set.append(int(same_date_instance.weight)*int(same_date_instance.reps))
            for same_date_object in same_date_set:
                if int(same_date_object.weight) * int(same_date_object.reps) == max(same_date_volume_set):
                    max_volume_objects.append(same_date_object)
            single_max_volume_objects.append(max_volume_objects[0])
            same_date_set = []
            same_date_volume_set = []
            max_volume_objects = []
        i += 1

    template_date_volume = []
    for template_volume_object in single_max_volume_objects:
        template_date_volume.append((template_volume_object.date, int(template_volume_object.weight)*int(template_volume_object.reps)))


    return render(request, 'gymloggerapp/graph_page.html', { 'username': username, 'show_graph': show_graph, 'timeframe': timeframe, 'volume_pb_detail': volume_pb_detail, 'template_date_volume':template_date_volume, 'single_max_weight_objects': single_max_weight_objects, 'template_volume': template_volume, 'highest_weight_list': highest_weight_list, 'volume_pb': volume_pb, 'weight_pb': weight_pb, 'graph': graph, 'form': GraphDropDownForm(request.GET),'exercisegroup_id': exercisegroup_id, 'exercisename': exercisename, 'sets': sets})

#JsonResponses returning set data required for graphs.
def get_data_weight(request, exercisegroup_id):

    if not request.user.is_authenticated:
        return redirect('login')

    global global_sets_used

    exercisename = ExerciseName.objects.get(pk=exercisegroup_id)
    
    sets = global_sets_used.filter(exercisegroup=exercisename).order_by('date')
    set_list = []
    highest_weight_list = []

    for each_set in sets:
        set_list.append(each_set)
    
    #Creates a list (highest_weight_list) of SetLogger objects with the highest recorded weight at the date
    #of creation.
    
    i = 0
    check_weight_list = []
    highest_weight_list = []
    for set_instance in set_list:
        check_weight_list.append(set_instance.weight)
        if i == 0:
            highest_weight_list.append(set_list[0])
        elif max(check_weight_list) <= set_instance.weight:
            if highest_weight_list[-1].date != set_instance.date:
                highest_weight_list.append(set_instance)
            elif highest_weight_list[-1].date == set_instance.date:
                highest_weight_list.remove(highest_weight_list[-1])
                highest_weight_list.append(set_instance)
        i += 1

    #Creating JsonResponse
    weights = []
    xnumbers = []
    xlabels = []

    index = 0
    x = 0
    for weight_object in highest_weight_list:
        if index == 0:
           weights.append({ "x": 0, "y": int(weight_object.weight) })
           xnumbers.append(0)
           xlabels.append(str(weight_object.date))
        else:
           delta = weight_object.date - highest_weight_list[index-1].date
           x += delta.days
           weights.append({ "x": int(x), "y": int(weight_object.weight) })
           xnumbers.append(int(x))
           xlabels.append(str(weight_object.date))
        index += 1

    data = { "weights": weights, "xnumbers": xnumbers, "xlabels": xlabels }
    
    return JsonResponse(data, safe=False)

def get_data_volume(request, exercisegroup_id):

    if not request.user.is_authenticated:
        return redirect('login')

    global global_sets_used

    exercisename = ExerciseName.objects.get(pk=exercisegroup_id)
    sets = global_sets_used.filter(exercisegroup=exercisename).order_by('date')
    
    set_list = []
    highest_volume_list = []

    for each_set in sets:
        set_list.append(each_set)
    
    #Creates a list (highest_volume_list) of SetLogger objects with the highest recorded volume at the date
    #of creation.

    i = 0
    check_volume_list = []
    highest_volume_list = []
    for set_instance in set_list:
        check_volume_list.append(int(set_instance.weight)*int(set_instance.reps))
        if i == 0:
            highest_volume_list.append(set_list[0])
        elif max(check_volume_list) <= int(set_instance.weight)*int(set_instance.reps):
            if highest_volume_list[-1].date != set_instance.date:
                highest_volume_list.append(set_instance)
            elif highest_volume_list[-1].date == set_instance.date:
                highest_volume_list.remove(highest_volume_list[-1])
                highest_volume_list.append(set_instance)
        i += 1
    
    
    #Creating JsonResponse
    volumes = []
    xnumbers = []
    xlabels = []

    index = 0
    x = 0
    for volume_object in highest_volume_list:
        if index == 0:
           volumes.append({ "x": 0, "y": int(volume_object.weight)*int(volume_object.reps) })
           xnumbers.append(0)
           xlabels.append(str(volume_object.date))
        else:
           delta = volume_object.date - highest_volume_list[index-1].date
           x += delta.days
           volumes.append({ "x": int(x), "y": int(volume_object.weight)*int(volume_object.reps) })
           xnumbers.append(int(x))
           xlabels.append(str(volume_object.date))
        index += 1

    data = { "volumes": volumes, "xnumbers": xnumbers, "xlabels": xlabels }
    
    return JsonResponse(data, safe=False)

def get_data_weight_workout(request, exercisegroup_id):

    if not request.user.is_authenticated:
        return redirect('login')

    global global_sets_used

    exercisename = ExerciseName.objects.get(pk=exercisegroup_id)
    sets = global_sets_used.filter(exercisegroup=exercisename).order_by('date')
    
    set_list = []

    for each_set in sets:
        set_list.append(each_set)
    
    same_date_set = []
    same_date_weight_set = []
    max_weight_objects = []
    single_max_weight_objects = []

    #Creates a list (highest_weight_list) of SetLogger objects with the highest recorded weight per date recorded.
    i = 0
    for instance in set_list:
        same_date_set.append(instance)
        if set_list[-1] == set_list[i] or set_list[i+1].date != instance.date:
            for same_date_instance in same_date_set:
                same_date_weight_set.append(int(same_date_instance.weight))
            for same_date_object in same_date_set:
                if int(same_date_object.weight) == max(same_date_weight_set):
                    max_weight_objects.append(same_date_object)
            single_max_weight_objects.append(max_weight_objects[0])
            same_date_set = []
            same_date_weight_set = []
            max_weight_objects = []
        i += 1


    dateweights = []
    xnumbers = []
    xlabels = []

    index = 0
    x = 0
    for dateweight_object in single_max_weight_objects:
        if index == 0:
           dateweights.append({ "x": 0, "y": int(dateweight_object.weight) })
           xnumbers.append(0)
           xlabels.append(str(dateweight_object.date))
        else:
           delta = dateweight_object.date - single_max_weight_objects[index-1].date
           x += delta.days
           dateweights.append({ "x": int(x), "y": int(dateweight_object.weight) })
           xnumbers.append(int(x))
           xlabels.append(str(dateweight_object.date))
        index += 1

    data = { "dateweights": dateweights, "xnumbers": xnumbers, "xlabels": xlabels }
    
    return JsonResponse(data, safe=False)

def get_data_volume_workout(request, exercisegroup_id):

    if not request.user.is_authenticated:
        return redirect('login')

    global global_sets_used

    exercisename = ExerciseName.objects.get(pk=exercisegroup_id)
    sets = global_sets_used.filter(exercisegroup=exercisename).order_by('date')
    
    set_list = []

    for each_set in sets:
        set_list.append(each_set)
    
    same_date_set = []
    same_date_volume_set = []
    max_volume_objects = []
    single_max_volume_objects = []

    #Creates a list (highest_weight_list) of SetLogger objects with the highest recorded volume per date recorded.
    i = 0
    for instance in set_list:
        same_date_set.append(instance)
        if set_list[-1] == set_list[i] or set_list[i+1].date != instance.date:
            for same_date_instance in same_date_set:
                same_date_volume_set.append(int(same_date_instance.weight)*int(same_date_instance.reps))
            for same_date_object in same_date_set:
                if int(same_date_object.weight) * int(same_date_object.reps) == max(same_date_volume_set):
                    max_volume_objects.append(same_date_object)
            single_max_volume_objects.append(max_volume_objects[0])
            same_date_set = []
            same_date_volume_set = []
            max_volume_objects = []
        i += 1

    datevolumes = []
    xnumbers = []
    xlabels = []

    index = 0
    x = 0
    for datevolume_object in single_max_volume_objects:
        if index == 0:
           datevolumes.append({ "x": 0, "y": int(datevolume_object.weight) * int(datevolume_object.reps) })
           xnumbers.append(0)
           xlabels.append(str(datevolume_object.date))
        else:
           delta = datevolume_object.date - single_max_volume_objects[index-1].date
           x += delta.days
           datevolumes.append({ "x": int(x), "y": int(datevolume_object.weight) * int(datevolume_object.reps) })
           xnumbers.append(int(x))
           xlabels.append(str(datevolume_object.date))
        index += 1

    data = { "datevolumes": datevolumes, "xnumbers": xnumbers, "xlabels": xlabels }
    
    return JsonResponse(data, safe=False)


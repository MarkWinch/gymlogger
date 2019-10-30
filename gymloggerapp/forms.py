from django import forms
from .models import SetLogger, ExerciseName, MuscleGroup
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UpdateProfile(forms.ModelForm):
    '''
    Form used to update email and username for an account.
    '''
    email = forms.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username', 'email',)

class SignUpForm(UserCreationForm):
    '''
    For allowing a user to create an account.
    '''
    email = forms.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )

class ExerciseForeignKeyForm(forms.ModelForm):
    '''
    Custom form used in a modelformset allowing editing of exercises.
    '''

    def __init__(self, *args, **kwargs):
            user_id = kwargs.pop('user_id')
            super(ExerciseForeignKeyForm, self).__init__(*args, **kwargs)
            self.fields['muscle_group'].queryset = MuscleGroup.objects.filter(user=user_id)
 
    class Meta:
        model = ExerciseName
        fields = ('muscle_group', 'name_of_exercise', 'delete_true')
        widgets={ 'name_of_exercise': forms.TextInput(attrs={'class':'muscle-form'}),
                  'muscle_group': forms.Select(attrs={'class':'muscle-dropdown'}),
                  'delete_true': forms.CheckboxInput(attrs={ 'class': 'delete-exercises' })}
        labels={'delete_true': ''}

class MuscleDropDownForm(forms.Form):
    '''
    Dropdown form used to select a muscle group.
    '''
    def __init__(self, *args, **kwargs):
            user_id = kwargs.pop('user_id')
            super(MuscleDropDownForm, self).__init__(*args, **kwargs)
            self.fields['muscle_choice'].queryset = MuscleGroup.objects.filter(user=user_id).order_by('muscle')
    

    muscle_choice = forms.ModelChoiceField(queryset=MuscleGroup.objects.all(), empty_label="All", widget=forms.Select(attrs={'onchange': 'this.form.submit();'}))
    
def GraphChoices():
    '''
    This function returns the specifications used to display each graph.
    '''
    return [
            ('Highest recorded weight over time', 'Highest recorded weight over time'), 
            ('Highest recorded volume over time', 'Highest recorded volume over time'), 
            ('Highest weight per workout', 'Highest weight per workout'), 
            ('Highest volume per workout', 'Highest volume per workout')]

def TimeChoices():
    '''
    This function returns the timeframes used to display each graph.
    '''
    return [
            ('All', 'All'),
            ('1 month', '1 month'), 
            ('3 months', '3 months'), 
            ('6 months', '6 months'), 
            ('1 year', '1 year')]
            
class GraphDropDownForm(forms.Form):
    '''
    This form provides dropdown form selections for which graph to display, and which timeframe to use.
    '''

    graph = forms.ChoiceField(choices=GraphChoices(), widget=forms.Select(attrs={'onchange': 'this.form.submit();'}))
    timeframe = forms.ChoiceField(choices=TimeChoices(), widget=forms.Select(attrs={'onchange': 'this.form.submit();'}))

def SetCardsTimeframeMonths():
    '''
    This function returns month choices for displaying sets.
    '''
    return [
            ('All months', 'All months'),
            ('January', 'January'), 
            ('February', 'February'), 
            ('March', 'March'), 
            ('April', 'April'),
            ('May', 'May'),
            ('June', 'June'),
            ('July', 'July'),
            ('August', 'August'),
            ('September', 'September'),
            ('October', 'October'),
            ('November', 'November'),
            ('December', 'December')]

def SetCardsTimeframeYears(user_id):
    '''
    This function returns year options to display sets.
    '''
    sets = SetLogger.objects.filter(user=user_id).order_by('date')
    selection_list = [('All years', 'All years')]
    set_list = []
    years_on_record = []

    for set_instance in sets:
        set_list.append(set_instance)

    for each_set in set_list:
        if str(each_set.date.year) not in years_on_record:
           selection_list.append((str(each_set.date.year), str(each_set.date.year)))
        years_on_record.append(str(each_set.date.year))
        
    return selection_list


class SetCardsTimeframeForm(forms.Form):
    '''
    This form allows the user to select a month and year to display sets.
    '''

    def __init__(self, *args, **kwargs):
            user_id = kwargs.pop('user_id')
            super(SetCardsTimeframeForm, self).__init__(*args, **kwargs)
            self.fields['year'].choices = SetCardsTimeframeYears(user_id)
            

    month = forms.ChoiceField(choices=SetCardsTimeframeMonths(), widget=forms.Select(attrs={'onchange': 'this.form.submit();'}))
    year = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'onchange': 'this.form.submit();'}))

class DeleteAccountForm(forms.Form):
    '''
    This form allows the user to deactivate their account.
    '''
    delete_account = forms.CharField(widget=forms.HiddenInput(), initial='delete')

class MuscleGroupForm(forms.ModelForm):
    '''
    This form allows the user to add a muscle group.
    '''

    muscle = forms.CharField(widget=forms.TextInput(attrs={'class':
        'muscle-form', 'autocomplete':'off'}))

    class Meta: 
        model = MuscleGroup
        fields = ('muscle',)


class ExerciseNameForm(forms.ModelForm):
    '''
    This form allows a user to add an exercise. 
    '''

    def __init__(self, *args, **kwargs):
            user_id = kwargs.pop('user_id')
            super(ExerciseNameForm, self).__init__(*args, **kwargs)
            self.fields['muscle_group'].queryset = MuscleGroup.objects.filter(user=user_id)

    name_of_exercise = forms.CharField(widget=forms.TextInput(attrs={'class':
        'exercise-form', 'autocomplete':'off'}))
    muscle_group = forms.ModelChoiceField(queryset=MuscleGroup.objects.all(), widget=forms.Select(attrs={'class':'muscle-dropdown'}))
    

    class Meta: 
        model = ExerciseName
        fields = ('name_of_exercise', 'muscle_group',)



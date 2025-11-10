from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import User,UserProfile
from django.shortcuts import get_object_or_404, render
from .encryption import encrypt, decrypt

# Create your views here.
def main(request):
    return render(request, "main/main.html" )

def login_view(request):
    return render(request, "login.html" )

def user_profile_view(request):
    return render(request, "user_profile.html" )


def user_profile(request):
    if request.method == "POST":
        # Check if user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to update your profile")
            return redirect('login')
        
        # Get the measurements from POST data
        chest = request.POST.get('chest')
        waist_circumference = request.POST.get('waist')
        hip_circumference = request.POST.get('hips')
        inseam = request.POST.get('inseam')
        height = request.POST.get('height')
        weight = request.POST.get('weight')  # Get weight
        body_shape = request.POST.get('body-shape', '')
        
        # CRITICAL: Get the uploaded photo from FILES (not POST!)
        photo = request.FILES.get('photo')
        
        user = request.user
        
        # Try to get existing profile or create a new one
        try:
            profile = UserProfile.objects.get(user=user)
            print("Existing profile found")
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=user)
            print("Creating new profile")
        
        # Update profile fields
        chest = encrypt(str(chest))
        waist_circumference = encrypt(str(waist_circumference))
        hip_circumference = encrypt(str(hip_circumference))
        inseam = encrypt(str(inseam))
        height = encrypt(str(height))
        



        profile.chest = chest
        profile.waist_circumference = waist_circumference
        profile.hip_circumference = hip_circumference
        profile.Inseam_length = inseam
        profile.height = height
        
        # Handle weight properly - only set if provided
        if weight and weight.strip():
            weight = encrypt(str(weight))
            profile.weight = weight
        else:
            profile.weight = None
        
        profile.body_shape = body_shape
        
        # CRITICAL: Only update image if a new one was uploaded
        if photo:
            profile.image = photo
            print(f"Image uploaded: {photo.name}, Size: {photo.size} bytes")
        else:
            print("No image uploaded")
        
        # Debug print before saving
        print(f"Saving profile with image: {profile.image}")
        
        # Save the profile
        profile.save()
        
        # Debug print after saving
        print(f"Profile saved! Image path: {profile.image}")
        if profile.image:
            print(f"Image URL: {profile.image.url}")
        
        messages.success(request, "Profile updated successfully!")
        return redirect('core-main')
    
    # GET request - render the form
    return render(request, "user_profile2.html")


def signup(request):
    if request.method == "POST":
        fname = request.POST['firstname']
        lname = request.POST['lastname']
        email = request.POST['email']
        pass1 = request.POST['signup-password']
        pass2 = request.POST['signup-confirm-password']

        if User.objects.filter(email=email):
            messages.error(request, "Email already exists. Try other email")
            return redirect('login')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't match")
            return redirect('login')

        myuser = User.objects.create_user(email=email, password=pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()
        
        messages.success(request, "Account successfully created.")


        #Welcome email
        # subject = "Welcome to SOS Pay!"
        # message = "Hello " + myuser.first_name + "!!\n" + "Welcome to SOS Pay\n Thank You for visiting this site.\n We have sent you a confirmation email. Please confirm your email address to activate your account. \n\n  Thank you "+fname
        # from_email = 'larteyian@gmail.com'
        # receipient_list = [myuser.email]
        # send_mail(subject, message, from_email, receipient_list, fail_silently=False)



        return redirect('signin')
    
    return redirect('login_view')

def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('core-main')

def signin(request):
    if request.method == "POST":
        email = request.POST['login-email']
        pass1 = request.POST['login-password']

        user = authenticate(email=email, password=pass1)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('core-main')  # Redirect to dashboard or main page
        else:
            messages.error(request, "Invalid email or password")
            return redirect('login')

    return redirect('core-main')

def profile(request):
    if request.method == "POST":
        chest = request.POST['chest']
        waist_circumference = request.POST['waist']
        hip_circumference = request.POST['hips']
        inseam = request.POST['inseam']
        height = request.POST['height']
        weight = request.POST['weight']
        body_shape = request.POST['body-shape']
        photo = request.POST['fname']

        email = request.session.get('email')
        user =  get_object_or_404(User, email=email)
        profile = get_object_or_404(UserProfile, user=user)

        profile.chest = chest
        profile.waist_circumference = waist_circumference
        profile.hip_circumference = hip_circumference
        profile.height = height
        profile.weight = weight
        profile.body_shape = body_shape
        profile.Inseam_length = inseam
        profile.image = photo

        profile.save()
        


        return redirect('core-main')




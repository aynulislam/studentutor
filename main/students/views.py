from django.shortcuts import render,redirect

from .forms import StudentSignupForm, StudentProfile, PostAnAdForm, AboutStudentForm, ProfilePicture
from django.contrib.auth.models import Group


from django.contrib.auth.models import User

from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.decorators import login_required

from .models import TutorInvitaions , Student, PostAnAd

from tutors.models import PostAnAd as PostAnAd_tutor
from tutors.models import Invitaions

from django.contrib import messages
# Create your views here.


def studentRegister(request):
    form = StudentSignupForm()

    if request.method == "POST":
        form = StudentSignupForm(request.POST)

        if form.is_valid():
            student = form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            age = form.cleaned_data.get('age')
            city = form.cleaned_data.get('city')
            firstName = form.cleaned_data.get('first_name')
            lastName = form.cleaned_data.get('last_name')

            group = Group.objects.get(name="students")
            student.groups.add(group)

            Student.objects.create(
                student=student,
                username= username,
                email = email,
                age =age,
                city = city,
                first_name = firstName,
                last_name = lastName
            )
            messages.success(request,'account was created for ' + username)
            return redirect("sign_in")

    context = {
        "form": form
    }
    return render(request, 'students/student_sign_up.html', context)


@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["students"])
def studentDashboard(request):
    student = request.user.student


    form = StudentProfile(instance=student)

    user = Student.objects.get(username = request.user.username)

    active_ads = PostAnAd.objects.filter(studentUser = request.user.student).count()

    p_form = ProfilePicture()

    if request.method=="POST":
        form = StudentProfile(request.POST,request.FILES, instance=student)
        p_form = ProfilePicture(request.POST, request.FILES)

        if p_form.is_valid():
            image = p_form.cleaned_data["image"]
            std_image = Student.objects.get(username = request.user.username)
            std_image.user_image = image
            std_image.save()

            return redirect("student_dashboard")
        else:
            messages.warning(request, 'Supported File Extensions are .jpg And .png, Max Image Size Is 1MB')
            return redirect("student_dashboard")

        if form.is_valid():
            form.save()

    context = {
        "form": form,
        "p_form": p_form,
        "totalAds": user.total_ads,
        "adsDel": user.ads_deleted,
        "activeAds": active_ads,
        "invitations_sent": user.invitations_sent,
        "invitations_sent_accepted": user.invitations_sent_accepted,
        "invitations_sent_rejected": user.invitations_sent_rejected,
        "invitations_recieved": user.invitations_recieved,
        "invitations_recieved_accepted": user.invitations_recieved_accepted,
        "invitations_recieved_rejected": user.invitations_recieved_rejected,
    }
    return render(request, 'students/student_dashboard.html', context)

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["students"])
def postAd(request, pk):
    postform = PostAnAdForm()
    user = Student.objects.get(username = request.user.username)

    postCount = user.ad_post_count

    if request.method == "POST":
        postform = PostAnAdForm(request.POST)
        

        if postform.is_valid():
            subject = postform.cleaned_data["subject"]
            tuition_level = postform.cleaned_data["tuition_level"]
            tuition_type = postform.cleaned_data["tuition_type"]
            address = postform.cleaned_data["address"]
            hours_per_day = postform.cleaned_data["hours_per_day"]
            days_per_week = postform.cleaned_data["days_per_week"]
            estimated_fees = postform.cleaned_data["estimated_fees"]

            PostAnAd.objects.create(
                studentUser = user,
                subject = subject,
                tuition_level = tuition_level,
                tuition_type = tuition_type,
                address = address,
                hours_per_day = hours_per_day,
                days_per_week = days_per_week,
                estimated_fees = estimated_fees
            )

            user.total_ads += 1
            user.ad_post_count += 1
            user.save()
            messages.info(request, "Your post is Successfully Created")
            return redirect("student_dashboard")
    context = {
        "form": postform
    }
    return render(request, 'students/post_ad.html', context)



@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["students"])
def Ads(request):
    try:
        studentAbout = AboutStudent.objects.get(student__username = request.user.username).order_by("-id")
    except:
        studentAbout = None
    ads = PostAnAd.objects.filter(studentUser=request.user.student).order_by("-id")
    context = {
        "ads":ads,
        "about": studentAbout
    }
    return render(request, 'students/ads.html', context)

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["students"])
def AdsDelete(request, pk):

    ad = PostAnAd.objects.get(id=pk)

    user = Student.objects.get(username=request.user.username)

    if request.method == "POST":
        ad.delete()
        user.ads_deleted += 1
        user.ad_post_count -=1
        user.save()
        return redirect("ads")
    context = {
        'ad':ad
    }
    return render(request, 'students/delete_ad.html', context)

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["students"])
def allTutors(request):
    tutors = PostAnAd_tutor.objects.all().order_by("-id")
    tuition_level_contains_query = request.GET.get('TuitionLevel')
    subject_contains_query = request.GET.get('Subject')
    city_contains_query = request.GET.get('City')

    if tutors:
        if tuition_level_contains_query != "" and tuition_level_contains_query is not None and tuition_level_contains_query != "All":
            tutors = tutors.filter(tuition_level = tuition_level_contains_query).order_by("-id")

        if subject_contains_query != "" and subject_contains_query is not None:
            tutors = tutors.filter(subject__icontains = subject_contains_query).order_by("-id")

        if city_contains_query != "" and city_contains_query is not None:
            tutors = tutors.filter(tutorUser__city__icontains = city_contains_query).order_by("-id")


    context = {
        "tutors":tutors
    }
    return render(request, 'students/all_tutors.html', context)

from tutors.models import AboutAndQualifications

def SpecificTutor(request, id):
    tutor = PostAnAd_tutor.objects.get(id = id)
    qual = AboutAndQualifications.objects.get(tutor__username = tutor.tutorUser.username)
    tutor.views += 1
    tutor.save()
    context = {
        "tutor": tutor,
        "qual": qual
    }
    return render (request, "students/specific_tutor.html", context)

from tutors.models import Tutor

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["students"])
def inviteFordemo(request, id):
    ad = PostAnAd_tutor.objects.get(id = id).order_by("-id")

    tutor = Tutor.objects.get ( username = ad.tutorUser.username)

    user = Student.objects.get(username = request.user.username)

    std = Student.objects.get(username = request.user.username)
    try:
        invites_sent_by_std = Invitaions.objects.get(tutor_ad = ad)
    except:
        invites_sent_by_std = None

    if request.method == "POST":
        if invites_sent_by_std != None:
            if invites_sent_by_std.invitation_sent == True and invites_sent_by_std.inivitaion_by_student.username == request.user.username: 
                messages.info(request, f'Invitation request already sent to {ad.tutorUser.first_name} {ad.tutorUser.last_name}')
                return redirect("all_tutors")
            else:
                Invitaions.objects.create(
                    inivitaion_by_student = std,
                    tutor_ad = ad,
                    invitation_sent = True,
                    accepted = False,
                    rejected = False
                )
                user.invitations_sent += 1
                user.save()
                tutor.invitations_recieved += 1
                tutor.save()
                messages.info(request, f'Invited {tutor.first_name} {tutor.last_name} For A Demo')
                return redirect("invited")

        else:
            Invitaions.objects.create(
                    inivitaion_by_student = std,
                    tutor_ad = ad,
                    invitation_sent = True,
                    accepted = False,
                    rejected = False
                )
            user.invitations_sent += 1
            user.save()
            tutor.invitations_recieved += 1
            tutor.save()
            messages.info(request, f'Invited {tutor.first_name} {tutor.last_name} For A Demo')
            return redirect("invited")
    context = {
        "ad":ad
    }
    return render(request, 'students/invite_for_demo.html', context)

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["students"])
def invited(request):
    student = Student.objects.get(username = request.user.username)
    invited = Invitaions.objects.filter(inivitaion_by_student= student).order_by("-id")
    context={
        "invited": invited,
    }
    return render(request, "students/invited.html", context)

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["students"])
def invitations(request):
    invites = TutorInvitaions.objects.filter(student_ad__studentUser = request.user.student).order_by("-id")
    context = {
        "invites":invites
    }

    return render(request, 'students/invitations.html', context)

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["students"])
def view_your_ad(request, id):
    student_ad = TutorInvitaions.objects.get(id = id)
    try:
        tutors = PostAnAd_tutor.objects.filter(subject = student_ad.student_ad.subject)[4]
    except:
        tutors = PostAnAd_tutor.objects.filter(subject = student_ad.student_ad.subject)

    context = {
        "invite":student_ad,
        "tutors": tutors
    }
    return render(request,'students/view_your_ad.html', context)

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["students"])
def acceptInvitation(request, id):
    invite = TutorInvitaions.objects.get(id = id)

    student = Student.objects.get(username = request.user.username)
    tutor = Tutor.objects.get(username = invite.inivitaion_by_tutor.username)
    if request.method == "POST":
        invite.accepted = True
        invite.rejected = False
        invite.save()
        student.invitations_recieved_accepted += 1
        student.save()
        tutor.invitations_sent_accepted += 1
        tutor.save()
        messages.info(request, f'Accepted Invitation Request from {tutor.first_name} {tutor.last_name}')
        return redirect("invitations_student")
    context = {
        "invite":invite
    }

    return render(request, "students/accept_invitation.html", context)

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["students"])
def rejectInvite(request, id):
    invite = TutorInvitaions.objects.get(id = id)

    student = Student.objects.get(username = request.user.username)
    tutor = Tutor.objects.get(username = invite.inivitaion_by_tutor.username)
    if request.method == "POST":
        invite.delete()
        student.invitations_recieved_rejected += 1
        student.save()

        tutor.invitations_sent_rejected += 1
        tutor.save()
        messages.warning(request, f'Rejected Invite From {tutor.first_name} {tutor.last_name}')
        return redirect("invitations_student")
    context = {}
    return render(request,'students/reject_invitation.html', context)


@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["students"])
def aboutStudent(request):
    aboutForm  = AboutStudentForm()


    if request.method == "POST":
        aboutForm = AboutStudentForm(request.POST)
        if aboutForm.is_valid():
            try:
                AboutStudent.objects.get(student__username = request.user.username).delete()
            except:
                pass
            about = aboutForm.cleaned_data["textArea"]
            std = Student.objects.get(username=request.user.username)
            std.profile_complete = True
            std.textArea = about
            std.save()
            return redirect("student_dashboard")
    context = {
        "form": aboutForm
    }

    return render(request, "students/student_about.html", context)


@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["students"])
def del_account_student(request):
    student = User.objects.get(username = request.user.username)
    if request.method == "POST":
        student.is_active = False
        student.save()
        return redirect("student_dashboard")
    context = {}
    return render(request, "students/del_account.html", context)
from turtle import position
from django.shortcuts import render, reverse, redirect
from voting.models import Voter, Position, Candidate, Votes
from account.models import CustomUser
from account.forms import CustomUserForm
from voting.forms import *
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import csv
from django.db.models import Count


def psg_voterlist(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse('text/csv')
    response['Content-Disposition'] = 'attachment; filename=votes.csv'
    votes = Votes.objects.all()
    voter_name_list = []
    candidate_name_list = []
    position_name_list = []
    yes_voted_list = []
    no_voted_list = []
    for vote in votes:
        voter_name = vote.voter.admin.username
        candidate = vote.candidate.fullname
        position = vote.candidate.position
        yes_voted = vote.yes_vote
        no_voted = vote.no_vote

        voter_name_list.append(voter_name)
        candidate_name_list.append(candidate)
        position_name_list.append(position)
        yes_voted_list.append(yes_voted)
        no_voted_list.append(no_voted)
    writer = csv.writer(response)
    writer.writerow(['Voters Name', 'Candidate',
                     'Position', 'Yes Voted', 'No Voted'])
    for(a, b, c, d, e) in zip(voter_name_list, candidate_name_list, position_name_list, yes_voted_list, no_voted_list):
        writer.writerow([a, b, c, d, e])

    return response


def psg_counter(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse('text/csv')
    response['Content-Disposition'] = 'attachment; filename=votes.csv'
    x = Votes.objects.all().values('candidate', 'yes_vote').annotate(
        total=Count('candidate')).order_by('total')
    candidates = Candidate.objects

    # votes = Votes.objects.all()
    candidate_name = []
    position_list = []
    position_id_list = []
    count_list = []
    # yes_voted_list = []
    # no_voted_list = []
    for vote in x:
        # voter_name = vote.voter.admin.username
        candidate = candidates.get(id=int(vote['candidate'])).fullname
        position = candidates.get(id=int(vote['candidate'])).position.name
        position_id = candidates.get(
            id=int(vote['candidate'])).position.priority
        count = vote['total']

        candidate_name.append(candidate)
        position_list.append(position)
        count_list.append(count)
        position_id_list.append(position_id)
    writer = csv.writer(response)
    writer.writerow(['Candidate Name', 'Position_id', 'Position', 'Count'])
    list_test = []

    for(a, b, c, d) in zip(candidate_name, position_id_list, position_list, count_list):

        list_test.append((a, b, c, d))
        # writer.writerow([a, b, c])
    list_test.sort(key=lambda x: x[1])
    for(a, b, c, d) in list_test:
        writer.writerow([a, b, c, d])

    print(list_test)

    return response


def find_n_winners(data, n):
    """Read More
    https://www.geeksforgeeks.org/python-program-to-find-n-largest-elements-from-a-list/
    """
    final_list = []
    candidate_data = data[:]
    # print("Candidate = ", str(candidate_data))
    for i in range(0, n):
        max1 = 0
        if len(candidate_data) == 0:
            continue
        this_winner = max(candidate_data, key=lambda x: x['votes'])
        # TODO: Check if None
        this = this_winner['name'] + \
            " with " + str(this_winner['votes']) + " votes"
        final_list.append(this)
        candidate_data.remove(this_winner)
    return ", &nbsp;".join(final_list)


def dashboard(request):
    positions = Position.objects.all().order_by('priority')
    candidates = Candidate.objects.all()
    voters = Voter.objects.all()
    voted_voters = Voter.objects.filter(voted=1)
    list_of_candidates = []
    votes_count = []
    chart_data = {}

    for position in positions:
        list_of_candidates = []
        votes_count = []
        for candidate in Candidate.objects.filter(position=position):
            list_of_candidates.append(candidate.fullname)
            votes = Votes.objects.filter(candidate=candidate).count()
            votes_count.append(votes)
        chart_data[position] = {
            'candidates': list_of_candidates,
            'votes': votes_count,
            'pos_id': position.id
        }

    context = {
        'position_count': positions.count(),
        'candidate_count': candidates.count(),
        'voters_count': voters.count(),
        'voted_voters_count': voted_voters.count(),
        'positions': positions,
        'chart_data': chart_data,
        'page_title': "Dashboard"
    }
    return render(request, "admin/home.html", context)


def voters(request):
    voters = Voter.objects.all()
    userForm = CustomUserForm(request.POST or None)
    voterForm = VoterForm(request.POST or None)
    context = {
        'form1': userForm,
        'form2': voterForm,
        'voters': voters,
        'page_title': 'Voters List'
    }
    if request.method == 'POST':
        if userForm.is_valid() and voterForm.is_valid():
            user = userForm.save(commit=False)
            voter = voterForm.save(commit=False)
            voter.admin = user
            user.save()
            voter.save()
            messages.success(request, "New voter created")
        else:
            messages.error(request, "Form validation failed")
    return render(request, "admin/voters.html", context)


def view_voter_by_id(request):
    voter_id = request.GET.get('id', None)
    voter = Voter.objects.filter(id=voter_id)
    context = {}
    if not voter.exists():
        context['code'] = 404
    else:
        context['code'] = 200
        voter = voter[0]
        context['username'] = voter.admin.username
        # context['last_name'] = voter.admin.last_name
        context['phone'] = voter.phone
        context['id'] = voter.id
        # context['email'] = voter.admin.email
    return JsonResponse(context)


def countdown_view(request):
    context = {}
    # if countDown.objects.exists():
    #     countdown = countDown.objects.all()[0]
    #     context['countdown'] = countdown
    countdownForm = CountDownForm(request.POST, request.FILES or None)
    context['form1'] = countdownForm
    context['page_title'] = 'Count Down List'

    if request.method == 'POST':
        if countdownForm.is_valid():
            countdownform = countdownForm.save(commit=False)
            countdownform.save()
            messages.success(request, "New counter is created")
        else:
            messages.error(request, "Form validation failed")
    return render(request, "admin/votecountdown.html", context)


def view_counter_by_id(request):
    counter_id = request.GET.get('id', None)
    counter = countDown.objects.filter(id=counter_id)
    context = {}
    if not counter.exists():
        context['code'] = 404
    else:
        context['code'] = 200
        counter = counter[0]
        context['title'] = counter.title
        context['end_time_counter'] = counter.end_time_counter
        context['view_flag'] = counter.view_flag
        context['id'] = counter.id
    return JsonResponse(context)


def updateCounter(request):

    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        instance = countDown.objects.get(id=request.POST.get('id'))
        counter = CountDownForm(request.POST or None,
                                request.FILES or None, instance=instance)
        if counter.is_valid():
            counter.save()
            messages.success(request, "Counter's  updated")

    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('adminViewTimeCounter'))


def deleteCounter(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        counter = countDown.objects.get(id=request.POST.get('id'))
        counter.delete()
        messages.success(request, "Counter Has Been Deleted")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('adminViewTimeCounter'))


def view_position_by_id(request):
    pos_id = request.GET.get('id', None)
    pos = Position.objects.filter(id=pos_id)
    context = {}
    if not pos.exists():
        context['code'] = 404
    else:
        context['code'] = 200
        pos = pos[0]
        context['name'] = pos.name
        # context['max_vote'] = pos.max_vote
        context['id'] = pos.id
    return JsonResponse(context)


def updateVoter(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        instance = Voter.objects.get(id=request.POST.get('id'))
        print("instance2", instance)
        user = CustomUserForm(request.POST or None, instance=instance.admin)

        voter = VoterForm(request.POST or None, instance=instance)
        user.save()
        voter.save()
        messages.success(request, "Voter's bio updated")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('adminViewVoters'))


def deleteVoter(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        admin = Voter.objects.get(id=request.POST.get('id')).admin
        admin.delete()
        messages.success(request, "Voter Has Been Deleted")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('adminViewVoters'))


def viewPositions(request):
    positions = Position.objects.order_by('-priority').all()
    form = PositionForm(request.POST or None)
    context = {
        'positions': positions,
        'form1': form,
        'page_title': "Positions"
    }
    if request.method == 'POST':
        if form.is_valid():
            form = form.save(commit=False)
            form.priority = positions.count() + 1  # Just in case it is empty.
            form.save()
            messages.success(request, "New Position Created")
        else:
            messages.error(request, "Form errors")
    return render(request, "admin/positions.html", context)


def updatePosition(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        instance = Position.objects.get(id=request.POST.get('id'))
        pos = PositionForm(request.POST or None, instance=instance)
        pos.save()
        messages.success(request, "Position has been updated")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('viewPositions'))


def deletePosition(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        pos = Position.objects.get(id=request.POST.get('id'))
        pos.delete()
        messages.success(request, "Position Has Been Deleted")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('viewPositions'))


def viewCandidates(request):
    candidates = Candidate.objects.all()
    form = CandidateForm(request.POST or None, request.FILES or None)
    context = {
        'candidates': candidates,
        'form1': form,
        'page_title': 'Candidates'
    }
    if request.method == 'POST':
        if form.is_valid():
            form = form.save()
            messages.success(request, "New Candidate Created")
        else:
            messages.error(request, "Form errors")
    return render(request, "admin/candidates.html", context)


def updateCandidate(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        candidate_id = request.POST.get('id')
        candidate = Candidate.objects.get(id=candidate_id)
        form = CandidateForm(request.POST or None,
                             request.FILES or None, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, "Candidate Data Updated")
        else:
            messages.error(request, "Form has errors")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('viewCandidates'))


def deleteCandidate(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        pos = Candidate.objects.get(id=request.POST.get('id'))
        pos.delete()
        messages.success(request, "Candidate Has Been Deleted")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('viewCandidates'))


def view_candidate_by_id(request):
    candidate_id = request.GET.get('id', None)
    candidate = Candidate.objects.filter(id=candidate_id)
    context = {}
    if not candidate.exists():
        context['code'] = 404
    else:
        candidate = candidate[0]
        context['code'] = 200
        context['fullname'] = candidate.fullname
        previous = CandidateForm(instance=candidate)
        context['form'] = str(previous.as_p())
    return JsonResponse(context)


def ballot_position(request):
    context = {
        'page_title': "Ballot Position"
    }
    return render(request, "admin/ballot_position.html", context)


def update_ballot_position(request, position_id, up_or_down):
    try:
        context = {
            'error': False
        }
        position = Position.objects.get(id=position_id)
        if up_or_down == 'up':
            priority = position.priority - 1
            if priority == 0:
                context['error'] = True
                output = "This position is already at the top"
            else:
                Position.objects.filter(priority=priority).update(
                    priority=(priority+1))
                position.priority = priority
                position.save()
                output = "Moved Up"
        else:
            priority = position.priority + 1
            if priority > Position.objects.all().count():
                output = "This position is already at the bottom"
                context['error'] = True
            else:
                Position.objects.filter(priority=priority).update(
                    priority=(priority-1))
                position.priority = priority
                position.save()
                output = "Moved Down"
        context['message'] = output
    except Exception as e:
        context['message'] = e

    return JsonResponse(context)


def ballot_title(request):
    from urllib.parse import urlparse
    url = urlparse(request.META['HTTP_REFERER']).path
    from django.urls import resolve
    try:
        redirect_url = resolve(url)
        title = request.POST.get('title', 'No Name')
        file = open(settings.ELECTION_TITLE_PATH, 'w')
        file.write(title)
        file.close()
        messages.success(
            request, "Election title has been changed to " + str(title))
        return redirect(url)
    except Exception as e:
        messages.error(request, e)
        return redirect("/")


def viewVotes(request):
    votes = Votes.objects.all()
    context = {
        'votes': votes,
        'page_title': 'Votes'
    }
    return render(request, "admin/votes.html", context)


def resetVote(request):
    Votes.objects.all().delete()
    Voter.objects.all().update(voted=False)
    messages.success(request, "All votes has been reset")
    return redirect(reverse('viewVotes'))

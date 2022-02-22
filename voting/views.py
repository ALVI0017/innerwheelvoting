from django.shortcuts import render, redirect, reverse
from account.views import account_login
from voting.models import Voter, Position, Candidate, Votes
from django.http import JsonResponse
from django.utils.text import slugify
from django.contrib import messages
from django.http import JsonResponse
import requests
import json
# Create your views here.


def index(request):
    if not request.user.is_authenticated:
        return account_login(request)
    context = {}
    # return render(request, "voting/login.html", context)


def generate_ballot(display_controls=False):
    positions = Position.objects.order_by('priority').all()
    output = ""
    candidates_data = ""
    num = 1
    # return None
    for position in positions:
        name = position.name
        position_name = slugify(name)
        candidates = Candidate.objects.filter(position=position)
        instruction = "You can vote the candidates by clicking the box"
        if candidates.count() > 1:

            for candidate in candidates:

                input_box = '<div class="button_vote button1"> Vote <input label="yes" type="radio" value="'+str(candidate.id)+'" class="flat-red ' + \
                    position_name+'" name="' + \
                    position_name+"[]" + '">  </div>'
                # input_box = '<div class="button_vote button3"><input type="radio" value="'+str(candidate.id)+'" class="flat-red ' + \
                #     position_name+'" name="' + \
                #     position_name+"[]" + '"></div>'

                image = "/media/" + str(candidate.photo)
                candidates_data = candidates_data + '<div class="column"><div class="card"  style="padding:20px"><br><img src="' + \
                    image+'"width="40%" class="clist"><span class="cname clist"> <br>' + "" + \
                    candidate.fullname+'</span></li> <li style ="  padding-left: 30px; font-size: 15px;">' + \
                    input_box + "  </div><br> </div>"

            candidates_data = '<div class="row">' + \
                candidates_data + '</div>'
            # candidates_data = candidates_data + '<li>' + input_box + '<button type="button" class="btn btn-primary btn-sm btn-flat clist platform" data-fullname="'+candidate.fullname+'" data-bio="'+candidate.bio+'"><i class="fa fa-search"></i> Platform</button><img src="' + \
            #     image+'" height="100px" width="100px" class="clist"><span class="cname clist">' + \
            #     candidate.fullname+'</span></li>'
        else:
            for candidate in candidates:
                input_box = '<div class="button_vote button1"> Yes <input type="radio" value="Yes|'+str(candidate.id)+'" class="flat-red ' + \
                    position_name+'" name="' + \
                    position_name+"[]" + '"> </div>'
                input_box_2 = '<div class="button_vote button3"> No <input type="radio" value="No|'+str(candidate.id)+'" class="flat-red ' + \
                    position_name+'" name="' + \
                    position_name+"[]" + '"> </div>'

                image = "/media/" + str(candidate.photo)
                candidates_data = candidates_data + '<div class="column"><div class="card"> <img src="' + \
                    image+'"width="40%" class="clist"><span class="cname clist">' + "<br>" + \
                    candidate.fullname+'</span></li> <li style =" display:flex; justify-content:center;padding-left:10px;font-size: 15px;">' + input_box + ' ' + ' &nbsp;&nbsp;' \
                    + input_box_2 + '</li> <br> </div></div>'
        up = ''
        if position.priority == 1:
            up = 'disabled'
        down = ''
        if position.priority == positions.count():
            down = 'disabled'
        output = output + f"""<div class="row">	<div class="col-xs-12"><div class="box box-solid" id="{position.id}">
             <div class="box-header with-border">
            <h3 class="box-title"><b>{name}</b></h3>"""

        if display_controls:
            output = output + f""" <div class="pull-right box-tools">
        <button type="button" class="btn btn-default btn-sm moveup" data-id="{position.id}" {up}><i class="fa fa-arrow-up"></i> </button>
        <button type="button" class="btn btn-default btn-sm movedown" data-id="{position.id}" {down}><i class="fa fa-arrow-down"></i></button>
        </div>"""

        output = output + f"""</div>
        <div class="box-body">
        <div class="row">
        <p>

        <span class="pull-right">

        <button type="button" class="btn btn-success btn-sm btn-flat reset" data-desc="{position_name}"><i class="fa fa-refresh"></i> Reset</button>
        </span>

        </p>
        </div>
        <br>
        <div id="candidate_list">
        <ul>
        {candidates_data}
        </ul>
        </div>
        </div>
        </div>
        </div>
        </div>
        """
        position.priority = num
        position.save()
        num = num + 1
        candidates_data = ''
    return output


def fetch_ballot(request):
    output = generate_ballot(display_controls=True)
    return JsonResponse(output, safe=False)


def dashboard(request):
    user = request.user
    votes = Votes.objects.all()
    candidates = Candidate.objects.all()
    voters = Voter.objects.all()
    voted_voters = Voter.objects.filter(voted=1)
    list_of_candidates = []
    votes_count = []
    positions = Position.objects.all().order_by('priority')

    for position in positions:
        list_of_candidates = []
        votes_count = []
        for candidate in Candidate.objects.filter(position=position):
            list_of_candidates.append(candidate.fullname)
            votes = Votes.objects.filter(candidate=candidate).count()
            votes_count.append(votes)
        # chart_data[position] = {
        #     'candidates': list_of_candidates,
        #     'votes': votes_count,
        #     'pos_id': position.id
        # }

    context = {

        # 'chart_data': chart_data,
        # 'page_title': "Dashboard"
    }

    if user.voter.voted:  # * User has voted
        # To display election result or candidates I voted for ?

        context = {
            'my_votes': Votes.objects.filter(voter=user.voter),
            # 'votes': Votes.objects.all(),
            'position_count': positions.count(),
            'candidate_count': candidates.count(),
            'voters_count': voters.count(),
            'votes_count': votes_count,
            'voted_voters_count': voted_voters.count(),
            'positions': positions,
        }
        return render(request, "voting/voter/result.html", context)

    else:

        return redirect(reverse('show_ballot'))


def show_ballot(request):
    if request.user.voter.voted:
        messages.error(request, "You have voted already")
        return redirect(reverse('voterDashboard'))
    ballot = generate_ballot(display_controls=False)
    context = {
        'ballot': ballot
    }
    return render(request, "voting/voter/ballot.html", context)


def preview_vote(request):
    if request.method != 'POST':
        error = True
        response = "Please browse the system properly"
    else:
        output = ""
        form = dict(request.POST)
        # We don't need to loop over CSRF token
        form.pop('csrfmiddlewaretoken', None)
        error = False
        data = []
        positions = Position.objects.all()
        for position in positions:

            pos = slugify(position.name)
            pos_id = position.id
            # if position.max_vote > 1:
            this_key = pos + "[]"
            form_position = form.get(this_key)
            print('form_position', form_position)
            if form_position is None:
                continue

            start_tag = f"""
                <div class='row votelist' style='padding-bottom: 2px'>
                        <span class='col-sm-4'><span class=''><b>{position.name} :</b></span></span>
                        <span class='col-sm-8'>
                        <ul style='list-style-type:none; margin-left:-40px'>

            """
            end_tag = "</ul></span></div><hr/>"
            data = ""

            test_voted = False
            test_voted_str = ""
            for form_candidate_id in form_position:
                if '|' in form_candidate_id:
                    testcase = str(form_candidate_id.split('|')[0])
                    form_candidate_id = form_candidate_id.split('|')[1]
                    if testcase == 'No':
                        test_voted = False
                        test_voted_str += "test"
                    elif testcase == 'Yes':
                        test_voted = True
                        test_voted_str += "test"

                else:
                    form_candidate_id = form_candidate_id
                try:
                    candidate = Candidate.objects.get(
                        id=form_candidate_id, position=position)
                    if test_voted_str != "":
                        if test_voted == False:
                            test_str = f"""
                            <li><i class="fa-solid fa-xmark"></i>You have given No vote to {candidate.fullname}  </li>
                        """
                        else:
                            test_str = f"""
                            <li><i class="fa fa-check-square-o"></i>You have given Yes vote to {candidate.fullname} Yes Voted</li>
                        """
                    else:

                        test_str = f"""
                            <li><i class="fa fa-check-square-o"></i> {candidate.fullname}</li>
                        """
                    data += test_str
                except:
                    error = True
                    response = "Please, browse the system properly"
            output += start_tag + data + end_tag

    context = {
        'error': error,
        'list': output
    }
    return JsonResponse(context, safe=False)


def submit_ballot(request):
    if request.method != 'POST':
        messages.error(request, "Please, browse the system properly")
        return redirect(reverse('show_ballot'))

    # Verify if the voter has voted or not
    voter = request.user.voter
    if voter.voted:
        messages.error(request, "You have voted already")
        return redirect(reverse('voterDashboard'))

    form = dict(request.POST)
    form.pop('csrfmiddlewaretoken', None)  # Pop CSRF Token
    form.pop('submit_vote', None)  # Pop Submit Button

    # Ensure at least one vote is selected
    if len(form.keys()) < 1:
        messages.error(request, "Please select at least one candidate")
        return redirect(reverse('show_ballot'))
    positions = Position.objects.all()
    form_count = 0

    for position in positions:
        pos = slugify(position.name)
        pos_id = position.id
        # if position.max_vote > 1:
        this_key = pos + "[]"
        form_position = form.get(this_key)
        if form_position is None:
            continue
        test_voted = False
        test_voted_str = ""
        for form_candidate_id in form_position:
            if '|' in form_candidate_id:
                testcase = str(form_candidate_id.split('|')[0])
                form_candidate_id = form_candidate_id.split('|')[1]
                if testcase == 'No':
                    test_voted = False
                    test_voted_str += "test"
                elif testcase == 'Yes':
                    test_voted = True
                    test_voted_str += "test"

            else:
                form_candidate_id = form_candidate_id

            form_count += 1
            try:
                candidate = Candidate.objects.get(
                    id=form_candidate_id, position=position)
                vote = Votes()
                vote.candidate = candidate
                vote.voter = voter
                vote.position = position
                if test_voted_str != "":
                    if test_voted == False:
                        vote.no_vote = True
                    else:
                        vote.yes_vote = True
                else:
                    vote.yes_vote = True
                vote.save()
            except Exception as e:
                messages.error(
                    request, "Please, browse the system properly " + str(e))
                return redirect(reverse('show_ballot'))

    # Count total number of records inserted
    # Check it viz-a-viz form_count
    inserted_votes = Votes.objects.filter(voter=voter)
    if (inserted_votes.count() != form_count):
        # Delete
        inserted_votes.delete()
        messages.error(request, "Please try voting again!")
        return redirect(reverse('show_ballot'))
    else:
        # Update Voter profile to voted
        voter.voted = True
        voter.save()
        messages.success(request, "Thanks for voting")
        return redirect(reverse('voterDashboard'))

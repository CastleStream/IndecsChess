from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.utils import timezone
from django.http import JsonResponse
from .models import Game, Profile


def home(request):
    users = User.objects.all()
    games = Game.objects.all()


    games_list = []
    for game in games:
        games_list.append(game)


    if request.method == 'GET':
        return render(request, 'chessapp/home.html', {'users':users, "games":games_list})
    elif not username_present(request.POST['player1']):
        return render(request, 'chessapp/home.html', {'users':users, 'error1':'Can not find Player 1.', "games":games_list})

    elif not username_present(request.POST['player2']):
        return render(request, 'chessapp/home.html', {'users':users, 'error2':'Can not find Player 2.', "games":games_list})

    else:
        user1 = User.objects.get(username=request.POST['player1'])
        user2 = User.objects.get(username=request.POST['player2'])
        outcome = float(request.POST['outcome'])

        save_game(user1, user2, outcome)
        user1new, user2new = game_ELO(user1.profile.currentELO, user2.profile.currentELO, outcome)
        user1change = user1new - user1.profile.currentELO
        user2change = user2new - user2.profile.currentELO

        gamedata = {'user1': user1,
                    'user2': user2,
                    'outcome': outcome,
                    'user1change': user1change,
                    'user2change': user2change}

        if gamedata['outcome'] == 1:
            gamedata['message'] = 'Player 1 won.'
        elif gamedata['outcome'] == 0:
            gamedata['message'] = 'Player 2 won.'
        else:
            gamedata['outcome'] = 'Game was draw.'




        return render(request, 'chessapp/gameadded.html', {'gamedata':gamedata, "games":games_list})


def createuser(request):
    # Check if coming first time
    if request.method == 'GET':
        return render(request, 'chessapp/createuser.html')
    else:
        try:
            user = User.objects.create_user(request.POST['nickname'])
            user.profile.realname = request.POST['realname']
            user.save()
            return redirect('home')

        except IntegrityError:
            return render(request, 'chessapp/createuser.html', {'error':'That username has already been taken'})


def ranking(request):
    # users = User.objects.all().order_by('profile.currentELO')
    profiles = Profile.objects.all().order_by('-currentELO')[:10]
    ranking = []
    i = 1
    for profile in profiles:

        rank = str(i) + ". " + profile.user.username + " (" + str(profile.currentELO) +")"
        ranking.append(rank)
        i += 1
    return render(request, 'chessapp/ranking.html', {'ranking':ranking})


def playersearch(request):
    if request.method == 'GET':
        return render(request, 'chessapp/playersearch.html')
    else:
        user = User.objects.get(username=request.POST['search'])
        return redirect('playerpage', user.id)


def playerpage(request, user_pk):
    user = get_object_or_404(User, pk=user_pk)
    games = Game.objects.all()
    if request.method == 'GET':
        data = [1200]
        date = [str(user.date_joined.strftime("%d.%m.%Y"))]
        opponent = []

        for game in games:
            white = get_object_or_404(User, username=game.player1)
            black = get_object_or_404(User, username=game.player2)

            if game.player1 == user.username:
                data.append(int(GameELOWhite(game.player1ELO, game.player2ELO, game.result)))
                date.append(str(game.dateTime.strftime("%d.%m.%Y")))
                opponent.append(game.player2)

            elif game.player2 == user.username:
                data.append(int(GameELOBlack(game.player1ELO, game.player2ELO, game.result)))
                date.append(str(game.dateTime.strftime("%d.%m.%Y")))
                opponent.append(game.player1)


        return render(request, 'chessapp/playerpage.html', {'user':user, 'data':data, 'date':date})

"""
def dataToVisuals(request, user_pk):
    user = get_object_or_404(User, pk=user_pk)

    data = []
    date = []
    opponent = []

    for game in Game:
        if game.player1 == user.username:
            data.append(GameELOWhite(game.player1, game.player2, game.result))
            date.append(game.dateTime)
            opponent.append(game.player2)

        elif game.player2 == user.username:
            data.append(int(GameELOWhite(game.player1, game.player2, game.result)))
            date.append(str(game.dateTime))
            opponent.append(str(game.player1))

    return JsonResponse(data={
        'data': data,
        'date': date,
        'opponent': opponent,
    })
"""


def save_game(player1, player2, result):
    game = Game(player1=player1.username, player2=player2.username, result=result, player1ELO=player1.profile.currentELO, player2ELO=player2.profile.currentELO)
    game.save()

    player1.profile.currentELO, player2.profile.currentELO = game_ELO(player1.profile.currentELO, player2.profile.currentELO, result)
    if player1.profile.currentELO > player1.profile.highestELO:
        player1.profile.highestELO = player1.profile.currentELO

    if player2.profile.currentELO > player2.profile.highestELO:
        player2.profile.highestELO = player2.profile.currentELO

    if player1.profile.currentELO < player1.profile.lowestELO:
        player1.profile.lowestELO = player1.profile.currentELO

    if player2.profile.currentELO < player2.profile.lowestELO:
        player2.profile.lowestELO = player2.profile.currentELO

    player1.save()
    player2.save()

    return


def game_ELO(rating1, rating2, result):

    # Probabilities of winning
    prob_rating1 = 1/(1+10 ** ((rating2-rating1)/400))
    prob_rating2 = 1/(1+10 ** ((rating1-rating2)/400))

    # Adjusting ELO rantings
    rating1 += 32*(result - prob_rating1)
    rating2 += 32*(1 - result - prob_rating2)

    return rating1, rating2


def GameELOBlack(rating1, rating2, result):

    # Probabilities of winning
    prob_rating2 = 1/(1+10 ** ((rating1-rating2)/400))

    # Adjusting ELO rantings
    rating2 += 32*(1 - result - prob_rating2)

    return rating2


def GameELOWhite(rating1, rating2, result):
    # Probabilities of winning
    prob_rating1 = 1/(1+10 ** ((rating2-rating1)/400))

    # Adjusting ELO rantings
    rating1 += 32*(result - prob_rating1)

    return rating1


def username_present(username):
    if User.objects.filter(username=username).exists():
        return True

    return False

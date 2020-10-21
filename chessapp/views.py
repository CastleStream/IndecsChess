from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.utils import timezone
from .models import Game, Profile

def home(request):
    users = User.objects.all()
    if request.method == 'GET':
        return render(request, 'chessapp/home.html', {'users':users})
    elif not username_present(request.POST['player1']):
        return render(request, 'chessapp/home.html', {'users':users, 'error':'Can not find Player 1.'})

    elif not username_present(request.POST['player2']):
        return render(request, 'chessapp/home.html', {'users':users, 'error':'Can not find Player 2.'})

    else:
        """
        user1 = authenticate(request, username=request.POST['player1'])
        user2 = authenticate(request, username=request.POST['player2'])
        """
        user1 = User.objects.get(username=request.POST['player1'])
        user2 = User.objects.get(username=request.POST['player2'])

        save_game(user1, user2, 1)

        profiles = Profile.objects.all().order_by('-currentELO')[:10]
        return render(request, 'chessapp/ranking.html', {'profiles':profiles})



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
            return render(request, 'chessapp/createuser.html', {'error':'That nickname has already been taken'})

def ranking(request):
    # users = User.objects.all().order_by('profile.currentELO')
    profiles = Profile.objects.all().order_by('-currentELO')[:10]
    return render(request, 'chessapp/ranking.html', {'profiles':profiles})


def playersearch(request):
    if request.method == 'GET':
        return render(request, 'chessapp/playersearch.html')
    else:
        user = User.objects.get(username=request.POST['search'])
        return redirect('playerpage', user.id)



def playerpage(request, user_pk):
    user = get_object_or_404(User, pk=user_pk)
    if request.method == 'GET':
        return render(request, 'chessapp/playerpage.html', {'user':user})


def save_game(player1, player2, result):
    game = Game(player1=player1.username, player2=player2.username, result=result, player1ELO=player1.profile.currentELO, player2ELO=player2.profile.currentELO)
    game.save()

    player1.profile.currentELO, player2.profile.currentELO = game_ELO(player1.profile.currentELO, player2.profile.currentELO, 1)
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


def username_present(username):
    if User.objects.filter(username=username).exists():
        return True

    return False
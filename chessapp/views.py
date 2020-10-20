from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.utils import timezone
from .models import Game

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

        save_game(request.POST['player1'], request.POST['player2'], 1,
                  user1.profile.currentELO, user2.profile.currentELO)

        user1.profile.currentELO, user2.profile.currentELO = game_ELO(user1.profile.currentELO, user2.profile.currentELO, 1)
        user1.save()
        user2.save()


        return render(request, 'chessapp/ranking.html', {'users':users})



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
    return render(request, 'chessapp/ranking.html')


def playerpage(request):
    pass


def save_game(player1, player2, result, player1ELO, player2ELO):
    game = Game(player1=player1, player2=player2, result=result, player1ELO=player1ELO, player2ELO=player2ELO)
    game.save()
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

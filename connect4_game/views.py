from django.shortcuts import render
from django.http import HttpResponse
from .models import Game
from django.shortcuts import redirect
from uuid import UUID

def valid_username(username):
    if (len(username)<5) or (len(username)>29) or (not username.isalnum()):
        return False
    return True

def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.

    Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}

    Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.
    """
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
        return True
    except ValueError:
        return False

def validate_post_request(request):
    result = {}
    if ("user_name" not in request.POST) or not valid_username(request.POST['user_name']):
        result['status']  = False
        result['message'] = "Invalid alias, only alphanumeric characters are allowed and length of alias should be atleast 5"
        return result

    if ("game_type" not in request.POST) or (request.POST['game_type'] not in ['new', 'existing']):
        result['status']  = False
        result['message'] = "Invalid request"
        return result
    
    if request.POST['game_type'] == 'existing':
        if "game_id" not in request.POST or not is_valid_uuid(request.POST['game_id'], version=4):
            result['status']  = False
            result['message'] = "Invalid Game id provided"
            return result
        else:
            result['status']  = True
            return result
    
    # now checking only new game types
    if ("against" not in request.POST) or (request.POST['against'] not in ['computer', 'human']):
        result['status']  = False
        result['message'] = "Invalid request"
        return result
    
    result['status']  = True
    return result


def index(request):
    if request.method == "POST":
        validate_request = validate_post_request(request)
        if not validate_request['status']:
            if "username" in request.session:
                return render(request, "connect4_game/index.html", {
                'message': validate_request['message'],
                'username': request.session['username'],
            })
            else:
                return render(request, "connect4_game/index.html", {
                    'message': validate_request['message'],
                })
        
        request.session['username'] = request.POST['user_name']
        
        # generate game id and create a new game, or join existing game
        if request.POST['game_type'] == 'new':
            if request.POST['against'] == 'computer':
                new_game = Game.objects.create(
                    creator = request.session['username'],
                    game_state = "y" + str(len(request.session['username'])) + "#" + request.session['username'] + "000000000000000000000000000000000000000000f",
                    against_ai = True,
                    opponent_name = "ai",
                )
                game_id = new_game.game_id
            elif request.POST['against'] == 'human':
                new_game = Game.objects.create(
                    creator = request.session['username'],
                    game_state = "y" + str(len(request.session['username'])) + "#" + request.session['username'] + "000000000000000000000000000000000000000000f",
                    against_ai = False,
                )
                game_id = new_game.game_id
            return redirect('/game/' + game_id.urn[9:])
        else:
            game_id = request.POST['game_id']
            return redirect('/game/' + game_id)
    else:
        if "username" in request.session:
            return render(request, "connect4_game/index.html", {
                'username': request.session['username'],
            })
        else:
            return render(request, "connect4_game/index.html")        


# handling /game/:game-id route
def game(request, game_id):
    if "username" not in request.session:
        return redirect('/')
            
    try:
        curr_game = Game.objects.get(pk=game_id)
        return render(request, "connect4_game/game_page.html", {
            'username' : request.session['username'],
            'roomname': game_id,
        })
    except:
        return redirect('/')
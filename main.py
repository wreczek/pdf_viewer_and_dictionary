from app.app_factory import create_app, login_manager
from app.models import User

app = create_app()


@login_manager.user_loader
def load_user(user_id):
    print(f'Loading user with ID: {user_id}')
    return User.query.get(int(user_id))


if __name__ == "__main__":
    app.run(debug=True)

#  TODO:
#   1. details button - dodac funkcjonalnosc z planu
#   2. być może apply filter nie powinien odświeżać całej strony tylko samą tabelkę?
#   3. ogarnac zmiany z 3 commitami wstecz (slim vs no slim, czemu nie dziala, co powinno dzialac)
#       commit 47e...
#   4. Dodac Word model, ORM i usuwanie dodawanie etc. przez ten model
#   5. Add list_words endpoint with pagination
#   6. Usuwanie plikow z listy Files (i moze jakies inne manipulacje?) np. archive

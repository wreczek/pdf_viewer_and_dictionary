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
#   6. posprzatac nazewnictwo endpointow i sciezek (uploaded_list, pdf_viewer, ... etc)
#   otworzyc file_manager.py vs temp_file_manager.py i przepisac stare rzeczy do nowego podejscia
#   7. uploadowanie plikow: aktualnie upload pliku z ta sama nazwa zamienia pliki + nie zmienia daty uploadu
#   8. zapisywanie stanu PDFa na host=0.0.0.0 dla wszystkich ten sam (nawet chyba jesli ktos mial usera)
#   9. dodac jakies pipeliny/CI/CD:
#       a) docker-compose.yml
#       b) testy
#       c) githyb.yml?

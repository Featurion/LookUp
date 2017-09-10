from src.gui import app


ui = app.Interface(
    '127.0.0.1', 1492,
    hmac_key = b'614b4d734f78785a4131733075737832745a456f5a41',
    challenge_key = b'76b8e2753d9ffc4b93111063d296a8729a3829caaeb3')
ui.start()

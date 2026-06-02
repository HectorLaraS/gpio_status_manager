from src.web.app import app

app.secret_key = "CHANGE_ME_LATER"


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5050,
        debug=True,
    )

    app.secret_key = "CHANGE_ME_LATER"
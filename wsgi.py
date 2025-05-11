from app import create_app

application = create_app()
# test
if __name__ == "__main__":
    application.run()
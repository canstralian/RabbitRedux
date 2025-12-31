from app import create_app

# Create the app instance
# TODO: Add WSGI server configuration (workers, threads, timeouts)
# TODO: Implement graceful shutdown handling
# TODO: Add production logging configuration
app = create_app()

if __name__ == "__main__":
    app.run()
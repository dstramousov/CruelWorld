from src.core.app import main


# Application entry point. Keep all startup logic inside src.core.app.main()
# so tests and tools can import the package without opening a window.
if __name__ == "__main__":
    raise SystemExit(main())

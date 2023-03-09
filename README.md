### Building the game
```
pyinstaller --onedir --add-data 'c:\users\user\appdata\local\programs\python\python37\lib\site-packages\customtkinter;customtkinter' --add-data '.\resources;resources' --noconsole .\run_client.py
```
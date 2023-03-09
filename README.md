### Building the game
```
pyinstaller --onedir --add-data 'c:\users\admin\appdata\local\programs\python\python37\lib\site-packages\customtkinter;customtkinter' --add-data '.\resources;resources' --noconsole -n weerwolven .\run_client.py
```
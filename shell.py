import koala

while True:
    text = input('koala >> ')
    result, error = koala.run('shell.py', text)

    if (error):
        print(error.as_string())
    else:
        print(result)

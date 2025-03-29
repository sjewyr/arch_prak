FROM python

COPY . .

ENTRYPOINT [ "poetry", "run", "main.py" ]


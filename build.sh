    #!/bin/bash
    python3 -m pip install -r requirements.txt
    python3.9 manage.py collectstatic --no-input --clear

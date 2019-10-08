# Dev
mklink /D "node_modules" "D:\PROJEKTI\COMMON\npm\node_modules"


# App
py -3.6 -m pip install -U pip
py -3.6 -m venv env
python -m pip install -U pip

pip install -r requirements.txt
pip install -U -r requirements.txt

# Database


## Schema migration
Only "upgrade" command should be used in production

This is how to initiate with multidb set-up:
Run/db_migrate.bat

```flask db init --multidb```

Then:

```flask db migrate```

## Data migration

Modify the generated migration script with: op.execute()
https://alembic.sqlalchemy.org/en/latest/ops.html#alembic.operations.Operations.execute

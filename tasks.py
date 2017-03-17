import os

from invoke import task


def success(string):
    return '\033[92m' + string + '\033[0m'


def prefix_venv(cmd):
    """
    Prefixes the cmd with the virtualenv's bin/ folder if the cmd is found there
    """
    if os.environ.get('USE_VENV') == 'true':
        venv_cmd = os.path.join(VENV, 'bin', cmd)
        if os.path.exists(venv_cmd):
            return venv_cmd
    return cmd

# Default ENV variables
os.environ.setdefault('PIP', 'pip')
os.environ.setdefault('PYTHON', 'python')
os.environ.setdefault('PYTHON_VERSION', '3')
os.environ.setdefault('HIDE', 'out')                # Hides stdout by default
os.environ.setdefault('INVOKE_SHELL', '/bin/sh')    # Replace default shell, i.e. /bin/ash for alpine
os.environ.setdefault('USE_VENV', 'true')           # Execute commands from virtualenv if true

ENV_PRODUCTION = 'production'
ENV_DOCKER = 'docker'
ENV_DEV = 'dev'
ENV_TEST = 'test'
ENV_DEFAULT = ENV_PRODUCTION

DIR = os.path.dirname(os.path.realpath(__file__))
VENV = os.path.join(DIR, 'env')
MANAGE = os.path.join(DIR, 'manage.py')


def python(ctx, args, **kwargs):
    """
    Uses python from virtualenv if available, falls back to ENV variable PYTHON
    """
    ctx.run('{python} {args}'.format(python=prefix_venv(os.environ.get('PYTHON')), args=args),
            shell=os.environ.get('INVOKE_SHELL'), **kwargs)


def pip(ctx, args, **kwargs):
    """
    Uses pip from virtualenv if available, falls back to ENV variable PIP
    """
    ctx.run('{pip} {args}'.format(pip=prefix_venv(os.environ.get('PIP')), args=args),
            shell=os.environ.get('INVOKE_SHELL'), **kwargs)


def manage(ctx, args, **kwargs):
    python(ctx, '{manage} {args}'.format(manage=MANAGE, args=args), **kwargs)


@task
def clean(ctx):
    """
    Removes generate directories and compiled files
    """
    print(success('Cleaning cached files...'))
    ctx.run('find %s | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf' % DIR, shell=os.environ.get('INVOKE_SHELL'))


@task
def virtualenv(ctx):
    """
    Creates a virtualenv with the provided Python version, falls back to python3
    :param ctx:
    """
    if os.environ.get('USE_VENV') == 'true':
        print(success('Creating virtualenv...'))
        ctx.run('virtualenv -p python{version} env'.format(version=os.environ.get('PYTHON_VERSION')),
                hide=os.environ.get('HIDE'),
                shell=os.environ.get('INVOKE_SHELL'))


@task
def requirements(ctx, env=ENV_DEFAULT, **kwargs):
    """
    Installs requirements, optionally with devel requirements
    :param ctx:
    :param env:
    """
    if env == ENV_PRODUCTION:
        print(success('Installing requirements...'))
        pip(ctx, 'install -r requirements.txt', **kwargs)
    else:
        print(success('Installing development requirements...'))
        pip(ctx, 'install -r requirements-devel.txt', **kwargs)


@task
def setup(ctx, env=ENV_DEFAULT):
    """
    Runs all setup tasks (no management commands)
    :param ctx:
    :param env:
    """
    if env == ENV_DEV and not os.path.isdir(VENV):
        virtualenv(ctx)
    requirements(ctx, env=env, hide=os.environ.get('HIDE'))


@task
def db_recreate(ctx):
    """
    Drops and recreates the database
    """
    print(success('Recreating the database...'))
    manage(ctx, 'recreate_database', hide=os.environ.get('HIDE'))


@task
def db_migrate(ctx):
    """
    Runs database migrations
    """
    print(success('Running database migrations...'))
    manage(ctx, 'migrate --noinput', hide=os.environ.get('HIDE'))


@task
def db_fixtures(ctx, verify_users=True, initial_revisions=True):
    """
    Loads fixtures (test data) into the database

    :param ctx:
    :param verify_users:
    :param initial_revisions:
    """
    fixtures = [
        'apps/core/fixtures/initial_data.json',
        'apps/user/fixtures/auth_data.json',
    ]
    print(success('Loading fixtures...'))
    manage(ctx, 'loaddata {fixtures}'.format(fixtures=' '.join(fixtures)), hide=os.environ.get('HIDE'))

    if verify_users:
        # Verify user emails, so no email confirmations are necessary on sign-in
        print(success('Verifying users...'))
        manage(ctx, 'verify_users', hide=os.environ.get('HIDE'))


@task
def db(ctx, recreate=False, fixtures=False, wait=False):
    """
    Runs all database tasks
    :param ctx:
    :param recreate:
    :param fixtures:
    """
    if wait:
        print(success('Waiting for database connection...'))
        manage(ctx, 'wait_for_database', hide=os.environ.get('HIDE'))

    if recreate:
        db_recreate(ctx)

    db_migrate(ctx)

    if fixtures:
        db_fixtures(ctx)


@task
def static(ctx):
    """
    Collect static files
    """
    print(success('Collecting static files...'))
    manage(ctx, 'collectstatic --noinput', hide=os.environ.get('HIDE'))


@task
def test(ctx):
    """
    Runs tests
    """
    print(success('Running tests...'))
    ctx.run(prefix_venv('pytest'), shell=os.environ.get('INVOKE_SHELL'))


@task(default=True)
def main(ctx, env=ENV_DEFAULT):
    """
    Does a full build for a python version and environment
    :param ctx:
    :param env:
    """
    setup(ctx, env=env)
    db(ctx, recreate=(env == ENV_DEV), fixtures=(env == ENV_DEV))

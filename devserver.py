"""Only local development. Production uses Gunicorn and explicit secrets."""
import os,secrets,subprocess,sys
if os.getenv('PRODUCTION')=='1': raise SystemExit('Use Gunicorn em produção.')
os.environ.setdefault('SECRET_KEY',secrets.token_urlsafe(64))
os.environ['DEBUG']='1'
os.environ.setdefault('ALLOWED_HOSTS','localhost,127.0.0.1')
subprocess.run([sys.executable,'manage.py','migrate','--noinput'],check=True)
subprocess.run([sys.executable,'manage.py','setup_roles'],check=True)
subprocess.run([sys.executable,'manage.py','seed_demo'],check=True)
port = sys.argv[sys.argv.index('--port')+1] if '--port' in sys.argv else os.getenv('PORT','8000')
subprocess.run([sys.executable,'manage.py','runserver','0.0.0.0:'+port,'--noreload'],check=True)

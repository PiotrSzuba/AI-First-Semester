Fill those lines with your Reddit credentials in docker-compose.yml

CLIENT_ID:

CLIENT_SECRET:

REDDIT_USERNAME:

PASSWORD:

in grafana section set this to whatever password you want

GF_SECURITY_ADMIN_PASSWORD:

then to tun it:

docker-compose build

docker-compose up

and go to http://localhost:8501/ for streamlit\
http://localhost:3000/ for grafana stats

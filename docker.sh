docker build -t app_cars .
docker ps --filter "publish=8888" -q | xargs -r docker stop \
 && docker ps -a --filter "publish=8888" -q | xargs -r docker rm
docker run -v ~/.aws:/root/.aws:ro -e AWS_PROFILE=charles-perso -p 8888:80 app_cars
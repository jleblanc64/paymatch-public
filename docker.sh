docker build -t app_cars .

# optional: kill previously started app
docker ps --filter "publish=8888" -q | xargs -r docker stop \
 && docker ps -a --filter "publish=8888" -q | xargs -r docker rm

docker run -p 8888:80 app_cars
FROM nginx:1.27-alpine

# The public water site is the static React bundle, not the repository's
# separate Streamlit analysis tool.
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY water-web/ /usr/share/nginx/html/

EXPOSE 80

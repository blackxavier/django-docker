FROM nginxinc/nginx-unprivileged

# RUN useradd -r -s /sbin/nologin nginx

COPY nginx.conf /etc/nginx/conf.d/

RUN chown -R nginx:nginx /etc/nginx/conf.d 

USER nginx
EXPOSE 80  
CMD ["nginx", "-g", "daemon off;"]



# # create directory for the app user
# RUN mkdir -p /home/app

# # create the app user
# RUN addgroup --system app && adduser --system --group app

# RUN rm /etc/nginx/conf.d/default.conf
# COPY nginx.conf /etc/nginx/conf.d
# # change to the app user
# USER app
FROM python:3.9-slim
ENV PYTHONUNBUFFERED True


WORKDIR "/serving_diffusion_ui"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./
RUN ls -ll

ARG port
ARG aip_endpoint_name


ENV SERVER_PORT=$port
ENV AIP_ENDPOINT_NAME=$aip_endpoint_name

EXPOSE $SERVER_PORT

CMD python ./webui_playground.py --port $SERVER_PORT --aip-endpoint-name $AIP_ENDPOINT_NAME
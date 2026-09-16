ARG SUMO_IMAGE=ghcr.io/eclipse-sumo/sumo:v1_26_0
FROM ${SUMO_IMAGE}

ENV PYTHONUNBUFFERED=1
# The SUMO tools directory carries sumolib, which the converter uses to locate
# netconvert. Keep it on the path alongside the converter itself.
ENV PYTHONPATH=/opt/ll2sumo:/usr/share/sumo/tools
ENV SUMO_HOME=/usr/share/sumo
# The official SUMO v1_26_0 image stores Arrow/Parquet runtime libraries here.
ENV LD_LIBRARY_PATH=/usr/local/lib/python3.10/dist-packages/pyarrow

WORKDIR /workspace

COPY ll2sumo /opt/ll2sumo/ll2sumo

ENTRYPOINT ["python3", "-m", "ll2sumo.convert"]

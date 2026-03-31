FROM ghcr.io/actions/actions-runner:latest

USER root

RUN apt-get update && \
    apt-get install -y \
        openjdk-21-jdk \
        maven \
        python3 \
        python3-venv \
        python3-pip && \
    apt-get clean

ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-arm64
ENV MAVEN_HOME=/usr/share/maven
ENV PATH=$JAVA_HOME/bin:$MAVEN_HOME/bin:/usr/bin:$PATH

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER runner

ENTRYPOINT ["/entrypoint.sh"]


{%- if cookiecutter.include_fuzzing == "yes" -%}
# ClusterFuzzLite Build Container
# This Dockerfile builds the fuzz targets for ClusterFuzzLite
#
# Reference: https://google.github.io/clusterfuzzlite/build-integration/python/

FROM gcr.io/oss-fuzz-base/base-builder-python:v1

# Copy project source
COPY . $SRC/{{ cookiecutter.project_slug }}
WORKDIR $SRC/{{ cookiecutter.project_slug }}

# Install dependencies for fuzzing
RUN pip3 install --upgrade pip && \
    pip3 install atheris && \
    pip3 install -e .

# Copy build script
COPY .clusterfuzzlite/build.sh $SRC/
{%- endif %}

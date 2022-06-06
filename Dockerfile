FROM jupyter/scipy-notebook

RUN set -ex \
   && sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen \
   && sed -i 's/^# ru_RU.UTF-8 UTF-8$/ru_RU.UTF-8 UTF-8/g' /etc/locale.gen \
   && locale-gen en_US.UTF-8 ru_RU.UTF-8 \
   && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# install Python packages you often use
RUN set -ex \
   && conda install --quiet --yes \
   # choose the Python packages you need
   'plotly==4.9.0' \
   'folium==0.11.0' \
   && conda clean --all -f -y \
   # install Jupyter Lab extensions you need
   && jupyter labextension install jupyterlab-plotly@4.9.0 --no-build \
   && jupyter lab build -y \
   && jupyter lab clean -y \
   && rm -rf "/home/${NB_USER}/.cache/yarn" \
   && rm -rf "/home/${NB_USER}/.node-gyp" \
   && fix-permissions "${CONDA_DIR}" \
   && fix-permissions "/home/${NB_USER}"
FROM continuumio/miniconda3

RUN pip install pandas
RUN pip install sqlalchemy
RUN pip install beautifulsoup4
RUN pip install numpy
RUN pip install bokeh
RUN conda install jupyter
RUN pip install tabulate

EXPOSE 8888

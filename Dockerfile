FROM continuumio/miniconda3

RUN useradd -ms /bin/bash telegram_bot_user

RUN mkdir /tele_meds_bot && chown -R telegram_bot_user /tele_meds_bot /opt/conda
USER telegram_bot_user

COPY ./ /tele_meds_bot
WORKDIR /tele_meds_bot

RUN conda env update -n base -f environment.yml && \
  rm -rf /opt/conda/pkgs

CMD ["python", "timer_bot.py"]
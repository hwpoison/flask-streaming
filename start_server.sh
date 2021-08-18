#!/bin/bash
echo Starting project!
export FLASK_APP=fkstreaming
export FLASK_ENV=development
flask run --host=0.0.0.0

#!/bin/bash
source .venv/bin/activate

command="$1"
option="$2"
cpus=$(nproc)

if [ "$command" == "help" ]; then
    echo "Usage: $0 [command] [option]"
    echo "Commands:"
    echo "  help                Show this help message"
    echo "  dev                 Start the FastAPI development server"
    echo "  prod                Start the FastAPI production server"
    echo "  script [name]       Run a specific script (e.g., seed)"

elif [ "$command" == "dev" ]; then
    fastapi dev app.py

elif [ "$command" == "prod" ]; then
    fastapi run app.py

elif [ "$command" == "superprod" ]; then
    gunicorn -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 app:app

elif [ "$command" == "script" ]; then
    if [ -z "$option" ]; then
        echo "Please specify a script to run (e.g., seed)"
        exit 1
    fi

    python -m scripts.$option

else
    echo "Unknown command: $command"
    echo "Use '$0 help' for usage information."
    exit 1

fi
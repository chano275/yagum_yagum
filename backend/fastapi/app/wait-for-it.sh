#!/usr/bin/env bash
#   wait-for-it.sh
#   Use this script to test if a given TCP host/port are available
#   in the environment you are executing this script.
#
#   https://github.com/vishnubob/wait-for-it
#
#   Licensed under the MIT License
#

set -e

TIMEOUT=15
QUIET=0

echoerr() { if [ "$QUIET" -ne 1 ]; then echo "$@" 1>&2; fi; }

usage() {
    cat << USAGE >&2
Usage:
    $0 host:port [-s] [-t timeout] [-- command [args]]
    -h HOST | --host=HOST       Host or IP under test
    -p PORT | --port=PORT       TCP port under test
    -s | --strict               Only execute subcommand if the test succeeds
    -q | --quiet                Don't output any status messages
    -t TIMEOUT | --timeout=TIMEOUT
                                Timeout in seconds, zero for no timeout
    -- COMMAND [ARGS]           Execute command with args after the test finishes
USAGE
    exit 1
}

wait_for() {
    if [ "$TIMEOUT" -gt 0 ]; then
        echoerr "Waiting for $HOST:$PORT for up to $TIMEOUT seconds..."
    else
        echoerr "Waiting for $HOST:$PORT without a timeout..."
    fi
    start_ts=$(date +%s)
    while :
    do
        if [ "$(nc -z "$HOST" "$PORT" 2>/dev/null; echo $?)" -eq 0 ]; then
            end_ts=$(date +%s)
            echoerr "$HOST:$PORT is available after $((end_ts - start_ts)) seconds."
            break
        fi
        sleep 1
        if [ "$TIMEOUT" -gt 0 ] && [ $(( $(date +%s) - start_ts )) -ge "$TIMEOUT" ]; then
            echoerr "Operation timed out after ${TIMEOUT} seconds"
            exit 1
        fi
    done
}

# 인자 처리
if [ $# -eq 0 ]; then
    usage
fi

while [ $# -gt 0 ]
do
    case "$1" in
        *:* )
        HOST=$(echo "$1" | cut -d: -f1)
        PORT=$(echo "$1" | cut -d: -f2)
        shift 1
        ;;
        -h)
        HOST="$2"
        shift 2
        ;;
        --host=*)
        HOST="${1#*=}"
        shift 1
        ;;
        -p)
        PORT="$2"
        shift 2
        ;;
        --port=*)
        PORT="${1#*=}"
        shift 1
        ;;
        -t)
        TIMEOUT="$2"
        shift 2
        ;;
        --timeout=*)
        TIMEOUT="${1#*=}"
        shift 1
        ;;
        -q|--quiet)
        QUIET=1
        shift 1
        ;;
        -s|--strict)
        STRICT=1
        shift 1
        ;;
        --)
        shift
        break
        ;;
        *)
        echoerr "Unknown argument: $1"
        usage
        ;;
    esac
done

if [ -z "$HOST" ] || [ -z "$PORT" ]; then
    echoerr "Error: you need to provide a host and port to test."
    usage
fi

wait_for

if [ "$STRICT" = "1" ] && [ "$#" -gt 0 ]; then
    exec "$@"
elif [ "$#" -gt 0 ]; then
    "$@"
fi
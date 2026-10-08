import hashlib
import hmac
import json
from datetime import timezone as dt_timezone
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from .models import IntegridadeLog

GENESIS_HASH = '0' * 64

def canon_payload(timestamp, event, data_json, previous_hash):
    payload = {
            'timestamp': timestamp.astimezone(dt_timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'event': event,
            'data': data_json,
            'previous_hash': previous_hash,
            }
    return json.dumps(
            payload,
            sort_keys = True,
            ensure_ascii = False,
            separators = (',', ':')
            )

def calculate_hash(timestamp, event, data_json, previous_hash):
    msg = canon_payload(timestamp, event, data_json, previous_hash).encode('utf-8')

    return hmac.new(
            settings.LOG_INTEGRITY_KEY.encode('utf-8'),
            msg,
            hashlib.sha256
            ).hexdigest()

def event_register(event, data):
    canon_data = json.dumps(
            data,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":")
            )
    ts = timezone.now()

    with transaction.atomic():

        last = (
                IntegridadeLog.objects
                .select_for_update()
                .order_by("-id")
                .first()
                )

        previous_hash = (
                last.actual_hash
                if last
                else GENESIS_HASH
                )

        new_hash = calculate_hash(
                ts,
                event,
                canon_data,
                previous_hash
                )

        register = IntegridadeLog.objects.create(
                timestamp=ts,
                event=event,
                data=canon_data,
                previous_hash=previous_hash,
                actual_hash=new_hash
                )
    return register
